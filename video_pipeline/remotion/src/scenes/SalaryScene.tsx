import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Scene, VideoProps} from "../schema";

// 薪资动态条形图：按 max 归一化，逐条弹入并数字滚动
export const SalaryScene: React.FC<{scene: Scene; props: VideoProps}> = ({scene, props}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const salaries = props.occupation.salaries;
  const maxVal = Math.max(...salaries.map((s) => s.max ?? 0), 1);

  return (
    <AbsoluteFill style={{padding: 80, justifyContent: "center"}}>
      <div style={{fontSize: 56, fontWeight: 800, color: "#fff", marginBottom: 48}}>
        💰 薪资范围
      </div>

      {salaries.map((s, i) => {
        const delay = i * 8;
        const grow = spring({frame: frame - delay, fps, config: {damping: 16}});
        const widthPct = interpolate(grow, [0, 1], [0, ((s.max ?? 0) / maxVal) * 100]);
        const shown = Math.round(interpolate(grow, [0, 1], [0, s.max ?? 0]) / 1000);

        return (
          <div key={i} style={{marginBottom: 36}}>
            <div style={{display: "flex", justifyContent: "space-between", marginBottom: 10}}>
              <span style={{fontSize: 34, color: "#e6ebf5"}}>{s.label}</span>
              <span style={{fontSize: 34, color: props.theme.accent, fontWeight: 700}}>
                ${shown}k
              </span>
            </div>
            <div style={{height: 28, background: "#1c2740", borderRadius: 14}}>
              <div
                style={{
                  height: "100%", width: `${widthPct}%`, borderRadius: 14,
                  background: `linear-gradient(90deg, ${props.theme.primary}, ${props.theme.accent})`,
                }}
              />
            </div>
          </div>
        );
      })}

      <div style={{marginTop: 40, fontSize: 32, color: "#8b97b0", lineHeight: 1.5}}>
        {scene.narration}
      </div>
    </AbsoluteFill>
  );
};
