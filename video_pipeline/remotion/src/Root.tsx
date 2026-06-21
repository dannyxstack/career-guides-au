import React from "react";
import {Composition} from "remotion";
import {VideoRoot} from "./compositions/VideoRoot";
import {propsSchema, VideoProps} from "./schema";
import {mockProps} from "./lib/mock";

const FPS = 30;

// 视频总时长 = 各场景时长之和（由 inputProps 动态决定）
const calc = ({props}: {props: VideoProps}) => {
  const total = props.scenes.reduce((a, s) => a + s.durationSec, 0);
  return {durationInFrames: Math.max(1, Math.ceil(total * FPS))};
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Short"
        component={VideoRoot}
        schema={propsSchema}
        defaultProps={mockProps}
        fps={FPS}
        width={1080}
        height={1920}
        durationInFrames={300}
        calculateMetadata={calc}
      />
      <Composition
        id="Long"
        component={VideoRoot}
        schema={propsSchema}
        defaultProps={{"format":"long-16x9","title":"太阳能安装工：澳洲最缺的高薪技工之一","occupation":{"nameZh":"太阳能安装工","nameEn":"Solar Panel Installer","anzscoCode":"342113","summary":"安装住宅与商业屋顶光伏系统，澳洲清洁能源目标下持续紧缺。","salaries":[{"label":"初级（0~2年）","min":60000,"max":80000},{"label":"中级（2~5年）","min":80000,"max":105000},{"label":"高级/项目（5年+）","min":100000,"max":135000}],"ratings":[{"labelZh":"高","dimension":"job_demand","stars":5},{"labelZh":"低","dimension":"competition","stars":2},{"labelZh":"较高","dimension":"income_level","stars":4}],"visaPathways":[{"subclass":"482","name":"TSS"},{"subclass":"186","name":"ENS"}],"growthAreas":["住宅屋顶光伏","工商业光伏","储能 Solar+ESS"]},"scenes":[{"id":"title","name":"开场","narration":"想在澳洲拿高薪又好移民？看看太阳能安装工。","durationSec":4,"broll":"solar panel rooftop"},{"id":"salary","name":"薪资","narration":"中级年薪八到十万澳元，高级项目能到十三万五。","durationSec":8,"broll":"money calculator"},{"id":"cta","name":"结尾","narration":"关注我，了解更多澳洲紧缺职业。","durationSec":3,"broll":"subscribe"}],"theme":{"primary":"#10B981","bg":"#0B1120","accent":"#F59E0B","font":"Inter"}}}
        fps={FPS}
        width={1920}
        height={1080}
        durationInFrames={300}
        calculateMetadata={calc}
      />
    </>
  );
};
