import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {loadFont as loadGrotesk} from '@remotion/google-fonts/SpaceGrotesk';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';
import {theme} from '../theme';
import {cues, CueWindow} from './cues';
import type {FolgersRevealProps} from './schema';
import {SlamCallout} from './NumberCallout';
import {EvidenceFrame} from './EvidenceFrame';
import {RocketsFeathers} from './RocketsFeathers';
import {CutawayPanel} from './Cutaway';
import {EndCard} from './EndCard';
import {Watermark} from './Watermark';
import {PeakFallAnnotation} from './ChartAnnotation';
import {
  CaughtTitle,
  CiteCard,
  ShrinkOverlay,
  SourceHeader,
  StatCard,
  ThoughtBubble,
} from './Overlays';
import {punchScale} from './punches';
import {SfxTrack} from './Sfx';

loadGrotesk();
loadMono();

const MONO = '"JetBrains Mono", monospace';

// sfxFiles is injected by calculateMetadata (probes which slots exist).
export type MainProps = FolgersRevealProps & {sfxFiles: string[]};

const CueSequence: React.FC<{
  window: CueWindow;
  fps: number;
  name: string;
  children: React.ReactNode;
}> = ({window, fps, name, children}) => (
  <Sequence
    name={name}
    from={Math.round(window.start * fps)}
    durationInFrames={Math.round((window.end - window.start) * fps)}
  >
    {children}
  </Sequence>
);

// Framed screen recording (same visual language as EvidenceFrame).
const RecordingFrame: React.FC<{
  src: string | null;
  sourceLabel: string;
  placeholder: string;
  top?: number;
  height?: number;
  inset?: number;
  rotate?: number;
}> = ({src, sourceLabel, placeholder, top = 360, height = 560, inset = 40, rotate = 1}) =>
  src ? (
    <div
      style={{
        position: 'absolute',
        top,
        left: inset,
        right: inset,
        height,
        borderRadius: 18,
        overflow: 'hidden',
        border: `3px solid ${theme.bgElevated}`,
        boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
        transform: `rotate(${rotate}deg)`,
      }}
    >
      <OffthreadVideo
        muted
        src={staticFile(src)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'top',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          padding: '12px 24px',
          background: 'rgba(10,11,13,0.92)',
          fontFamily: MONO,
          fontSize: 26,
          color: theme.textSecondary,
          display: 'flex',
          gap: 14,
        }}
      >
        <span style={{color: theme.green, fontWeight: 700}}>REAL</span>
        <span>{sourceLabel}</span>
      </div>
    </div>
  ) : (
    <EvidenceFrame
      src={null}
      sourceLabel={sourceLabel}
      placeholder={placeholder}
      top={top}
      height={height}
      inset={inset}
    />
  );

// Relative windows inside a cutaway panel reuse the same helper.
const Rel = CueSequence;

