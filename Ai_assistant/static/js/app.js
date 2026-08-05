import { AudioStreamer } from "./audio-streamer.js";
import { LiveSession } from "./live-session.js";

const shell = document.querySelector(".shell");
const powerButton = document.querySelector("#powerButton");
const stateLabel = document.querySelector("#stateLabel");
const quip = document.querySelector("#quip");

const stateCopy = {
  disconnected: ["Disconnected", "Ready when you are, darling."],
  connecting: ["Connecting", "Putting on the lip gloss. One sec."],
  listening: ["Listening", "Go on. Impress me."],
  speaking: ["Speaking", "Relax, I've got this."],
};

let liveSession = null;
let audioStreamer = null;
let active = false;

function setState(state, message = null) {
  const [label, fallback] = stateCopy[state] || stateCopy.disconnected;
  shell.dataset.state = state;
  stateLabel.textContent = label;
  quip.textContent = message || fallback;
  powerButton.disabled = state === "connecting";
  powerButton.setAttribute("aria-label", active ? "Stop Zoya" : "Start Zoya");
}

async function getClientConfig() {
  const response = await fetch("/api/client-config", { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Could not load Gemini configuration");
  }

  return response.json();
}

async function startZoya() {
  active = true;
  setState("connecting");

  const config = await getClientConfig();

  if (!config.configured) {
    throw new Error("GEMINI_API_KEY is missing. Zoya is fabulous, not clairvoyant.");
  }

  audioStreamer = new AudioStreamer({
    onAudioChunk: (base64Pcm) => liveSession?.sendAudio(base64Pcm),
    onSpeakingStart: () => setState("speaking"),
    onSpeakingEnd: () => {
      if (active) {
        setState("listening");
      }
    },
  });

  liveSession = new LiveSession({
    apiKey: config.apiKey,
    model: config.model,
    onState: (state) => setState(state),
    onQuip: (message) => {
      quip.textContent = message;
    },
    onAudio: async ({ data, interrupted }) => {
      if (interrupted) {
        audioStreamer?.clearPlayback();
        return;
      }

      await audioStreamer?.playPcm16(data);
    },
    onError: (message) => {
      stopZoya();
      setState("disconnected", message || "Something got dramatic. Try again.");
    },
  });

  await audioStreamer.start();
  await liveSession.connect();
}

function stopZoya() {
  active = false;
  liveSession?.disconnect();
  liveSession = null;
  audioStreamer?.stop();
  audioStreamer = null;
  setState("disconnected");
}

powerButton.addEventListener("click", async () => {
  if (active) {
    stopZoya();
    return;
  }

  try {
    await startZoya();
  } catch (error) {
    active = false;
    await audioStreamer?.stop();
    audioStreamer = null;
    liveSession?.disconnect();
    liveSession = null;
    setState("disconnected", error.message);
  }
});

setState("disconnected");
