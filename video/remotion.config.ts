import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setConcurrency(null);
Config.setEntryPoint("src/index.ts");

// Locally, leave this unset — Remotion will download and cache its own
// chrome-headless-shell on first render. In sandboxed CI environments
// where that download is blocked, point REMOTION_BROWSER_EXECUTABLE at
// a pre-installed binary (e.g. Playwright's headless_shell at
// /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell).
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
