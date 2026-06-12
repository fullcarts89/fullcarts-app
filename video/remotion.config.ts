import { Config } from "@remotion/cli/config";

// PNG image format is required so alpha (transparency) is preserved when we
// render the lower-third overlays for compositing in Captions App / CapCut.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
