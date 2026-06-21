"""快速验证 md_parser 解析结果，不需要数据库连接。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.parsers.md_parser import parse_md

data = parse_md("output/electrician.md")

print(f"anzsco_code : {data.get('anzsco_code')}")
print(f"anzsco_title: {data.get('anzsco_title')}")
print(f"name_zh     : {data.get('name_zh')}")
print(f"shortage    : {data.get('shortage_listed')}")
print(f"workforce   : {data.get('workforce_size')}")

ratings = data.get("ratings", [])
print(f"\nratings ({len(ratings)}):")
for r in ratings:
    stars = "★" * r["stars"] + "☆" * (5 - r["stars"])
    print(f"  {r['dimension']:<30} {r['label_zh']} {stars}")

print(f"\neducation   : {len(data.get('education', []))} rows")
print(f"salaries    : {len(data.get('salaries', []))} rows")
for s in data.get("salaries", []):
    print(f"  {s['experience'][:35]:<35} {s['salary_min']}~{s['salary_max']}")

print(f"\njob_listings: {len(data.get('job_listings', []))} rows")
for jl in data.get("job_listings", []):
    print(f"  {jl['platform']:<10} {jl['count_min']}~{jl['count_max']}")

print(f"\nvisa_pathways: {len(data.get('visa_pathways', []))} rows")
print(f"fit         : {len(data.get('suitability_fit', []))} items")
print(f"unfit       : {len(data.get('suitability_unfit', []))} items")
print(f"sources     : {len(data.get('sources', []))} rows")

faqs = data.get("faqs", [])
print(f"\nfaqs ({len(faqs)}):")
for f in faqs:
    print(f"  [{f['faq_type']:<15}] {f['question'][:45]}")

print(f"\ngrowth_areas: {data.get('growth_areas')}")
print(f"\nsummary[:80]: {(data.get('summary') or '')[:80]}")
