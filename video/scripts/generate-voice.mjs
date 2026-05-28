#!/usr/bin/env node
/**
 * generate-voice.mjs
 *
 * Reads a ShrinkEvent .ts data file, extracts the `narration` string +
 * `narrationAudio` output path, calls ElevenLabs TTS, and writes the
 * mp3 to video/public/<narrationAudio>.
 *
 * Pre-render workflow (per the strategy doc: audio is cached, not
 * regenerated per render):
 *
 *   1. Edit the narration in src/data/<event>.ts
 *   2. Run: node scripts/generate-voice.mjs src/data/<event>.ts
 *   3. Commit the resulting mp3 alongside the event JSON
 *   4. npm run build → Remotion picks up the mp3 via staticFile()
 *
 * Requires ELEVENLABS_API_KEY in .env.local (gitignored).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, "..");

// Hand-rolled .env.local parser to avoid pulling in dotenv as a dep.
function loadEnvLocal() {
  const envPath = path.join(projectRoot, ".env.local");
  if (!fs.existsSync(envPath)) return;
  const lines = fs.readFileSync(envPath, "utf8").split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const value = trimmed.slice(eq + 1).trim().replace(/^["']|["']$/g, "");
    if (!process.env[key]) process.env[key] = value;
  }
}

// Crude extractor — pulls `narration: "..."` or `narration: [...].join(" ")`
// without spinning up a full TS compiler. Sufficient for our hand-authored
// event files; revisit if we move to JSON-driven events.
function extractNarrationFromTs(tsSource) {
  const arrayMatch = tsSource.match(
    /narration:\s*\[([\s\S]*?)\]\s*\.\s*join\(\s*["']([^"']*)["']\s*\)/,
  );
  if (arrayMatch) {
    const items = [...arrayMatch[1].matchAll(/["']((?:\\.|[^"'\\])*?)["']/g)]
      .map((m) => m[1].replace(/\\(.)/g, "$1"));
    return items.join(arrayMatch[2]);
  }
  const stringMatch = tsSource.match(
    /narration:\s*["']((?:\\.|[^"'\\])*?)["']/,
  );
  if (stringMatch) return stringMatch[1].replace(/\\(.)/g, "$1");
  return null;
}

function extractField(tsSource, field) {
  const m = tsSource.match(
    new RegExp(`${field}:\\s*["']((?:\\\\.|[^"'\\\\])*?)["']`),
  );
  return m ? m[1].replace(/\\(.)/g, "$1") : null;
}

async function main() {
  loadEnvLocal();

  const eventFile = process.argv[2];
  if (!eventFile) {
    console.error("Usage: node scripts/generate-voice.mjs <path/to/event.ts>");
    process.exit(1);
  }

  const apiKey = process.env.ELEVENLABS_API_KEY;
  const voiceId = process.env.ELEVENLABS_VOICE_ID || "pNInz6obpgDQGcFmaJgB";
  const modelId = process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2";

  if (!apiKey) {
    console.error("ELEVENLABS_API_KEY missing. Add it to video/.env.local.");
    process.exit(1);
  }

  const tsSource = fs.readFileSync(eventFile, "utf8");
  const narration = extractNarrationFromTs(tsSource);
  const outRelative = extractField(tsSource, "narrationAudio");

  if (!narration) {
    console.error(`No \`narration\` field found in ${eventFile}`);
    process.exit(1);
  }
  if (!outRelative) {
    console.error(`No \`narrationAudio\` field found in ${eventFile}`);
    process.exit(1);
  }

  const outPath = path.join(projectRoot, "public", outRelative);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  console.log(`> Voice: ${voiceId}  Model: ${modelId}`);
  console.log(`> Narration (${narration.length} chars): "${narration.slice(0, 80)}..."`);
  console.log(`> Output:    public/${outRelative}`);

  const res = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
    {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "content-type": "application/json",
        accept: "audio/mpeg",
      },
      body: JSON.stringify({
        text: narration,
        model_id: modelId,
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.3,
          use_speaker_boost: true,
        },
      }),
    },
  );

  if (!res.ok) {
    const errText = await res.text();
    console.error(`ElevenLabs API error ${res.status}: ${errText}`);
    process.exit(1);
  }

  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outPath, buf);
  console.log(`> Wrote ${(buf.length / 1024).toFixed(1)} KB to ${outPath}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
