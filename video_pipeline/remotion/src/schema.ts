import {z} from "zod";

// 与 Python spec_builder 输出的 inputProps 一一对应（唯一数据契约）
export const salarySchema = z.object({
  label: z.string(),
  min: z.number().nullable(),
  max: z.number().nullable(),
});

export const ratingSchema = z.object({
  labelZh: z.string().nullable(),
  dimension: z.string(),
  stars: z.number().nullable(),
});

export const captionSchema = z.object({
  text: z.string(),
  start: z.number(),
  end: z.number(),
});

export const sceneSchema = z.object({
  id: z.string(),
  name: z.string(),
  narration: z.string(),
  durationSec: z.number(),
  broll: z.string().optional().default(""),
  audioSrc: z.string().nullable().optional(),
  captions: z.array(captionSchema).optional().default([]),
  bgImage: z.string().nullable().optional(),
});

export const propsSchema = z.object({
  format: z.string(),
  title: z.string(),
  occupation: z.object({
    nameZh: z.string().nullable(),
    nameEn: z.string().nullable(),
    anzscoCode: z.string(),
    summary: z.string().nullable(),
    salaries: z.array(salarySchema),
    ratings: z.array(ratingSchema),
    visaPathways: z.array(
      z.object({subclass: z.string(), name: z.string().nullable()})
    ),
    growthAreas: z.array(z.string()),
  }),
  scenes: z.array(sceneSchema),
  theme: z.object({
    primary: z.string(),
    bg: z.string(),
    accent: z.string(),
    font: z.string(),
  }),
});

export type VideoProps = z.infer<typeof propsSchema>;
export type Scene = z.infer<typeof sceneSchema>;