export const Main: React.FC<MainProps> = (props) => {
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  // Punch-in map (face shots only — cutaways cover the base while zoomed)
  const baseScale = punchScale(frame / fps);

  return (
    <AbsoluteFill style={{background: theme.bg}}>
      {/* Base layer: the Captions talking-head export. NO caption rendering
          here — the Captions app burns its own captions into the edit. */}
      {props.baseVideo ? (
        <OffthreadVideo
          src={staticFile(props.baseVideo)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${baseScale})`,
            transformOrigin: '50% 38%',
          }}
        />
      ) : (
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: MONO,
            fontSize: 36,
            color: theme.textTertiary,
            textAlign: 'center',
            lineHeight: 1.8,
          }}
        >
          drop the Captions export at
          <br />
          public/folgers/base.mp4
          <br />
          and set the baseVideo prop
        </AbsoluteFill>
      )}

      <Watermark />

      {/* Cold open — "Caught: Folgers" (the sonic-logo moment) */}
      <CueSequence window={cues.caughtTitle} fps={fps} name="caught: title">
        <CaughtTitle brand={props.brand} />
      </CueSequence>

      {/* Beat 1 — hook. With a press screenshot: full SourceFrame cutaway.
          Until it lands: the original slam over the talking head. */}
      <CueSequence window={cues.hookLowCallout} fps={fps} name="19-month low">
        {props.articleImage ? (
          <CutawayPanel
            kicker="THE NEWS"
            durSec={cues.hookLowCallout.end - cues.hookLowCallout.start}
          >
            <SourceHeader headline={props.articleHeadline} top={280} />
            <EvidenceFrame
              src={props.articleImage}
              sourceLabel={`${props.articleName} — ${props.articleUrl}`}
              placeholder={'drop press screenshot at\npublic/folgers/article.png'}
              top={560}
              height={620}
              inset={40}
              zoomTo={1.04}
              panX={0}
              panY={-1}
              rotate={0}
            />
            <CiteCard name={props.articleName} url={props.articleUrl} top={1280} />
          </CutawayPanel>
        ) : (
          <SlamCallout text={props.lowLabel} sub="coffee futures, this week" />
        )}
      </CueSequence>
      <CueSequence window={cues.excuseGone} fps={fps} name="excuse gone">
        <SlamCallout text="THE EXCUSE IS GONE" top={420} />
      </CueSequence>

      {/* Cutaway 1 — credibility: full-screen branded panel with the real
          fullcarts.org screen recordings */}
      <CueSequence window={cues.cutDb} fps={fps} name="CUT: database">
        <CutawayPanel
          kicker="THE DATABASE"
          durSec={cues.cutDb.end - cues.cutDb.start}
        >
          <Rel window={cues.dbOverview} fps={fps} name="fullcarts overview">
            <RecordingFrame
              src={props.dbOverviewRecording}
              sourceLabel="fullcarts.org — live database"
              placeholder={'drop screen recording at\npublic/folgers/fullcarts-overview.mov'}
              top={300}
            />
          </Rel>
          <Rel window={cues.dbFolgersPage} fps={fps} name="folgers page">
            <RecordingFrame
              src={props.dbFolgersRecording}
              sourceLabel="fullcarts.org — the Folgers record"
              placeholder={'drop screen recording at\npublic/folgers/folgers-page.mov'}
              top={300}
              rotate={-1}
            />
          </Rel>
          <Rel window={cues.dbStat} fps={fps} name="2228 stat">
            <StatCard
              label="Documented shrinks"
              value={props.dbCount}
              caption="size cuts logged — every one source-cited"
              top={1060}
            />
          </Rel>
        </CutawayPanel>
      </CueSequence>

      {/* Cutaway 2 — the reveal: delisted listing, current listing, the
          numbers. Frame heights match each screenshot's aspect at 994px
          inner width so the highlight rings map 1:1 onto the pixels. */}
      <CueSequence window={cues.cutReveal} fps={fps} name="CUT: the reveal">
        <CutawayPanel
          kicker="EXHIBIT — WALMART.COM"
          durSec={cues.cutReveal.end - cues.cutReveal.start}
        >
          <Rel window={cues.listingThen} fps={fps} name="51oz listing">
            <EvidenceFrame
              src={props.listingThenImage}
              sourceLabel={props.listingThenSource}
              placeholder={'drop delisted 51 oz listing at\npublic/folgers/listing-then.png'}
              top={280}
              height={562}
              inset={40}
              zoomTo={1}
              panX={0}
              panY={0}
              rotate={-1}
              ring={{x: 76, y: 15.5, rx: 23.5, ry: 12}}
            />
          </Rel>
          <Rel window={cues.listingNow} fps={fps} name="43.5oz walmart">
            <EvidenceFrame
              src={props.listingNowImage}
              sourceLabel={props.listingNowSource}
              placeholder={'drop current 43.5 oz listing at\npublic/folgers/listing-now.png'}
              top={340}
              height={436}
              inset={40}
              zoomTo={1.05}
              panX={-1}
              panY={-1}
              rotate={1}
              ring={{x: 60.2, y: 8.9, rx: 8.5, ry: 7.5}}
            />
          </Rel>
          {/* The signature data card carries the numbers (style board:
              ShrinkOverlay) — bars wipe on the VO, badge pops on "fifteen
              percent" */}
          <Rel window={cues.shrinkOverlay} fps={fps} name="shrink overlay">
            <ShrinkOverlay
              brand={props.brand}
              product={props.productName}
              sizeBefore={props.sizeBefore}
              sizeAfter={props.sizeAfter}
              unit={props.sizeUnit}
              sourceLine="walmart.com · Jun 2026"
              top={980}
              afterAtSec={cues.shrinkAfterSec}
              badgeAtSec={cues.shrinkBadgeSec}
            />
          </Rel>
        </CutawayPanel>
      </CueSequence>

      {/* Cutaway 3 — the market: real futures chart, dot on the all-time
          high, arrow drawn down to the current price */}
      <CueSequence window={cues.cutChart} fps={fps} name="CUT: the market">
        <CutawayPanel
          kicker="COFFEE FUTURES — 12 MO"
          durSec={cues.cutChart.end - cues.cutChart.start}
        >
          <EvidenceFrame
            src={props.priceChartImage}
            sourceLabel={props.priceChartSource}
            placeholder={'drop real futures chart at\npublic/folgers/price-chart.png'}
            top={300}
            height={522}
            inset={40}
            zoomTo={1}
            panX={0}
            panY={0}
            rotate={0}
          >
            <PeakFallAnnotation
              peak={{x: 40.0, y: 10.6}}
              fallTo={{x: 89, y: 80}}
              aspect={993 / 1913}
              dotAtSec={cues.peakDotSec}
              arrowAtSec={cues.fallArrowSec}
            />
          </EvidenceFrame>
          <Rel window={cues.peakCallout} fps={fps} name="peak callout">
            <SlamCallout text={props.peakLabel} top={920} />
          </Rel>
          <Rel window={cues.dropCallout} fps={fps} name="drop callout">
            <SlamCallout text={props.dropLabel} top={920} />
          </Rel>
          <CiteCard
            name="ICE Arabica (KC)"
            url="12-month futures chart · Jun 2026"
            top={1200}
          />
        </CutawayPanel>
      </CueSequence>

      {/* Cutaway 4 — the metaphor (typography + strokes, never reads as data) */}
      <CueSequence window={cues.cutRockets} fps={fps} name="CUT: rockets & feathers">
        <CutawayPanel
          kicker="THE PATTERN"
          durSec={cues.cutRockets.end - cues.cutRockets.start}
        >
          <RocketsFeathers />
        </CutawayPanel>
      </CueSequence>

      {/* Beat 6 — punchline (on the talking head) */}
      <CueSequence window={cues.permanentRaise} fps={fps} name="permanent raise">
        <SlamCallout text="A PERMANENT RAISE" sub="you paid for it" />
      </CueSequence>

      {/* The gag */}
      <CueSequence window={cues.dadBurp} fps={fps} name="dad burp">
        <ThoughtBubble
          text="dad burp incoming…"
          durSec={cues.dadBurp.end - cues.dadBurp.start}
        />
      </CueSequence>

      {/* Beat 7 — CTA */}
      <CueSequence window={cues.endCard} fps={fps} name="end card">
        <EndCard />
      </CueSequence>

      {/* SFX layer (slots in public/sfx/ — missing files are skipped) */}
      <SfxTrack available={props.sfxFiles} />
    </AbsoluteFill>
  );
};
