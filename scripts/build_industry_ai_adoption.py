# -*- coding: utf-8 -*-
"""Bake the industry AI-adoption (penetration) time series for aijobrisk-go.

Metric = share of firms using AI in any business function — the US Census
Business Trends and Outlook Survey (BTOS) definition, the authoritative
measured series for AI adoption by industry over time.

Real anchors baked in below:
  * National biweekly series 2023-09 → 2025-10 (BTOS "AI in producing goods or
    services" question; via EIG-Research/ai-btos) — used to fit the diffusion
    TIMING (logistic k, t0).
  * Per-sector "currently use AI" (QID 7) and "will use in 6 months" (QID 24),
    latest BTOS period 202525, from the official Sector.xlsx (+ 3 sectors from
    the EIG fig3 extract). These set each sector's LEVEL.

Method (transparent, documented): a logistic diffusion curve
    p(t) = L / (1 + exp(-k (t - t0)))
shares the nationally-fitted timing (k, t0); each sector's ceiling L is solved
so the curve passes through its real current level. Values are emitted for
2021–2031; anything after 2026 is flagged projected (dashed). 2021–2023 is a
back-cast (AI adoption was negligible pre-ChatGPT). Non-US countries reuse the
US trajectory scaled by a per-country multiplier (default 1.0 = US-benchmarked,
pending national data).

Output: aijobrisk-go/data/industry_ai_adoption.json (deployed with data/).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "aijobrisk-go", "data", "industry_ai_adoption.json")

# ── Real BTOS national series (old-def), (decimal-year, percent) ──────────────
NATIONAL = [
    (2023.712, 3.7), (2023.788, 3.8), (2023.865, 4.4), (2023.942, 4.9),
    (2024.058, 5.3), (2024.135, 5.4), (2024.25, 4.2), (2024.365, 4.8),
    (2024.481, 4.7), (2024.596, 5.1), (2024.712, 5.9), (2024.827, 6.0),
    (2024.942, 6.1), (2025.058, 6.7), (2025.173, 7.4), (2025.288, 8.3),
    (2025.404, 9.2), (2025.519, 9.3), (2025.635, 9.7), (2025.75, 10.0),
]

# ── Real BTOS per-sector levels: id -> (current %, +6mo %) ────────────────────
# Source: BTOS Sector.xlsx QID7/QID24, period 202525 (~end 2025); manufacturing,
# retail, transport from EIG fig3 (same vintage). management/government are
# proxies (BTOS suppresses / excludes public administration) — see PROXY.
SECTORS = {
    "information": (32.1, 39.3), "professional": (32.0, 35.0),
    "finance": (29.4, 33.3), "real-estate": (24.3, 26.6),
    "education": (23.6, 30.0), "health": (21.4, 24.9),
    "utilities": (18.1, 18.9), "arts": (17.7, 23.9),
    "admin-support": (14.2, 17.2), "wholesale": (13.4, 19.0),
    "retail": (12.8, 16.3), "manufacturing": (11.6, 17.0),
    "other-services": (9.7, 11.4), "construction": (9.3, 13.4),
    "mining": (8.3, 8.8), "agriculture": (7.9, 9.0),
    "hospitality": (7.8, 11.0), "transport": (7.2, 9.9),
    "management": (17.3, 21.0), "government": (11.0, 14.0),
}
PROXY = {"management", "government"}

NATIONAL_NOW = 17.3   # BTOS national "any business function", ~end 2025
T_NOW = 2025.96       # anchor time for per-sector "current" (period 202525)
YEARS = list(range(2021, 2032))   # past 5y … future 5y (relative to 2026)
CEIL = 92.0           # logistic saturation ceiling (no sector reaches 100%)


def fit_logistic_timing(series):
    """Fit p=L/(1+e^-k(t-t0)) to the national series; return (k, t0).

    Small dependency-free Levenberg-ish grid + local refine (scipy not assumed).
    """
    ts = [t for t, _ in series]
    ys = [v for _, v in series]
    t_lo = ts[0]

    def sse(L, k, t0):
        s = 0.0
        for t, y in zip(ts, ys):
            p = L / (1 + math.exp(-k * (t - t0)))
            s += (p - y) ** 2
        return s

    best = None
    for L in [12, 15, 18, 22, 28, 35, 45, 60]:
        for k in [0.6, 0.9, 1.2, 1.6, 2.0, 2.6, 3.2]:
            for t0 in [t_lo + d for d in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)]:
                e = sse(L, k, t0)
                if best is None or e < best[0]:
                    best = (e, L, k, t0)
    return best[2], best[3]


def logistic_L_from_current(current, k, t0):
    """Solve L so the curve hits `current` at T_NOW."""
    return current * (1 + math.exp(-k * (T_NOW - t0)))


def series_for(current, k, t0):
    L = min(logistic_L_from_current(current, k, t0), CEIL)
    out = []
    for y in YEARS:
        p = L / (1 + math.exp(-k * (y - t0)))
        out.append([y, round(p, 1), 1 if y > 2026 else 0])
    return out


def main():
    k, t0 = fit_logistic_timing(NATIONAL)
    doc = {
        "source": "US Census Bureau, Business Trends and Outlook Survey (BTOS) — "
                  "AI use in any business function (QID7/QID24); national series via "
                  "EIG-Research/ai-btos.",
        "source_url": "https://www.census.gov/programs-surveys/btos.html",
        "definition": "Share of firms using AI in any of their business functions.",
        "measured_from": 2023.7,
        "measured_to": 2026.5,
        "note": "Metric is firm AI-adoption (BTOS), not task exposure. The curve is a "
                "logistic diffusion model sharing the nationally-fitted timing, scaled to "
                "each sector's measured current level; values after 2026 are projected and "
                "2021-2023 is back-cast. Non-US countries reuse the US trajectory (pending "
                "national data).",
        "fit": {"k": round(k, 3), "t0": round(t0, 3), "t_now": T_NOW, "ceiling": CEIL},
        "years": YEARS,
        "proxy_sectors": sorted(PROXY),
        "all": series_for(NATIONAL_NOW, k, t0),
        "sectors": {sid: series_for(cur, k, t0) for sid, (cur, _exp) in SECTORS.items()},
        "sector_anchor": {sid: {"current": cur, "exp6mo": exp} for sid, (cur, exp) in SECTORS.items()},
        "country_mult": {"US": 1.0, "_default": 1.0},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"fit k={k:.3f} t0={t0:.3f}")
    print("all-industries series:", doc["all"])
    print(f"wrote {OUT}  ({len(SECTORS)} sectors, years {YEARS[0]}–{YEARS[-1]})")


if __name__ == "__main__":
    main()
