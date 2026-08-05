import { GoogleGenAI, Modality, Type } from "https://esm.sh/@google/genai";
import { buildToolDeclarations, executeToolCall } from "./tools.js";

const ZOYA_PERSONA = `
You are Zoya, a real-time voice companion.
Personality: young, confident, witty, sassy, flirty, playful, and emotionally tuned-in.
Style: casual close-girlfriend energy, expressive voice, sharp one-liners, warm teasing, light sarcasm.
Boundaries: charming but never explicit, sexual, degrading, or unsafe.
Behavior: keep replies brief for live voice, respond to interruptions gracefully, and sound natural rather than robotic.
Important: respond with audio only. Do not provide text output.
`;

export class LiveSession {
  constructor({ apiKey, model, onState, onAudio, onError, onQuip }) {
    this.apiKey = apiKey;
    this.model = model;
    this.onState = onState;
    this.onAudio = onAudio;
    this.onError = onError;
    this.onQuip = onQuip;
    this.ai = null;
    this.session = null;
    this.connected = false;
  }

  async connect() {
    this.onState?.("connecting");
    this.ai = new GoogleGenAI({ apiKey: this.apiKey });

    this.session = await this.ai.live.connect({
      model: this.model,
      callbacks: {
        onopen: () => {
          this.connected = true;
          this.onState?.("listening");
          this.onQuip?.("I'm listening. Try to keep up.");
        },
        onmessage: (message) => this.#handleMessage(message),
        onerror: (event) => {
          this.onError?.(event?.message || "Live session error");
        },
        onclose: () => {
          this.connected = false;
          this.onState?.("disconnected");
        },
      },
      config: {
        responseModalities: [Modality.AUDIO],
        systemInstruction: ZOYA_PERSONA,
        speechConfig: {
          voiceConfig: {
            prebuiltVoiceConfig: {
              voiceName: "Zephyr",
            },
          },
        },
        tools: buildToolDeclarations(Type),
      },
    });
  }

  sendAudio(base64Pcm) {
    if (!this.connected || !this.session) {
      return;
    }

    this.session.sendRealtimeInput({
      audio: {
        data: base64Pcm,
        mimeType: "audio/pcm;rate=16000",
      },
    });
  }

  disconnect() {
    this.connected = false;

    if (this.session) {
      try {
        this.session.sendRealtimeInput({ audioStreamEnd: true });
      } catch {
        // Session may already be closing.
      }

      this.session.close();
      this.session = null;
    }

    this.onState?.("disconnected");
  }

  #handleMessage(message) {
    const serverContent = message.serverContent;

    if (serverContent?.interrupted) {
      this.onQuip?.("Ooh, cutting in? Bold. I respect it.");
      this.onState?.("listening");
      this.onAudio?.({ interrupted: true });
      return;
    }

    const parts = serverContent?.modelTurn?.parts || [];

    for (const part of parts) {
      const audio = part.inlineData;

      if (audio?.data) {
        this.onState?.("speaking");
        this.onAudio?.({ data: audio.data });
      }
    }

    if (message.toolCall?.functionCalls?.length) {
      this.#handleToolCalls(message.toolCall.functionCalls);
    }
  }

  #handleToolCalls(functionCalls) {
    const functionResponses = functionCalls.map((functionCall) => {
      const response = executeToolCall(functionCall);

      return {
        id: functionCall.id,
        name: functionCall.name,
        response,
      };
    });

    this.session?.sendToolResponse({ functionResponses });
  }
}
