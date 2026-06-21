import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {Scene, VideoProps} from "../schema";

// 字幕叠加层：按当前帧时间（场景内相对时间）显示对应字幕段
export const Captions: React.FC<{scene: Scene; props: VideoProps}> = ({scene, props}) => {
  const frame = useCurrentFrame();
  const {fps, height} = useVideoConfig();
  const t = frame / fps;
  const caps = scene.captions ?? [];
  const active = caps.find((c) => t >= c.start && t < c.end);
  if (!active) return null;

  // 竖屏字幕略靠下，横屏更靠底部
  const isVertical = props.format.startsWith("short");
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: isVertical ? height * 0.18 : 90,
        paddingLeft: 60,
        paddingRight: 60,
      }}
    >
      <div
        style={{
          fontSize: isVertical ? 54 : 44,
          fontWeight: 800,
          color: "#fff",
          textAlign: "center",
          lineHeight: 1.3,
          background: "rgba(0,0,0,0.55)",
          padding: "12px 26px",
          borderRadius: 14,
          maxWidth: "92%",
          textShadow: "0 2px 8px rgba(0,0,0,0.6)",
        }}
      >
        {active.text}
      </div>
    </AbsoluteFill>
  );
};
