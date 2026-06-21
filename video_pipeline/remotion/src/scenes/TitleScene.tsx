import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Scene, VideoProps} from "../schema";

export const TitleScene: React.FC<{scene: Scene; props: VideoProps}> = ({scene, props}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const occ = props.occupation;

  const enter = spring({frame, fps, config: {damping: 14}});
  const y = interpolate(enter, [0, 1], [60, 0]);
  const subOpacity = interpolate(frame, [10, 30], [0, 1], {extrapolateRight: "clamp"});

  return (
    <AbsoluteFill
      style={{justifyContent: "center", alignItems: "center", padding: 80, textAlign: "center"}}
    >
      <div
        style={{
          fontSize: 34, letterSpacing: 6, color: props.theme.primary,
          opacity: subOpacity, marginBottom: 24,
        }}
      >
        ANZSCO {occ.anzscoCode}
      </div>
      <div
        style={{
          fontSize: 96, fontWeight: 800, color: "#fff",
          transform: `translateY(${y}px)`, opacity: enter, lineHeight: 1.1,
        }}
      >
        {occ.nameZh}
      </div>
      <div style={{fontSize: 40, color: "#8b97b0", marginTop: 16, opacity: subOpacity}}>
        {occ.nameEn}
      </div>
      <div
        style={{
          marginTop: 48, fontSize: 38, color: "#e6ebf5", maxWidth: 820,
          opacity: subOpacity, lineHeight: 1.5,
        }}
      >
        {scene.narration}
      </div>
    </AbsoluteFill>
  );
};
