#!/usr/bin/env bash
# nginx 日志按天切割 + 过期清理（aaPanel / 宝塔布局）
#
# 为什么不能只 mv：nginx 持有日志文件的 fd，文件被移走后它仍往旧 inode 写，
# 新建的 access.log 会一直是 0 字节。必须在 mv 之后给 nginx 发 USR1（reopen），
# 等它切到新 fd，再压缩旧文件。本脚本按这个顺序执行。
#
# 用法：
#   ./nginx-log-rotate.sh                     # 按默认切割 + 清理
#   ./nginx-log-rotate.sh --dry-run           # 只打印会做什么，不动文件
#   ./nginx-log-rotate.sh --keep 60           # 保留 60 天
#   ./nginx-log-rotate.sh --log-dir /www/wwwlogs --archive-dir /www/wwwlogs/rotated
#
# 退出码：0 成功；1 参数/环境错误；2 nginx reopen 失败（日志已移走，需人工介入）

set -euo pipefail

LOG_DIR="${LOG_DIR:-/www/wwwlogs}"
ARCHIVE_DIR="${ARCHIVE_DIR:-/www/wwwlogs/rotated}"
KEEP_DAYS="${KEEP_DAYS:-30}"
NGINX_BIN="${NGINX_BIN:-/www/server/nginx/sbin/nginx}"
NGINX_PID="${NGINX_PID:-/www/server/nginx/logs/nginx.pid}"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)     DRY_RUN=1; shift ;;
    --keep)        KEEP_DAYS="${2:?--keep 需要天数}"; shift 2 ;;
    --log-dir)     LOG_DIR="${2:?--log-dir 需要路径}"; shift 2 ;;
    --archive-dir) ARCHIVE_DIR="${2:?--archive-dir 需要路径}"; shift 2 ;;
    -h|--help)     sed -n '2,14p' "$0"; exit 0 ;;
    *)             echo "未知参数：$1（试试 --help）" >&2; exit 1 ;;
  esac
done

case "$KEEP_DAYS" in
  ''|*[!0-9]*) echo "--keep 必须是非负整数，收到：$KEEP_DAYS" >&2; exit 1 ;;
esac
[ -d "$LOG_DIR" ] || { echo "日志目录不存在：$LOG_DIR" >&2; exit 1; }

STAMP="$(date +%Y%m%d)"
say() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
run() { if [ "$DRY_RUN" = 1 ]; then say "DRY-RUN: $*"; else "$@"; fi; }

say "开始：log-dir=$LOG_DIR archive=$ARCHIVE_DIR keep=${KEEP_DAYS}d dry-run=$DRY_RUN"
run mkdir -p "$ARCHIVE_DIR"

# ---------- 1) 切割 ----------
# 只处理 $LOG_DIR 一层内的 *.log。已归档的文件在 $ARCHIVE_DIR，不会被重复扫到。
rotated=0
while IFS= read -r -d '' src; do
  base="$(basename "$src" .log)"
  dst="$ARCHIVE_DIR/${base}-${STAMP}.log"

  if [ ! -s "$src" ]; then
    say "跳过空日志：$src"
    continue
  fi
  # 同一天重复运行时不覆盖已归档的文件（幂等）。
  if [ -e "$dst" ] || [ -e "$dst.gz" ]; then
    say "跳过（今天已切割过）：$(basename "$dst")"
    continue
  fi

  say "切割：$src -> $dst"
  run mv "$src" "$dst"
  rotated=$((rotated + 1))
done < <(find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -print0)

# ---------- 2) 让 nginx 重开日志 ----------
# 必须在 mv 之后、gzip 之前。三种方式依次尝试，全失败则退出码 2——
# 此时日志已经被移走但 nginx 还在写旧 fd，属于需要人工介入的状态。
reopen_nginx() {
  if [ -r "$NGINX_PID" ]; then
    pid="$(cat "$NGINX_PID" 2>/dev/null || true)"
    if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
      say "nginx reopen：kill -USR1 $pid"
      run kill -USR1 "$pid" && return 0
    fi
  fi
  if [ -x "$NGINX_BIN" ]; then
    say "nginx reopen：$NGINX_BIN -s reopen"
    run "$NGINX_BIN" -s reopen && return 0
  fi
  if command -v systemctl >/dev/null 2>&1; then
    say "nginx reopen：systemctl reload nginx"
    run systemctl reload nginx && return 0
  fi
  return 1
}

if [ "$rotated" -gt 0 ]; then
  if ! reopen_nginx; then
    echo "!! nginx reopen 失败：日志已移到 $ARCHIVE_DIR，但 nginx 仍在写旧 fd。" >&2
    echo "!! 请手动执行 nginx -s reopen（或重启 nginx），否则新日志不会落盘。" >&2
    exit 2
  fi
  # 给 nginx 一点时间切到新 fd，再压缩，避免压到还在被写的文件。
  [ "$DRY_RUN" = 1 ] || sleep 2
else
  say "没有需要切割的日志，跳过 reopen"
fi

# ---------- 3) 压缩 ----------
# dry-run 时归档目录可能还不存在，先判断，免得 find 报错刷屏。
if [ -d "$ARCHIVE_DIR" ]; then
  while IFS= read -r -d '' f; do
    say "压缩：$(basename "$f")"
    run gzip -9 "$f"
  done < <(find "$ARCHIVE_DIR" -maxdepth 1 -type f -name '*.log' -print0)
fi

# ---------- 4) 清理过期 ----------
# 收紧作用域：只在归档目录一层内、只删普通文件、只删本脚本产出的命名格式。
# 不加 -delete 直接跑通配符，避免 LOG_DIR 被误设成别的目录时造成范围外删除。
if [ "$KEEP_DAYS" -gt 0 ] && [ -d "$ARCHIVE_DIR" ]; then
  deleted=0
  while IFS= read -r -d '' old; do
    say "删除过期（>${KEEP_DAYS}d）：$(basename "$old")"
    run rm -f -- "$old"
    deleted=$((deleted + 1))
  done < <(find "$ARCHIVE_DIR" -maxdepth 1 -type f -name '*-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].log.gz' \
             -mtime +"$KEEP_DAYS" -print0)
  say "清理完成：删除 $deleted 个归档"
else
  say "跳过清理（KEEP_DAYS=0 或归档目录尚不存在）"
fi

say "完成：本次切割 $rotated 个日志"
