# Codex Session Handoff · 2026-06-15

## Scope Covered

This session reviewed:

- `video_pipeline/out/ppt/bi-analyst.pptx`
- Mobile developer outline files in `video_pipeline/out/outlines/`
- Competitor / keyword directions for Australia career content
- Database coverage for AU occupations
- Frontend review for `http://localhost:4321/AU/en/`

The last user question before reset was:

- Whether adding Seek / Indeed / LinkedIn job-result screenshots to occupation pages is useful

That question was not answered yet in the thread because the user then asked to save session state.

## PPT Review

Reviewed actual file:

- `video_pipeline/out/ppt/bi-analyst.pptx`

Supporting inspection artifacts created:

- `video_pipeline/out/ppt/review_png/`
- `video_pipeline/out/ppt/review_contact.png`

Main conclusions:

- The PPT structure is complete, but it feels more like an internal deck than a growth-oriented content asset.
- The biggest weakness is first-screen impact: weak hook, too much empty space, and no strong visual story.
- The file only embedded chart images; the downloaded occupational images in `video_pipeline/out/img/` were not actually used in the PPT.
- Trend-page titles are too absolute for estimated data.
- CTA is generic and should be replaced with a stronger comment / lead-capture trigger.

Important data-risk note:

- The PPT used `ANZSCO 262199` and migration wording that looked too definitive.
- That should be re-checked against current Home Affairs / legislation sources before being presented as official mapping.

## Outline Review

Reviewed files:

- `video_pipeline/out/outlines/11_mobile-developer_tiktok_short.md`
- `video_pipeline/out/outlines/12_mobile-developer_youtube_long.md`

Key findings:

- The short version is structurally fine but too absolute in migration wording.
- The long version reads smoothly but still sounds like a linear explainer rather than a high-retention video script.
- `482 TSS` wording is outdated and should be updated to current `Skills in Demand` framing where appropriate.
- `Mobile Developer = ANZSCO 261319` is risky and should not be stated as a settled official code without clear mapping logic.
- CTA in the TikTok version is weak and should use a keyword-driven comment trigger.
- The scripts need more "decision points" and "contrarian truths", not just feature lists.

Related source file reviewed:

- `scripts/seed_mobile_developer.py`

## Competitor / Keyword Direction

Suggested content directions focused on:

- Australia jobs + salary
- skilled migration + occupation + salary
- short-form salary transparency
- Chinese-language Australia career / visa / pathway search intent

Reference competitor types suggested:

- Street-interview / salary transparency style
- SEEK-style career data framing
- Australia study / migration / career planning accounts

Keyword structure recommended:

- `Australia + job title + salary`
- `Australia + job title + visa`
- `Australia + job title + skilled migration`
- `澳洲 + 职业名 + 薪资`
- `澳洲 + 职业名 + 482`
- `澳洲 + 职业名 + PR`

## Database Coverage Assessment

Database access was confirmed through `.env` and `db/connection.py`.

Read-only DB findings:

- AU occupations in DB: `191`
- `shortage_listed=1`: `143`
- `shortage_listed=0`: `48`

Benchmark data downloaded:

- `.codex_tmp/jsa_occupation_profiles_feb_2026.xlsx`
- `.codex_tmp/jsa_employment_projections_may_2025_2035.xlsx`

Coverage findings:

- JSA 4-digit occupation groups: `358`
- Current DB 4-digit coverage: `145`
- Coverage rate: about `40.5%`
- Employment-weighted coverage: about `55.7%`

Interpretation:

- The current list is strong as a migration / shortage / high-interest AU occupation library.
- It is not a comprehensive Australia labour-market coverage set.
- Strongest current coverage is in trades, healthcare, IT, engineering, construction, mining, teaching, and care work.
- Biggest gaps are retail, clerical/admin, front-office, service, some healthcare support, and several management / professional roles with large employment bases.

High-priority missing occupation families identified:

- Sales assistants / retail
- General clerks
- Receptionists / medical receptionists
- Office managers
- Primary school teachers
- Commercial cleaners
- Kitchenhands / cooks / bakers
- Management consultants
- HR managers
- Health and welfare services managers
- Practice managers
- Dental assistants
- Medical technicians
- Counsellors
- Policy analysts
- Engineering managers
- Production managers
- Bus drivers
- Bookkeepers / payroll clerks
- ICT sales / telecom engineering / web developer adjacent roles

Important data-quality note:

- Some occupations in the DB appear to use market-friendly or custom occupational labels that do not cleanly map to exact official JSA profile codes.
- This is especially relevant for content that states ANZSCO codes directly.
- Recommended future data model fields:
  - `official_anzsco_code`
  - `marketing_title`
  - `source_code_version`
  - `visa_relevance`
  - `traffic_priority`

## Frontend Review

Reviewed live page:

- `http://localhost:4321/AU/en/`

Reviewed source files:

- `site/src/layouts/Base.astro`
- `site/src/pages/[country]/[locale]/index.astro`
- `site/src/pages/[country]/[locale]/[category]/[slug].astro`
- `site/src/pages/[country]/[locale]/compare/[pair].astro`
- `site/src/lib/data.ts`
- `site/src/components/RatingRadar.astro`

Main findings:

- The site works as a clean data index, but not yet as a strong user decision product.
- The hero section is too weak: it states the product name but not why the site is useful.
- The page jumps into compare cards and category grids too quickly.
- There is no search or filter layer, which becomes a navigation problem at current content volume.
- Cards repeat information unnecessarily, especially on English pages where the English name duplicates the title.
- The design is coherent with the project palette, but it reads more like an internal tool / dark knowledge base than a high-conviction content product.
- Mobile responsiveness is under-specified.

Implementation-specific notes:

- `Base.astro` has no real responsive `@media` rules.
- Detail and compare pages use hard-coded `grid-template-columns:1fr 1fr`, which likely compresses poorly on narrow screens.
- English UI still mixes Chinese text in some places, for example migration labels and some table headings.

Recommended frontend priorities:

1. Add a real hero with value proposition and main CTA.
2. Add search, filter, and sort to the index page.
3. Simplify occupation cards to avoid duplicate name rows.
4. Add a compact summary block at the top of each occupation page:
   - overall score
   - senior salary
   - PR relevance
   - training time
   - demand level
5. Add responsive rules and mobile stack behavior.
6. Normalize English-language labels across cards and detail pages.

## Pending Question

The user asked:

- Whether occupation pages should include Seek / Indeed / LinkedIn job-result screenshots

This was not answered yet.

Likely continuation topic:

- Evaluate whether job-result screenshots improve trust, freshness, and CTR on occupation pages
- Weigh usefulness against maintenance cost, staleness, and policy / scraping concerns
- Recommend whether to use static screenshots, structured job-count widgets, or outbound CTA blocks instead

## Useful Paths

- PPT file: `video_pipeline/out/ppt/bi-analyst.pptx`
- PPT review contact sheet: `video_pipeline/out/ppt/review_contact.png`
- Outline files:
  - `video_pipeline/out/outlines/11_mobile-developer_tiktok_short.md`
  - `video_pipeline/out/outlines/12_mobile-developer_youtube_long.md`
- Site source:
  - `site/src/layouts/Base.astro`
  - `site/src/pages/[country]/[locale]/index.astro`
  - `site/src/pages/[country]/[locale]/[category]/[slug].astro`
  - `site/src/pages/[country]/[locale]/compare/[pair].astro`
  - `site/src/lib/data.ts`

