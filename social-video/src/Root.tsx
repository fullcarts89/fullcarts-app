import {Composition} from 'remotion';
import {StoryVideo} from './StoryVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Story"
      component={StoryVideo}
      durationInFrames={150}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
