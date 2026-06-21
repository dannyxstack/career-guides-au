import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import {Scene, VideoProps} from "../schema";

// 通用旁白卡片：用于 summary / ratings / visa / growth / cta 等场景的占位布局
// （后续可像 SalaryScene 一样为每种 id 做专门的数据动画）
export const GenericScene: React.FC<{scene: Scene; props: VideoProps}> = ({scene, props}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 18], [0, 1], {extrapolateRight: "clamp"});

  return (
    <AbsoluteFill style={{padding: 90, justifyContent: "center", opacity}}>
      <div
        style={{
          fontSize: 30, letterSpacing: 4, color: props.theme.primary, marginBottom: 24,
        }}
      >
        {scene.name}
      </div>
      <div style={{fontSize: 52, fontWeight: 700, color: "#fff", lineHeight: 1.4}}>
        {scene.narration}
      </div>
      {scene.broll ? (
        <div style={{marginTop: 40, fontSize: 26, color: "#56617c"}}>🎞 {scene.broll}</div>
      ) : null}
    </AbsoluteFill>
  );
};
