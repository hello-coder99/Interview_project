class PcmCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.frameCount = 0;
    this.chunkFrames = 2048;
  }

  process(inputs) {
    const input = inputs[0]?.[0];

    if (!input) {
      return true;
    }

    for (let index = 0; index < input.length; index += 1) {
      const clamped = Math.max(-1, Math.min(1, input[index]));
      this.buffer.push(clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff);
      this.frameCount += 1;
    }

    if (this.frameCount >= this.chunkFrames) {
      const pcm = new Int16Array(this.buffer.length);

      for (let index = 0; index < this.buffer.length; index += 1) {
        pcm[index] = this.buffer[index];
      }

      this.port.postMessage(pcm.buffer, [pcm.buffer]);
      this.buffer = [];
      this.frameCount = 0;
    }

    return true;
  }
}

registerProcessor("pcm-capture-processor", PcmCaptureProcessor);
