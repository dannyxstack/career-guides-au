import React from "react";
import {AbsoluteFill, Audio, Img, Series, staticFile, useVideoConfig} from "remotion";
import {Scene, VideoProps} from "../schema";
import {TitleScene} from "../scenes/TitleScene";
import {SalaryScene} from "../scenes/SalaryScene";
import {GenericScene} from "../scenes/GenericScene";
import {Captions} from "../scenes/Captions";

// 按场景 id 分派到对应布局组件；未知 id 走通用旁白卡片
const pickScene = (scene: Scene, props: VideoProps) => {
  switch (scene.id) {
    case "title":
      return <TitleScene scene={scene} props={props} />;
    case "salary":
      return <SalaryScene scene={scene} props={props} />;
    default:
      return <GenericScene scene={scene} props={props} />;
  }
};

export const VideoRoot: React.FC<VideoProps> = (props) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill
      style={{backgroundColor: props.theme.bg, fontFamily: props.theme.font}}
    >
      <Series>
        {props.scenes.map((scene, i) => (
          <Series.Sequence
            key={i}
            durationInFrames={Math.max(1, Math.ceil(scene.durationSec * fps))}
          >
            {scene.bgImage ? (
              <AbsoluteFill>
                <Img
                  src={staticFile(scene.bgImage)}
                  style={{width: "100%", height: "100%", objectFit: "cover"}}
                />
              </AbsoluteFill>
            ) : (
              pickScene(scene, props)
            )}
            <Captions scene={scene} props={props} />
            {scene.audioSrc ? <Audio src={staticFile(scene.audioSrc)} /> : null}
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
