"""把现有职业的中文旧分类重映射为 10 个英文一级大类。可重复运行（幂等）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.connection import get_cursor

TEN = {
    "Healthcare & Care", "Education & Community", "Trades & Construction",
    "IT & Digital", "Engineering & Infrastructure", "Business, Finance & Legal",
    "Hospitality, Retail & Tourism", "Transport, Logistics & Mining",
    "Agriculture & Environment", "Creative, Media & Personal Services",
}

# 整类映射：旧中文类 → 新英文类
WHOLESALE = {
    "技工": "Trades & Construction",
    "医疗": "Healthcare & Care", "医疗健康": "Healthcare & Care", "健康服务": "Healthcare & Care",
    "教育": "Education & Community", "教育/社会服务": "Education & Community", "社区服务": "Education & Community",
    "IT": "IT & Digital",
    "工程": "Engineering & Infrastructure",
    "商业/金融/法律": "Business, Finance & Legal", "商业": "Business, Finance & Legal", "金融": "Business, Finance & Legal",
    "餐饮/酒店/旅游": "Hospitality, Retail & Tourism",
    "采矿": "Transport, Logistics & Mining", "运输": "Transport, Logistics & Mining",
    "物流": "Transport, Logistics & Mining", "航空": "Transport, Logistics & Mining",
    "农业": "Agriculture & Environment", "环境": "Agriculture & Environment",
    "创意/媒体": "Creative, Media & Personal Services",
}

# 混合桶（IT/工程、其他、技术、技术员、专业、专业服务、管理）按 anzsco_title 逐职业覆盖
OVERRIDE = {
    # IT/工程
    "Computer Network and Systems Engineer": "IT & Digital",
    "ICT Business Analyst": "IT & Digital", "ICT Developers and Programmers nec": "IT & Digital",
    "ICT Managers": "IT & Digital", "ICT Security Specialist": "IT & Digital",
    "Machine Learning Engineer": "IT & Digital", "Software Engineer": "IT & Digital",
    "Web Designer": "IT & Digital",
    "Architect": "Engineering & Infrastructure", "Chemical Engineer": "Engineering & Infrastructure",
    "Civil Engineer": "Engineering & Infrastructure", "Electrical Engineer": "Engineering & Infrastructure",
    "Environmental Engineer": "Engineering & Infrastructure", "Mechanical Engineer": "Engineering & Infrastructure",
    "Mining Engineer": "Engineering & Infrastructure",
    "Natural and Physical Science Professionals nec": "Engineering & Infrastructure",
    "Industrial Designer": "Creative, Media & Personal Services",
    # 其他
    "Airline Pilot": "Transport, Logistics & Mining", "Marine Transport Professional": "Transport, Logistics & Mining",
    "Agricultural Technician": "Agriculture & Environment", "Arborist / Forestry Worker": "Agriculture & Environment",
    "Meat Process Worker": "Agriculture & Environment",
    "Construction Project Manager": "Trades & Construction",
    "Customs Officer": "Business, Finance & Legal", "Real Estate Agent / Property Manager": "Business, Finance & Legal",
    "Firefighter": "Education & Community", "Police Officer": "Education & Community", "Security Officer": "Education & Community",
    "Flight Attendant": "Hospitality, Retail & Tourism",
    "Hairdresser / Beauty Therapist": "Creative, Media & Personal Services",
    "Land Surveyor / Building Surveyor": "Engineering & Infrastructure",
    # 技术 / 技术员 / 专业
    "Architectural Draftsperson": "Engineering & Infrastructure", "Building Automation Technician": "Engineering & Infrastructure",
    "Building Inspector": "Engineering & Infrastructure", "Instrumentation Technician": "Engineering & Infrastructure",
    "Electronics Technician": "Engineering & Infrastructure",
    "Contract Administrator": "Business, Finance & Legal", "Quantity Surveyor": "Engineering & Infrastructure",
    # 专业服务
    "Court Reporter": "Business, Finance & Legal", "Funeral Director": "Creative, Media & Personal Services",
    "Interpreter": "Creative, Media & Personal Services", "Librarian": "Education & Community",
    "Pet Groomer": "Creative, Media & Personal Services", "Records Manager": "Business, Finance & Legal",
    "WHS Officer": "Business, Finance & Legal",
    # 管理
    "Facilities Manager": "Business, Finance & Legal",
}


def run():
    changed, skipped, unmapped = 0, 0, []
    with get_cursor() as cur:
        cur.execute("SELECT id, anzsco_title, category FROM occupations")
        rows = cur.fetchall()
        for r in rows:
            cat = r["category"]
            if cat in TEN:
                skipped += 1
                continue
            new = OVERRIDE.get(r["anzsco_title"]) or WHOLESALE.get(cat)
            if not new:
                unmapped.append((r["id"], r["anzsco_title"], cat))
                continue
            cur.execute("UPDATE occupations SET category=%s WHERE id=%s", (new, r["id"]))
            changed += 1
    print(f"[remap] updated={changed} skipped(已英文)={skipped} unmapped={len(unmapped)}")
    for u in unmapped:
        print("  [UNMAPPED]", u)
    with get_cursor() as cur:
        cur.execute("SELECT category, COUNT(*) c FROM occupations GROUP BY category ORDER BY c DESC")
        print("--- 现有分类分布 ---")
        for r in cur.fetchall():
            print(f"  {r['c']:>4}  {r['category']}")


if __name__ == "__main__":
    run()
