import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
} from 'remotion';
import {loadFont as loadGrotesk} from '@remotion/google-fonts/SpaceGrotesk';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';
import type {Caption} from '@remotion/captions';
import {theme} from '../theme';
import {cues, CueWindow} from './cues';
import type {FolgersRevealProps} from './schema';
import {Captions} from './Captions';
import {PercentCounter, SizeStrike, SlamCallout} from './NumberCallout';
import {EvidenceFrame} from './EvidenceFrame';
import {RocketsFeathers} from './RocketsFeathers';
import {EndCard} from './EndCard';
import {Watermark} from './Watermark';

loadGrotesk();
loadMono();

const MONO = '"JetBrains Mono", monospace';

// Injected by calculateMetadata in Root.tsx after parsing the SRT.
export type MainProps = FolgersRevealProps & {captions: Caption[]};

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

export const Main: React.FC<MainProps> = (props) => {
  const {fps} = useVideoConfig();
  const pctDrop =
    ((props.sizeAfter - props.sizeBefore) / props.sizeBefore) * 100;

  return (
    <AbsoluteFill style={{background: theme.bg}}>
      {/* Base layer: the Captions talking-head export. */}
      {props.baseVideo ? (
        <OffthreadVideo
          src={staticFile(props.baseVideo)}
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
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

      {/* Beat 1 — hook */}
      <CueSequence window={cues.hookLowCallout} fps={fps} name="19-month low">
        <SlamCallout text={props.lowLabel} sub="coffee futures, this week" />
      </CueSequence>
      <CueSequence window={cues.excuseGone} fps={fps} name="excuse gone">
        <SlamCallout text="THE EXCUSE IS GONE" top={420} />
      </CueSequence>

      {/* Beat 2 — credibility: real fullcarts.org screen recording */}
      <CueSequence window={cues.dbRecording} fps={fps} name="db recording">
        {props.dbRecording ? (
          <div
            style={{
              position: 'absolute',
              top: 260,
              left: 80,
              right: 80,
              height: 920,
              borderRadius: 18,
              overflow: 'hidden',
              border: `3px solid ${theme.bgElevated}`,
              boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
              transform: 'rotate(1deg)',
            }}
          >
            <OffthreadVideo
              muted
              src={staticFile(props.dbRecording)}
              style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top'}}
            />
          </div>
        ) : (
          <EvidenceFrame
            src={null}
            sourceLabel="fullcarts.org — live database"
            placeholder={'drop screen recording at\npublic/folgers/db-recording.mp4'}
          />
        )}
      </CueSequence>

      {/* Beat 3 — the reveal: archived listing, current listing, the numbers */}
      <CueSequence window={cues.listingThen} fps={fps} name="51oz listing">
        <EvidenceFrame
          src={props.listingThenImage}
          sourceLabel={props.listingThenSource}
          placeholder={'drop archived 51 oz listing at\npublic/folgers/listing-then.png'}
          ring={{x: 50, y: 42, r: 13}}
        />
      </CueSequence>
      <CueSequence window={cues.listingNow} fps={fps} name="43.5oz listing">
        <EvidenceFrame
          src={props.listingNowImage}
          sourceLabel={props.listingNowSource}
          placeholder={'drop current 43.5 oz listing at\npublic/folgers/listing-now.png'}
          rotate={1.5}
          ring={{x: 50, y: 42, r: 13}}
        />
      </CueSequence>
      <CueSequence window={cues.sizeStrike} fps={fps} name="51 -> 43.5">
        <SizeStrike
          before={props.sizeBefore}
          after={props.sizeAfter}
          unit={props.sizeUnit}
          top={1290}
        />
      </CueSequence>
      <CueSequence window={cues.pctCounter} fps={fps} name="-14.7%">
        <PercentCounter toPct={pctDrop} label="of your coffee — gone" top={1290} />
      </CueSequence>

      {/* Beat 4 — real futures chart */}
      <CueSequence window={cues.priceChart} fps={fps} name="price chart">
        <EvidenceFrame
          src={props.priceChartImage}
          sourceLabel={props.priceChartSource}
          placeholder={'drop real futures chart at\npublic/folgers/price-chart.png'}
          zoomTo={1.08}
          rotate={-1}
        />
      </CueSequence>
      <CueSequence window={cues.peakCallout} fps={fps} name="peak callout">
        <SlamCallout text={props.peakLabel} top={1300} />
      </CueSequence>
      <CueSequence window={cues.dropCallout} fps={fps} name="drop callout">
        <SlamCallout text={props.dropLabel} top={1300} />
      </CueSequence>

      {/* Beat 5 — metaphor (typography only, never reads as data) */}
      <CueSequence window={cues.rocketsFeathers} fps={fps} name="rockets & feathers">
        <RocketsFeathers />
      </CueSequence>

      {/* Beat 6 — punchline */}
      <CueSequence window={cues.permanentRaise} fps={fps} name="permanent raise">
        <SlamCallout text="A PERMANENT RAISE" sub="you paid for it" />
      </CueSequence>

      {/* Captions ride above overlays, below the end card. */}
      <Captions captions={props.captions} highlightWords={props.highlightWords} />

      {/* Beat 7 — CTA */}
      <CueSequence window={cues.endCard} fps={fps} name="end card">
        <EndCard />
      </CueSequence>
    </AbsoluteFill>
  );
};
