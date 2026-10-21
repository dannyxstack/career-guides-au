#!/usr/bin/env bash
# 服务器端博客同步：拉取 GitHub Actions 自动发布的文章，热重载到运行中的站点。
#
# 设计：用一个**独立的稀疏镜像**（只检出 aijobrisk-go/data/blog 与 static/blog），
# Go 通过 AIJOBRISK_BLOG_DIR / AIJOBRISK_BLOG_STATIC_DIR 直接读镜像。线上代码目录完全不碰——
#   - 不会把新模板/Go 源码拉到正在运行的目录里（进程一旦重启就会变成「旧二进制 + 新模板」）
#   - 不会往线上仓库里被跟踪的 data/blog 写文件（否则你下次在线上 git pull 会冲突）
#
# 用法：
#   blog-pull.sh --init git@github.com:OWNER/REPO.git   # 一次性：建镜像
#   blog-pull.sh                                        # 日常（cron）：有新提交才同步 + 重载
#   blog-pull.sh --dry-run                              # 只看会做什么
#   blog-pull.sh --force                                # 跳过防误删检查 / 无新提交也重载
#
# 退出码：0 成功或无事可做｜1 环境/配置错误｜2 已同步但重载失败（需重启服务）｜
#         4 防误删检查拒绝（新 index 的文章数骤降）

set -euo pipefail

MIRROR="${MIRROR:-/opt/aijobrisk-blog-mirror}"
BRANCH="${BRANCH:-main}"
RELOAD_URL="${RELOAD_URL:-http://127.0.0.1:4332/internal/reload-blog}"
ENV_FILE="${ENV_FILE:-/opt/career-guides-au/aijobrisk-go/.env}"
MIN_KEEP_PCT="${MIN_KEEP_PCT:-50}"   # 新 index 文章数低于现有的 50% 视为异常（误删 / 坏提交）
PATHS=(aijobrisk-go/data/blog aijobrisk-go/static/blog)
INDEX=aijobrisk-go/data/blog/index.json
MARK="$MIRROR/.git/aijobrisk-blog-mirror"

say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
die() { code="$1"; shift; echo "ERROR: $*" >&2; exit "$code"; }

DRY=0; FORCE=0; INIT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --init)    INIT="${2:?--init 需要仓库地址}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --force)   FORCE=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *)         die 1 "未知参数：$1" ;;
  esac
done

command -v git >/dev/null || die 1 "需要 git"
command -v python3 >/dev/null || die 1 "需要 python3（防误删检查要解析 index.json）"

# ---------- 一次性初始化 ----------
if [ -n "$INIT" ]; then
  [ -e "$MIRROR" ] && die 1 "$MIRROR 已存在；要重建请先手动删除"
  say "克隆稀疏镜像 -> $MIRROR"
  git clone --quiet --depth=1 --filter=blob:none --sparse --branch "$BRANCH" "$INIT" "$MIRROR"
  git -C "$MIRROR" sparse-checkout set "${PATHS[@]}"
  touch "$MARK"   # 标记：本脚本只会对带标记的目录执行 reset --hard
  say "完成。请在 $ENV_FILE 加入（然后重启一次服务）："
  echo "    AIJOBRISK_BLOG_DIR=$MIRROR/aijobrisk-go/data/blog"
  echo "    AIJOBRISK_BLOG_STATIC_DIR=$MIRROR/aijobrisk-go/static/blog"
  echo "    AIJOBRISK_RELOAD_TOKEN=$(head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')"
  exit 0
fi

# ---------- 日常同步 ----------
# 只对本脚本建的镜像 reset --hard，避免误指到线上代码仓库时抹掉本地改动。
[ -f "$MARK" ] || die 1 "$MIRROR 不是博客镜像（缺 $MARK）。先运行：$0 --init <仓库地址>"

git -C "$MIRROR" fetch --quiet --depth=1 origin "$BRANCH"
old="$(git -C "$MIRROR" rev-parse HEAD)"
new="$(git -C "$MIRROR" rev-parse FETCH_HEAD)"

if [ "$old" = "$new" ] && [ "$FORCE" = 0 ]; then
  exit 0   # 无新提交，静默退出（cron 每 10 分钟跑，不刷日志）
fi

count_posts() {   # 从某个提交里数 index.json 的文章数；读不到/坏 JSON 返回非零
  git -C "$MIRROR" show "$1:$INDEX" 2>/dev/null \
    | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("posts", [])))'
}
newn="$(count_posts "$new")" || die 4 "新提交 ${new:0:8} 的 index.json 缺失或不是合法 JSON，拒绝同步"
oldn="$(count_posts "$old" || echo 0)"
say "新提交 ${old:0:8} -> ${new:0:8}：index.json 文章数 $oldn -> $newn"

if [ "$FORCE" = 0 ] && [ "$oldn" -gt 0 ] && [ $((newn * 100)) -lt $((oldn * MIN_KEEP_PCT)) ]; then
  die 4 "文章数骤降（$oldn -> $newn，低于 ${MIN_KEEP_PCT}%），疑似误删或坏提交，拒绝同步。确认无误后用 --force"
fi

if [ "$DRY" = 1 ]; then
  say "DRY-RUN：会 reset 到 ${new:0:8} 并调用重载接口"
  exit 0
fi

git -C "$MIRROR" reset --quiet --hard FETCH_HEAD
say "镜像已更新到 ${new:0:8}"

# ---------- 通知进程热重载 ----------
token="${AIJOBRISK_RELOAD_TOKEN:-}"
if [ -z "$token" ] && [ -r "$ENV_FILE" ]; then
  token="$(grep -E '^AIJOBRISK_RELOAD_TOKEN=' "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d "\"'" || true)"
fi
[ -n "$token" ] || die 2 "没有 AIJOBRISK_RELOAD_TOKEN（$ENV_FILE）。文件已同步，但需重启服务才会生效"

# --noproxy：服务器若设了 http_proxy，curl 会把 127.0.0.1 也送去代理。
if out="$(curl -fsS --noproxy '*' -m 15 -X POST -H "X-Reload-Token: $token" "$RELOAD_URL" 2>&1)"; then
  say "重载成功：$out"
else
  die 2 "重载接口调用失败：$out
  文件已同步到镜像，但运行中的进程还没读到。可能原因：服务还是旧二进制（接口不存在会 404）、
  token 不一致、或服务未运行。处理：确认新二进制已部署，然后 systemctl restart aijobrisk-go"
fi
