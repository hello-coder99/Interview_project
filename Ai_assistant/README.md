# Zoya AI Assistant

Zoya is a Flask-served, browser-native voice-to-voice assistant using the Gemini Live API with audio input and audio output only.

## Run

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key:

   ```bash
   set GEMINI_API_KEY=your_key_here
   ```

3. Start Flask:

   ```bash
   flask --app app run
   ```

4. Open `http://127.0.0.1:5000`.

The browser client imports `@google/genai` as an ES module and streams PCM16 microphone audio at 16 kHz to Gemini Live. Responses are decoded and played as 24 kHz PCM through the Web Audio API.

For production, do not expose a long-lived API key to the browser. Use an ephemeral token or a server-side Live API bridge.
