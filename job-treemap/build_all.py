"""One-command build for the job-treemap site.

Runs the whole pipeline in the right order so a single command rebuilds everything:

  1. summaries   (LLM, cached)      -> job-treemap/summaries.json   [best-effort]
  2. longform    (LLM, cached)      -> job-treemap/longform.json    [best-effort]
  3. build.py    (pass 1)           -> dist/ (incl. the /embed pages shoot_maps needs)
  4. shoot_maps  (Playwright)       -> dist/static/maps/*.png       [best-effort]
  5. build.py    (pass 2)           -> dist/ (new PNGs into og:image / Dataset schema)

Steps 1, 2 and 4 are best-effort: if they fail (no DeepSeek key, no Playwright,
no network) the pipeline logs it and carries on — build.py has deterministic
fallbacks for missing summaries/longform/maps, so the site still builds. Only
build.py itself is fatal.

The LLM steps are incremental + cached: they skip countries/sections already in
their JSON and only call the API for what's missing (or everything with
--force-content), so running the full pipeline every time is cheap once cached.

Usage (run with whichever Python you use for this repo):
  python job-treemap/build_all.py                 # full pipeline
  python job-treemap/build_all.py --no-maps       # skip Playwright + 2nd build
  python job-treemap/build_all.py --fast          # build.py only (skip LLM + maps)
  python job-treemap/build_all.py --force-content # regenerate all LLM copy
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable or "python"


def run(cmd, label, fatal=False):
    print(f"\n===== {label} =====", flush=True)
    # Force UTF-8 in subprocesses — Windows' GBK console otherwise crashes on
    # non-ASCII prints (e.g. ö) mid-run.
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        rc = subprocess.run(cmd, cwd=REPO, env=env).returncode
    except FileNotFoundError as e:
        rc = 127
        print(f"[build_all] cannot run {label}: {e}", flush=True)
    if rc != 0:
        if fatal:
            print(f"[build_all] {label} failed (exit {rc}) — aborting.", flush=True)
            sys.exit(rc)
        print(f"[build_all] {label} failed (exit {rc}) — continuing with fallback.",
              flush=True)
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="One-command job-treemap build.")
    ap.add_argument("--fast", action="store_true",
                    help="build.py only — skip the LLM copy and the maps")
    ap.add_argument("--no-maps", action="store_true",
                    help="skip the Playwright map shots and the second build")
    ap.add_argument("--force-content", action="store_true",
                    help="regenerate summaries + longform even if cached")
    args = ap.parse_args()

    build_cmd = [PY, os.path.join("job-treemap", "build.py")]

    # 1 & 2 — LLM copy (cached, best-effort). Skipped in --fast.
    if not args.fast:
        force = ["--force"] if args.force_content else []
        run([PY, "-m", "scripts.build_treemap_summaries", *force],
            "summaries (LLM, cached)")
        run([PY, "-m", "scripts.build_treemap_longform", *force],
            "longform (LLM, cached)")

    # 3 — first build (fatal). Produces the /embed pages the shooter loads.
    run(build_cmd, "build site (pass 1)", fatal=True)

    # 4 & 5 — static maps, then a second build so the fresh PNGs land in og/schema.
    if not args.fast and not args.no_maps:
        if run(["node", os.path.join("scripts", "shoot_maps.mjs")],
               "static maps (Playwright)"):
            run(build_cmd, "build site (pass 2 - maps in og/schema)", fatal=True)
        else:
            print("[build_all] maps skipped — dist/ from pass 1 is complete "
                  "(og falls back to og-image.png where a PNG is missing).", flush=True)

    # 6 — country PDF reports. build_reports.py is deterministic (assembles HTML
    #     + landing, embedding the maps from step 4); shoot_reports.mjs prints
    #     them to real-text PDFs via Playwright (best-effort, like the maps).
    if not args.fast:
        if run([PY, os.path.join("job-treemap", "build_reports.py")],
               "country reports (HTML + landing)"):
            if not args.no_maps:
                run(["node", os.path.join("scripts", "shoot_reports.mjs")],
                    "country reports (PDF, Playwright)")

    print("\n===== done =====", flush=True)


if __name__ == "__main__":
    main()
