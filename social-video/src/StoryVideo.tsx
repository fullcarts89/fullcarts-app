import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';

export const StoryVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#161616', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{opacity, color: '#fff', fontSize: 90, fontFamily: 'sans-serif', fontWeight: 700}}>
        Same can. Same price.
      </div>
      <div style={{opacity, color: '#ff3b30', fontSize: 140, fontWeight: 800, marginTop: 20}}>
        −14.7%
      </div>
    </AbsoluteFill>
  );
};
