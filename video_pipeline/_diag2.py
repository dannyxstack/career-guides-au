"""临时诊断：抓 youtube_long 大纲的原始模型返回，定位 JSON 截断/格式问题。用完即删。"""
from anthropic import Anthropic
from db.connection import get_cursor
from video_pipeline import config
from video_pipeline.prompts import SYSTEM, build_outline_prompt
from video_pipeline.data_source import get_occupation

with get_cursor() as cur:
    cur.execute("SELECT id FROM occupations WHERE anzsco_code='263211' AND country_code='AU'")
    oid = cur.fetchone()["id"]

occ = get_occupation(oid, "zh-CN")
prompt = build_outline_prompt(occ, "youtube_long")
client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
resp = client.messages.create(model=config.CLAUDE_MODEL, max_tokens=3000,
                              system=SYSTEM, messages=[{"role": "user", "content": prompt}])
text = resp.content[0].text
print("stop_reason:", resp.stop_reason)
print("output_tokens:", resp.usage.output_tokens)
print("text_len:", len(text))
print("--- around char 4270 ---")
print(repr(text[4230:4330]))
print("--- tail 200 ---")
print(repr(text[-200:]))
