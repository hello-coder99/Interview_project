import { arrayBufferToBase64, base64ToArrayBuffer } from "./utils.js";

export class AudioStreamer {
  constructor({ onAudioChunk, onSpeakingStart, onSpeakingEnd }) {
    this.onAudioChunk = onAudioChunk;
    this.onSpeakingStart = onSpeakingStart;
    this.onSpeakingEnd = onSpeakingEnd;

    this.captureContext = null;
    this.playbackContext = null;
    this.mediaStream = null;
    this.sourceNode = null;
    this.workletNode = null;
    this.silentSink = null;
    this.nextStartTime = 0;
    this.activeSources = new Set();
    this.endTimer = null;
  }

  async start() {
    await this.#ensurePlaybackContext();
    await this.#ensureCaptureContext();

    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      video: false,
    });

    this.sourceNode = this.captureContext.createMediaStreamSource(this.mediaStream);
    this.workletNode = new AudioWorkletNode(
      this.captureContext,
      "pcm-capture-processor",
      {
        numberOfInputs: 1,
        numberOfOutputs: 1,
        channelCount: 1,
      }
    );

    this.workletNode.port.onmessage = (event) => {
      this.onAudioChunk?.(arrayBufferToBase64(event.data));
    };

    this.silentSink = this.captureContext.createGain();
    this.silentSink.gain.value = 0;
    this.sourceNode.connect(this.workletNode);
    this.workletNode.connect(this.silentSink);
    this.silentSink.connect(this.captureContext.destination);
  }

  async stop() {
    this.clearPlayback();

    if (this.workletNode) {
      this.workletNode.disconnect();
      this.workletNode.port.onmessage = null;
      this.workletNode = null;
    }

    if (this.sourceNode) {
      this.sourceNode.disconnect();
      this.sourceNode = null;
    }

    if (this.silentSink) {
      this.silentSink.disconnect();
      this.silentSink = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    if (this.captureContext) {
      await this.captureContext.close();
      this.captureContext = null;
    }
  }

  async playPcm16(base64Audio) {
    await this.#ensurePlaybackContext();

    const pcm = new Int16Array(base64ToArrayBuffer(base64Audio));
    const audioBuffer = this.playbackContext.createBuffer(1, pcm.length, 24000);
    const channel = audioBuffer.getChannelData(0);

    for (let index = 0; index < pcm.length; index += 1) {
      channel[index] = Math.max(-1, Math.min(1, pcm[index] / 0x8000));
    }

    const source = this.playbackContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.playbackContext.destination);

    const startAt = Math.max(this.playbackContext.currentTime + 0.04, this.nextStartTime);
    this.nextStartTime = startAt + audioBuffer.duration;

    this.onSpeakingStart?.();
    window.clearTimeout(this.endTimer);

    source.onended = () => {
      this.activeSources.delete(source);
      const remainingMs = Math.max(0, (this.nextStartTime - this.playbackContext.currentTime) * 1000);

      window.clearTimeout(this.endTimer);
      this.endTimer = window.setTimeout(() => {
        if (this.activeSources.size === 0) {
          this.onSpeakingEnd?.();
        }
      }, remainingMs + 60);
    };

    this.activeSources.add(source);
    source.start(startAt);
  }

  clearPlayback() {
    window.clearTimeout(this.endTimer);

    for (const source of this.activeSources) {
      try {
        source.stop();
      } catch {
        // Already stopped.
      }
    }

    this.activeSources.clear();

    if (this.playbackContext) {
      this.nextStartTime = this.playbackContext.currentTime;
    }

    this.onSpeakingEnd?.();
  }

  async #ensureCaptureContext() {
    if (this.captureContext) {
      await this.captureContext.resume();
      return;
    }

    this.captureContext = new AudioContext({ sampleRate: 16000 });
    await this.captureContext.audioWorklet.addModule("/static/js/pcm-worklet.js");
  }

  async #ensurePlaybackContext() {
    if (!this.playbackContext) {
      this.playbackContext = new AudioContext({ sampleRate: 24000 });
      this.nextStartTime = this.playbackContext.currentTime;
    }

    await this.playbackContext.resume();
  }
}
