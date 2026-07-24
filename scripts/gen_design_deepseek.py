"""
用 DeepSeek 生成静态设计图（HTML mockup）。

设计探索用：**不绑定现有 site 的配色/主题**，由模型自主提出一套完整视觉方案，
便于与现行风格横向对比后决策。

用法：
  python scripts/gen_design_deepseek.py compare   # 职业对比页 -> aijobrisk-design/deepseek/compare.html
"""
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "aijobrisk-design", "deepseek")

BASE = (os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com").rstrip("/")
KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"

SYSTEM = (
    "You are a senior product designer and front-end engineer with a strong visual point of view. "
    "You output ONE complete, self-contained HTML file and nothing else. "
    "No markdown fences, no commentary, no explanation — raw HTML only, starting with <!DOCTYPE html>."
)

# 产品背景：只讲「是什么」，不讲「长什么样」——视觉方向完全交给模型
CONTEXT = """
PRODUCT CONTEXT (what the product is — NOT how it should look):
- Site: aijobrisk.com. It helps people understand how exposed their job is to AI, alongside
  salary, job demand, skills and migration information.
- Data is serious and research-backed: official national labour statistics across 14 countries,
  plus generative-AI exposure research (ILO Working Paper 140; Eloundou et al., OpenAI).
- Audience: job seekers, career changers, HR leaders and workforce planners.
- The tone should feel credible and useful rather than sensational.
"""

DESIGN_FREEDOM = """
VISUAL DIRECTION — YOUR CALL (this is the point of the exercise):
- Do NOT copy or assume any existing site styling. Start from a blank canvas.
- Invent ONE cohesive visual identity of your own: colour system, typography scale, spacing
  rhythm, corner radii, elevation/borders, and the visual treatment of data.
- Commit to a distinctive, opinionated aesthetic — this mockup will be compared side-by-side
  against a different design direction, so it should have a clear personality rather than
  playing it safe.
- Define your colours as CSS custom properties on :root so the palette is easy to read off.
- You choose whether the page is light, dark, or supports both.
- Use a system font stack (no web fonts), but design a deliberate type scale with it.
"""

# 真实数据（取自 occupations_v2 / occ-detail-v2，US），避免模型编造统计
FACTS = """
FACTS — use THESE numbers and points. Do not invent competing statistics.

OCCUPATION A — "Bookkeeping, Accounting & Auditing Clerks" (Bookkeeper), US, SOC 43-3031
  Workforce: 1,593,200 | Average salary: $53,560
  AI exposure percentile: 88/100 | Automation exposure: 8.5/10 | AI risk rating: 8.0/10
  Entry-level risk: 8.0/10 | Human moat: 3.0/10 | AI upside: 7.5/10
  Ratings (0–10): learning difficulty 3, learning duration 2, certification difficulty 2,
    job demand 6, competition 5, income level 3, work intensity 5, future prospect 5
  Verdict: AI will automate much data entry, reconciliation and report generation, sharply
    reducing entry-level roles; practitioners who move up into analysis retain value.
  Tasks most exposed: manual entry of invoice/receipt data; bank reconciliation and discrepancy
    adjustment; generating standard statements (trial balance, P&L); classifying and coding
    repetitive expenses; routine accounts receivable/payable processing.
  AI augments: anomaly/fraud detection and alerting; real-time dashboards; ML cash-flow
    forecasting; automated month-end close with data-integrity validation; turning unstructured
    PDFs/receipts into structured entries.
  Human moat: explaining complex financial anomalies and advising the business; communicating
    financial strategy to clients and management; non-standard transactions and accounting
    judgement; ensuring compliance and audit requirements; cross-department collaboration.
  Skills to build: QuickBooks Online / Xero; advanced Excel & Power BI; RPA basics; SQL and
    basic data modelling.

OCCUPATION B — "Accountants and Auditors" (Accountant), US, SOC 13-2011
  Workforce: 1,538,200 | Average salary: $94,750
  AI exposure percentile: 86/100 | Automation exposure: 7.5/10 | AI risk rating: 5.0/10
  Entry-level risk: 8.0/10 | Human moat: 6.5/10 | AI upside: 8.5/10
  Ratings (0–10): learning difficulty 5, learning duration 6, certification difficulty 7,
    job demand 8, competition 5, income level 7, work intensity 6.5, future prospect 6
  Verdict: A highly structured occupation — basic bookkeeping, reconciliation and tax
    calculation are quickly automated, but complex auditing and strategic finance endure.
  Tasks most exposed: invoice recognition and three-way matching (AI OCR); bank reconciliation
    and auto-classification (RPA); standard tax-return generation; drafting initial financial
    reports; large-sample substantive audit testing (AI tests the full population).
  AI augments: abnormal-transaction and fraud detection; tax-planning scenario simulation;
    cash-flow forecasting and rolling budgets; audit risk assessment; NLP contract-clause
    compliance review.
  Human moat: structured judgement on complex transactions (e.g. M&A accounting); stakeholder
    communication and business advisory; professional judgement in principle-based grey areas
    of accounting standards; cross-department process design; legal liability, signing
    authority and professional ethics.
  Skills to build: Power BI/Tableau + SQL; Python/R automation; AI tooling (Xero AI, Audit
    Command Language); advanced Excel modelling (VBA/Power Query); industry specialisation.

Education / qualification reality (reflect the ratings above):
  Bookkeeper — short vocational path, certificate or diploma, no degree required, low
    certification barrier; entry in months.
  Accountant — bachelor's degree plus a professional qualification (CPA/CA/ACCA), multi-year
    path, high certification barrier.

Data provenance to cite on the page: official national labour statistics (U.S. BLS OEWS /
O*NET) plus generative-AI exposure research — ILO Working Paper 140 and Eloundou et al.
"GPTs are GPTs" (OpenAI). Note: ILO WP140 is a working paper — do NOT describe the
underlying research as "peer-reviewed".
"""

# 排行榜真实数据（US，取自 occupations_v2）
RANK_FACTS = """
FACTS — these are the real leaderboards (United States). Use THESE occupations and numbers.
Do not invent occupations or competing statistics. "Exposure" is an AI-exposure percentile 0–100.

BOARD 1 — Most exposed to AI (highest exposure)
  1. Correspondence Clerks — exposure 100, $48,090
  2. Writers and Authors — exposure 100, $86,090
  3. Interpreters and Translators — exposure 100, $66,360
  4. Mathematicians — exposure 100, $129,260
  5. Brokerage Clerks — exposure 99, $72,850

BOARD 2 — Least exposed to AI (most resilient)
  1. Agricultural Equipment Operators — exposure 4, $43,710
  2. Athletes and Sports Competitors — exposure 4, $206,180
  3. Pile Driver Operators — exposure 4, $80,710
  4. Excavating & Loading Machine Operators, Surface Mining — exposure 4, $59,930
  5. Cooks, Short Order — exposure 4, $36,120

BOARD 3 — Highest paying
  1. Pediatric Surgeons — $502,050, exposure 49
  2. Cardiologists — $454,940, exposure 49
  3. Radiologists — $381,530, exposure 80
  4. Orthopedic Surgeons (except pediatric) — $373,570, exposure 47
  5. Anesthesiologists — $360,570, exposure 46

BOARD 4 — Largest workforce
  1. Fast Food and Counter Workers — 3,662,600 workers, exposure 23
  2. Retail Salespersons — 3,555,900 workers, exposure 57
  3. Cashiers — 3,357,000 workers, exposure 47
  4. Registered Nurses — 3,200,000 workers, exposure 58
  5. Customer Service Representatives — 2,912,000 workers, exposure 95

BOARD 5 — Strongest job demand
  1. Nurse Practitioners — demand 9.5/10, $137,300, exposure 63
  2. Family Medicine Physicians — demand 9.0/10, $255,820, exposure 64
  3. Nurse Anesthetists — demand 9.0/10, $248,320, exposure 31
  4. Dentists, All Other Specialists — demand 9.0/10, $247,930, exposure 43
  5. Computer & Information Systems Managers — demand 9.0/10, $192,160, exposure 87

BOARD 6 — Deepest human moat (hardest for AI to replace)
  1. Registered Nurses — moat 9.0/10, exposure 58
  2. Analog / Mixed-Signal IC Design Engineer — moat 9.0/10, exposure 85
  3. Airline Pilots, Copilots & Flight Engineers — moat 9.0/10, exposure 49
  4. Commercial Pilots — moat 9.0/10, exposure 39
  5. Air Traffic Controllers — moat 9.0/10, exposure 53

Coverage: 6,678 occupations across 14 countries.
Data provenance to cite: official national labour statistics (U.S. BLS OEWS / O*NET) plus
generative-AI exposure research — ILO Working Paper 140 and Eloundou et al. "GPTs are GPTs"
(OpenAI). ILO WP140 is a working paper — do NOT call the research "peer-reviewed".
"""

# 固定主题（从 aijobrisk-design/theme.css 提取；industries 两页必须用它，不再自由发挥）
THEME = """
BRAND THEME — you MUST use this exact palette (do NOT invent your own). Define these as CSS
variables on :root and build the whole page from them. Cool navy/slate + one blue accent;
calm, editorial, data-credible.
  --brand:#2563eb (links / primary CTA / active) ; --brand-hover:#1e4fc4 ; --brand-tint:#eef2ff
  --text:#0b1a2e ; --text-strong:#1e3a5f ; --text-body:#2c3e5a ; --text-muted:#4b5e7a
  --bg:#f6f9fc ; --bg-soft:#f8faff ; --surface:#ffffff ; --surface-tint:#eaf0f6 ;
  --surface-tint-2:#f0f5fe ; --surface-accent:#ecf3fa ; --line:#dce7f5
  Risk semantic (ONLY for risk indicators, always with a text label, never colour alone):
    --risk-low:#059669 / bg #d1fae5 ; --risk-mid:#f59e0b / bg #fef3c7 ; --risk-high:#dc2626 / bg #fee2e2
  --radius:12px ; --shadow:0 1px 3px rgba(11,26,46,.06),0 4px 12px rgba(11,26,46,.05)
Use ONE accent (the blue) only. System font stack. Generous whitespace.
Logo mark (inline SVG, top-left, next to the wordmark "AI Job Risk"):
  <svg viewBox="0 0 28 28" fill="none"><rect x="2" y="2" width="24" height="24" rx="6" stroke="#2563eb" stroke-width="2"/><path d="M8 19 L14 8 L20 19" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="17" r="1.5" fill="#f59e0b"/></svg>
"""

IND_FACTS = """
FACTS — use THESE. Data is a many-to-many occupation↔industry map (an occupation appears in
several industries). Do NOT show an "average risk" per industry (not meaningful). 6,678
occupations across 14 countries; industries below are NAICS sectors with US occupation counts.

20 INDUSTRIES (id — name — US occupation count):
  health — Health care & social assistance — 251
  manufacturing — Manufacturing — 306
  construction — Construction — 201
  retail — Retail trade — 192
  professional — Professional, scientific & technical services — 315
  information — Information — 160
  finance — Finance & insurance — 115
  education — Educational services — 336
  government — Government & public sector — 428
  transport — Transportation & warehousing — 110
  hospitality — Accommodation & food services — 91
  wholesale — Wholesale trade — 272
  admin-support — Administrative & support & waste services — 385
  management — Management of companies & enterprises — 206
  arts — Arts, entertainment & recreation — 143
  real-estate — Real estate & rental — 105
  utilities — Utilities — 61
  mining — Mining, quarrying, oil & gas — 69
  agriculture — Agriculture, forestry, fishing & hunting — 42
  other-services — Other services — 261

SAMPLE occupations inside "Health care & social assistance" (name — AI-risk 0–100 — median
salary — US workforce), 251 total:
  Registered Nurses — 58 — $101,420 — 3,200,000
  Customer Service Representatives — 95 — $46,590 — 2,912,000
  General and Operations Managers — 68 — $134,940 — 2,500,000
  Janitors and Cleaners — 5 — $38,760 — 2,360,000
  Office Clerks, General — 86 — $46,420 — 2,200,000
  Secretaries and Administrative Assistants — 93 — $49,350 — 1,898,400
  Bookkeeping, Accounting & Auditing Clerks — 88 — $53,560 — 1,593,200
  Software Developers — 96 — $148,100 — 1,548,200
  Accountants and Auditors — 86 — $94,750 — 1,538,200
  Maids and Housekeeping Cleaners — 8 — $37,080 — 1,500,000
  Nursing Assistants — 40 — $38,200 — 1,350,000
  Medical Assistants — 72 — $42,000 — 780,000
AI-risk severity labels: 0–33 Low, 34–66 Moderate, 67–100 High.
Data provenance to cite: official national labour statistics (BLS OEWS / O*NET) + BLS National
Employment Matrix for occupation↔industry; AI exposure from ILO Working Paper 140 and
Eloundou et al. (OpenAI). ILO WP140 is a working paper — do NOT call it "peer-reviewed".
"""

PROMPTS = {
    "industries": CONTEXT + THEME + IND_FACTS + """
TASK: Design a STATIC design mockup (a visual design comp) for the **/industries overview
page** — an index of all industries, each linking to its own /industry/{id} page.

The page MUST contain:
1. HEADER — H1 + short subhead. State the coverage (6,678 occupations across 14 countries) and
   that an occupation can belong to several industries (many-to-many). A country selector
   showing "United States" (static).
2. INDUSTRY GRID — render ALL 20 industries from FACTS as cards in a responsive grid. Each card:
   industry name, a small inline icon (simple inline SVG/CSS glyph, your choice per industry),
   the occupation count, and 2–3 example occupation names. The whole card links to
   href="industry.html" (placeholder for /industry/{id}). Do NOT show an average risk per
   industry. Give the card a subtle hover state.
3. A short data-provenance note near the bottom.
Also: top nav (logo + wordmark + a few links) and a minimal footer.

TECHNICAL: one self-contained .html, all CSS in one <style> in <head>, KEEP THE CSS COMPACT
(the whole file must fit well under 8000 output tokens — do not pad), no external assets,
inline SVG only, tiny cosmetic JS at most, semantic HTML5, one <h1>, responsive 375–1280px,
never scroll horizontally.
Output the raw HTML file only, complete and properly closed.
""",

    "industry-detail": CONTEXT + THEME + IND_FACTS + """
TASK: Design a STATIC design mockup for a single **/industry/{id} detail page**, using
"Health care & social assistance" as the example.

The page MUST contain:
1. HEADER — breadcrumb (Industries › Health care), H1 = the industry name, a one-line
   description, and summary stats (e.g. "251 occupations in the United States"). Country
   selector showing "United States" (static). Do NOT show an average risk for the industry.
2. OCCUPATION TABLE — the core. One row per occupation listing: occupation name, AI-risk score
   (0–100, shown as a number + a small risk-coloured badge WITH a text label Low/Moderate/High),
   median salary, and workforce (number of workers). Populate with the sample occupations from
   FACTS (and you may add a few more plausible health occupations to fill the table).
   The COLUMN HEADERS must look sortable — each sortable column header shows a sort affordance
   (e.g. ▲/▼), with one column shown as the active sort. A tiny bit of JS to actually sort is
   welcome but optional; the static design just needs to read as a sortable data table.
   Make the table responsive: on mobile it may become stacked cards, but keep it readable.
3. A short note that an occupation may appear in several industries, and data provenance.
Also: top nav (logo + wordmark + links) and a minimal footer.

TECHNICAL: one self-contained .html, all CSS in one <style> in <head>, KEEP THE CSS COMPACT
(the whole file must fit well under 8000 output tokens — do not pad), no external assets,
inline SVG only, tiny cosmetic/sort JS at most, semantic HTML5, one <h1>, a real <table> with
<thead>/<th scope="col"> for accessibility, responsive 375–1280px, never scroll horizontally.
Output the raw HTML file only, complete and properly closed.
""",

    "rankings": CONTEXT + DESIGN_FREEDOM + RANK_FACTS + """
TASK: Design a STATIC design mockup (a visual design comp) for the **rankings / leaderboards
index page** of the site.

The page presents SEVERAL different leaderboards at once. Each board shows only its TOP 5,
and links out to its own full ranking page.

The page MUST contain:

1. HEADER AREA
   - An H1 and a short subhead explaining what the rankings are and the coverage
     (6,678 occupations across 14 countries).
   - A country selector control showing "United States" as the current selection (static — it
     only needs to look right, not work).

2. THE LEADERBOARD GRID — the core of the page
   - Render ALL SIX boards from FACTS, each as its own self-contained card:
       Most exposed to AI · Least exposed to AI · Highest paying · Largest workforce ·
       Strongest job demand · Deepest human moat
   - Each card has: a clear board title, a one-line description of what it measures, and
     exactly FIVE ranked rows.
   - Each row shows the rank number, the occupation name, and that board's headline metric,
     plus a secondary metric where FACTS provides one. Give rank 1 extra visual emphasis.
   - Where a row shows an AI exposure value, pair it with a text severity label — never rely
     on colour alone to convey risk.
   - Each card ends with a "View full ranking →" link that points to **ranking-item.html**
     (use href="ranking-item.html"). This is the ONLY way to reach the detail page — the top 5
     rows themselves may link to occupations, but the full-ranking entry point is this link.
   - Responsive: multi-column grid on desktop, single column on mobile. Cards should align
     tidily even though their content lengths differ.

3. A short METHODOLOGY / DATA PROVENANCE note near the bottom citing the sources from FACTS.

ALSO INCLUDE: a simple top nav, a minimal footer, and at the very bottom a small
"Design system" strip showing your chosen palette as labelled swatches with hex values plus a
one-line note on typography and the mood you aimed for.

TECHNICAL REQUIREMENTS:
- ONE self-contained .html file. All CSS in a single <style> tag in <head>. No external
  stylesheets, web fonts, CDNs or external images — inline SVG / CSS shapes only.
- No JavaScript required; any JS must be tiny and purely cosmetic.
- Semantic HTML5, exactly one <h1>, ordered lists for the rankings where appropriate,
  accessible labels on the country selector, readable contrast.
- Fully responsive: works at 375px and 1280px, never scrolls horizontally.
- Polished and production-plausible.

Output the raw HTML file only.
""",


    "bookkeeper-vs-accountant": CONTEXT + DESIGN_FREEDOM + FACTS + """
TASK: Design a STATIC design mockup (a visual design comp) for the **comparison RESULT page**
that a user lands on after comparing two occupations: Bookkeeper vs Accountant.

The page MUST contain, in this order:

1. HEADER + RISK SCORES
   - Page title naming both occupations, and a clear side-by-side display of each occupation's
     AI risk score (use the AI risk rating out of 10, and you may also surface the exposure
     percentile). Make the two scores the visual anchor of the page.
   - Each score paired with a text severity label — never colour alone.

2. ONE-SENTENCE VERDICT
   - A single prominent descriptive sentence summarising the comparison (e.g. that both are
     highly exposed, but the accountant's professional judgement and signing authority give a
     substantially deeper human moat than the bookkeeper's).

3. TASK-BY-TASK COMPARISON
   - The core section. For each occupation, list its individual exposed tasks (from FACTS) as
     rows, each with a PROGRESS BAR showing how automatable that task is, plus a percentage or
     level label on the bar.
   - Lay the two occupations out so the tasks can be read against each other.
   - The per-task bar values are illustrative design values — add a small caption saying the
     per-task figures are illustrative, while the headline scores come from the cited research.

4. WHERE AI AUGMENTS — separate description for each occupation, side by side.

5. HUMAN MOAT — separate description for each occupation, side by side, and make it visually
   evident that the accountant's moat (6.5/10) is far deeper than the bookkeeper's (3.0/10).

6. OTHER DIMENSIONS — compare the two on: salary, education path, qualifications/certification
   barrier, and future prospects. Use whatever layout reads best (table or paired cards), with
   the real figures from FACTS.

7. FAQ — about 5 question/answer pairs relevant to this specific comparison (e.g. should a
   bookkeeper retrain as an accountant, will AI eliminate bookkeeping, what the score means,
   where data comes from, how to stay employable). Use native <details>/<summary>.

ALSO INCLUDE: a simple top nav, a minimal footer, and at the very bottom a small
"Design system" strip showing your chosen palette as labelled swatches with hex values plus a
one-line note on typography and the mood you aimed for.

TECHNICAL REQUIREMENTS:
- ONE self-contained .html file. All CSS in a single <style> tag in <head>. No external
  stylesheets, web fonts, CDNs or external images — inline SVG / CSS shapes only.
- Progress bars must be pure CSS/HTML (no JS needed) and accessible (use role="progressbar"
  with aria-valuenow, or equivalent, plus a visible text value).
- Semantic HTML5, exactly one <h1>, readable contrast.
- Fully responsive: works at 375px and 1280px, never scrolls horizontally.
- Polished and production-plausible.

Output the raw HTML file only.
""",

    "compare": CONTEXT + DESIGN_FREEDOM + """
TASK: Design a STATIC design mockup (a visual design comp, not a working app) for an
**occupation comparison page**. Use realistic placeholder content — no lorem ipsum.

The page MUST contain these four sections, in this order:

1. TWO OCCUPATION SELECTORS
   - A hero area with an H1 and a short subhead.
   - Two prominent selector cards ("Occupation A" / "Occupation B"), each with a
     search/combobox control showing a realistic pre-filled example (e.g. "Registered Nurse"
     vs "Software Engineer"), the country it applies to, and a small preview line
     (e.g. an AI-risk indicator + median salary).
   - A "VS" divider between them and a swap (⇄) affordance.
   - They stack vertically on mobile.

2. COMPARISON RESULT ENTRY
   - A prominent primary call-to-action (e.g. "Compare these jobs →").
   - Beneath it, a compact teaser of what the comparison delivers: a small side-by-side table
     or 3–4 metric tiles (AI exposure score, median salary, job demand, migration friendliness)
     showing both occupations' values with a clear visual indicator plus a text label.

3. POPULAR COMPARISON COMBINATIONS
   - A section of 6–8 clickable cards/chips, each showing "Job A vs Job B" plus a tiny stat
     (e.g. "AI risk 3.1 vs 7.4"). Realistic pairs, e.g. Registered Nurse vs Software Engineer,
     Accountant vs Data Analyst, Electrician vs Truck Driver, Graphic Designer vs UX Designer,
     Teacher vs Corporate Trainer, Paralegal vs Lawyer.
   - Responsive grid.

4. FAQ
   - 5–6 question/answer pairs: how the comparison works, where the data comes from, what the
     AI exposure score means, country coverage, how often data updates.
   - Use native <details>/<summary> accordions so the answers stay in the DOM.

ALSO INCLUDE:
- A simple top nav (wordmark + a few links) and a minimal footer.
- At the very bottom, a small "Design system" strip that displays the palette you chose as
  labelled colour swatches (with their hex values) plus a one-line note on the typography and
  the mood you were going for. This lets a reviewer read your visual decisions at a glance.

ACCESSIBILITY: never convey a risk level by colour alone — always pair it with a text label.
Maintain readable contrast.

TECHNICAL REQUIREMENTS:
- ONE self-contained .html file. All CSS in a single <style> tag in <head>. No external
  stylesheets, no web fonts, no CDN, no external images — inline SVG or CSS shapes only.
- No JavaScript required; any JS must be tiny and purely cosmetic.
- Semantic HTML5, one <h1>, accessible labels on all controls.
- Fully responsive: works at 375px and 1280px, never scrolls horizontally.
- Polished and production-plausible — a stakeholder will review this comp.

Output the raw HTML file only.
"""
}


def generate(kind):
    if not KEY:
        sys.exit("缺少 DEEPSEEK_API_KEY（.env）")
    body = {
        "model": MODEL,
        "max_tokens": 8192,
        "temperature": 1.0,          # 鼓励更鲜明的视觉主张
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": PROMPTS[kind]}],
    }
    print(f"[deepseek] model={MODEL} 生成 {kind} 设计图（自主配色）…")
    r = requests.post(f"{BASE}/chat/completions",
                      headers={"Authorization": f"Bearer {KEY}",
                               "Content-Type": "application/json"},
                      json=body, timeout=600)
    r.raise_for_status()
    data = r.json()
    html = data["choices"][0]["message"]["content"].strip()

    # 去掉模型可能加的 markdown 围栏
    html = re.sub(r"^```(?:html)?\s*", "", html)
    html = re.sub(r"\s*```$", "", html).strip()

    if "<!DOCTYPE" not in html[:200] and "<html" not in html[:400]:
        print("[warn] 输出开头不像完整 HTML，仍照写，请人工检查")

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"{kind}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html + "\n")

    usage = data.get("usage") or {}
    print(f"[deepseek] tokens: prompt={usage.get('prompt_tokens')} "
          f"completion={usage.get('completion_tokens')} "
          f"finish={data['choices'][0].get('finish_reason')}")
    print(f"[ok] {out}  ({len(html):,} chars)")
    return out


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "compare"
    if kind not in PROMPTS:
        sys.exit(f"未知类型 {kind}；可选：{', '.join(PROMPTS)}")
    generate(kind)
