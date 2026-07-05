# -*- coding: utf-8 -*-
"""投票 API（自建，复用现有 MySQL）。通用投票引擎，定义来自 site/src/data/polls.json。

端点：
  GET  /api/polls?occ=<slug>&token=<client_token>
       → { polls: { <code>: { type, counts:{key:cnt}, total, avgPct, mine } } }
  POST /api/polls/vote   { poll_code, occ_key, answer_key, client_token, turnstile? }
       → { ok, poll: { counts, total, avgPct, mine } }
  GET  /api/health

无注册：一浏览器一票（client_token），可改票(upsert)；ip_hash 软去重+限流；Turnstile 可选。
occ_key = 职业 slug（跨国共享）。只操作 poll_* 三张表，建议给本服务用最小权限 DB 账号。

本地起：
  POLLS_CORS_ORIGINS=http://localhost:4399 \
  e:/run/conda_envs/career-video/python.exe -m uvicorn api.polls_api:app --port 8790
生产：见 docs/polls-deploy.md（nginx 子域 + TLS + 设 POLLS_TURNSTILE_SECRET/POLLS_IP_SALT）。
"""
import os, sys, json, time, re, hashlib, threading
from collections import defaultdict, deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.request
import urllib.parse

from db.connection import get_cursor

# ---- 载入投票定义（与前端同一份 polls.json）----
POLLS_PATH = os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "polls.json")
with open(POLLS_PATH, encoding="utf-8") as f:
    _defs = json.load(f)["polls"]
POLLS = {p["code"]: p for p in _defs}
OPTION_KEYS = {p["code"]: {o["key"] for o in p["options"]} for p in _defs}
OPTION_MID = {p["code"]: {o["key"]: o.get("mid") for o in p["options"]} for p in _defs}

IP_SALT = os.getenv("POLLS_IP_SALT", "change-me")
TURNSTILE_SECRET = os.getenv("POLLS_TURNSTILE_SECRET", "")  # 空=不校验(dev)
CORS = [o.strip() for o in os.getenv(
    "POLLS_CORS_ORIGINS", "http://localhost:4399,http://localhost:4321").split(",") if o.strip()]
RATE_MAX = int(os.getenv("POLLS_RATE_MAX", "20"))     # 每窗口最大写入
RATE_WINDOW = int(os.getenv("POLLS_RATE_WINDOW", "60"))  # 窗口秒

_TOKEN_RE = re.compile(r"^[a-f0-9]{32}$")
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{0,158}$")

app = FastAPI(title="AI Career Graph Polls API")
app.add_middleware(CORSMiddleware, allow_origins=CORS, allow_methods=["GET", "POST"],
                   allow_headers=["*"], max_age=86400)

# ---- 简单内存限流（单实例足够；多实例需换 Redis）----
_hits = defaultdict(deque)
_hits_lock = threading.Lock()


def _rate_ok(key: str) -> bool:
    now = time.time()
    with _hits_lock:
        dq = _hits[key]
        while dq and dq[0] < now - RATE_WINDOW:
            dq.popleft()
        if len(dq) >= RATE_MAX:
            return False
        dq.append(now)
        return True


def _ip_hash(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for", "")
    ip = xff.split(",")[0].strip() if xff else (req.client.host if req.client else "?")
    return hashlib.sha256((ip + IP_SALT).encode()).hexdigest()


def _verify_turnstile(token: str, ip_plain: str) -> bool:
    if not TURNSTILE_SECRET:
        return True  # 未配置密钥=开发模式跳过
    try:
        data = urllib.parse.urlencode({"secret": TURNSTILE_SECRET, "response": token or ""}).encode()
        req = urllib.request.Request(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data)
        with urllib.request.urlopen(req, timeout=5) as r:
            return bool(json.load(r).get("success"))
    except Exception:
        return False


def _counts(cur, poll_code: str, occ_key: str):
    cur.execute(
        "SELECT answer_key, COUNT(*) c FROM poll_votes "
        "WHERE poll_code=%s AND occ_key=%s AND answer_key IS NOT NULL GROUP BY answer_key",
        (poll_code, occ_key))
    return {r["answer_key"]: r["c"] for r in cur.fetchall()}


def _avg_pct(poll_code: str, counts: dict):
    mids = OPTION_MID.get(poll_code, {})
    n = s = 0
    for k, c in counts.items():
        m = mids.get(k)
        if m is None:
            return None
        n += c; s += c * m
    return round(s / n) if n else None


def _poll_view(cur, poll_code: str, occ_key: str, token: str | None):
    counts = _counts(cur, poll_code, occ_key)
    mine = None
    if token:
        cur.execute("SELECT answer_key FROM poll_votes WHERE poll_code=%s AND occ_key=%s AND client_token=%s",
                    (poll_code, occ_key, token))
        row = cur.fetchone()
        mine = row["answer_key"] if row else None
    return {"type": POLLS[poll_code]["type"], "counts": counts,
            "total": sum(counts.values()), "avgPct": _avg_pct(poll_code, counts), "mine": mine}


@app.get("/api/health")
def health():
    return {"ok": True, "polls": list(POLLS.keys())}


@app.get("/api/polls")
def get_polls(occ: str, token: str | None = None):
    occ = (occ or "").lower()
    if not _SLUG_RE.match(occ):
        raise HTTPException(400, "bad occ")
    if token and not _TOKEN_RE.match(token):
        token = None
    with get_cursor() as cur:
        return {"polls": {code: _poll_view(cur, code, occ, token) for code in POLLS}}


class VoteIn(BaseModel):
    poll_code: str
    occ_key: str
    answer_key: str
    client_token: str
    turnstile: str | None = None


@app.post("/api/polls/vote")
def vote(v: VoteIn, request: Request):
    if v.poll_code not in POLLS:
        raise HTTPException(400, "unknown poll")
    occ = (v.occ_key or "").lower()
    if not _SLUG_RE.match(occ):
        raise HTTPException(400, "bad occ_key")
    if not _TOKEN_RE.match(v.client_token or ""):
        raise HTTPException(400, "bad token")
    if v.answer_key not in OPTION_KEYS[v.poll_code]:
        raise HTTPException(400, "bad answer")

    iph = _ip_hash(request)
    if not _rate_ok(iph):
        raise HTTPException(429, "too many votes")
    xff = request.headers.get("x-forwarded-for", "")
    ip_plain = xff.split(",")[0].strip() if xff else (request.client.host if request.client else "")
    if not _verify_turnstile(v.turnstile or "", ip_plain):
        raise HTTPException(403, "turnstile failed")

    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO poll_votes (poll_code, occ_key, client_token, answer_key, ip_hash) "
            "VALUES (%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE answer_key=VALUES(answer_key), ip_hash=VALUES(ip_hash)",
            (v.poll_code, occ, v.client_token, v.answer_key, iph))
        # 重算该 (poll_code, occ_key) 的聚合（供构建期烘焙；GET 用实时票）
        cur.execute("DELETE FROM poll_agg WHERE poll_code=%s AND occ_key=%s", (v.poll_code, occ))
        cur.execute(
            "INSERT INTO poll_agg (poll_code, occ_key, answer_key, cnt) "
            "SELECT poll_code, occ_key, answer_key, COUNT(*) FROM poll_votes "
            "WHERE poll_code=%s AND occ_key=%s AND answer_key IS NOT NULL GROUP BY poll_code, occ_key, answer_key",
            (v.poll_code, occ))
        view = _poll_view(cur, v.poll_code, occ, v.client_token)
    return {"ok": True, "poll": view}
