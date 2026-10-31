#!/usr/bin/env bash
# 本地同步 main：安全地拉取 GitHub 上的新提交（包括 GitHub Actions 博客 bot 每天的自动提交）。
#
# 和直接 git pull 的区别：
#   - 用 rebase 而不是 merge：本地未推送的提交会接到最新 main 后面，历史保持一条直线，
#     之后直接 git push 不会被拒，也不会多出 "Merge branch 'main'" 提交。
#   - 工作区有未提交的改动时自动暂存（autostash），拉完再放回来。
#   - 出冲突时自动回到拉取前的状态，不把仓库留在「rebase 进行到一半」的状态。
#   - 拉取前先检查：远端新增的文件如果和本地未跟踪文件同名，直接停下，不覆盖。
#
# 用法（Git Bash，仓库内任意目录）：
#   bash ops/pull.sh            # 拉取并 rebase
#   bash ops/pull.sh --dry-run  # 只看远端有哪些新提交，不改动本地
#
# 退出码：0 成功或已是最新｜1 环境问题（不在仓库、不在 main、有进行中的 rebase/merge、fetch 失败）｜
#         2 有冲突，已自动回滚到拉取前状态｜3 远端新文件会覆盖本地未跟踪文件，未拉取｜
#         4 已拉取，但你本地未提交的改动放回时有冲突，改动保存在 stash 里

set -uo pipefail

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
DRY=0

for a in "$@"; do
  case "$a" in
    --dry-run|-n) DRY=1 ;;
    -h|--help)    sed -n '2,20p' "$0"; exit 0 ;;
    *)            echo "未知参数：$a（试试 --help）" >&2; exit 1 ;;
  esac
done

die() { code="$1"; shift; echo; echo "✗ $*" >&2; exit "$code"; }
indent() { sed 's/^/  /'; }

root="$(git rev-parse --show-toplevel 2>/dev/null)" || die 1 "当前目录不在 git 仓库里"
cd "$root" || die 1 "无法进入 $root"
gitdir="$(git rev-parse --git-dir)"

if [ -d "$gitdir/rebase-merge" ] || [ -d "$gitdir/rebase-apply" ]; then
  die 1 "有一个进行中的 rebase。先处理完：git rebase --continue（解决冲突后）或 git rebase --abort"
fi
[ -f "$gitdir/MERGE_HEAD" ] && die 1 "有一个进行中的 merge。先处理完：git merge --continue 或 git merge --abort"

cur="$(git symbolic-ref --quiet --short HEAD)" || die 1 "当前是 detached HEAD，先 git switch $BRANCH"
[ "$cur" = "$BRANCH" ] || die 1 "当前在分支 $cur，这个脚本只同步 $BRANCH。先 git switch $BRANCH"

echo "→ 获取 $REMOTE/$BRANCH …"
git fetch --quiet "$REMOTE" "$BRANCH" || die 1 "fetch 失败（网络问题，或 SSH key 没加载？）"
up="$REMOTE/$BRANCH"

behind="$(git rev-list --count "HEAD..$up")"
ahead="$(git rev-list --count "$up..HEAD")"

if [ "$behind" -eq 0 ]; then
  echo "✓ 已是最新。"
  [ "$ahead" -gt 0 ] && echo "  本地领先 $ahead 个提交还没推送，可以 git push"
  exit 0
fi

# 远端在分叉点之后改了哪些文件（三点语法：只看远端那一侧）
incoming="$(git diff --name-only "HEAD...$up")"

echo
echo "远端有 $behind 个新提交："
git log --format='%h  %<(18,trunc)%an  %s' "HEAD..$up" | indent
echo
echo "涉及的目录："
printf '%s\n' "$incoming" | awk -F/ '{ print (NF > 2 ? $1"/"$2 : $0) }' | sort | uniq -c | sort -rn | sed 's/^ *//' | indent
[ "$ahead" -gt 0 ] && echo && echo "本地有 $ahead 个未推送的提交，会接到这些新提交后面。"

if [ "$DRY" = 1 ]; then
  echo
  echo "（--dry-run：没有改动本地）"
  exit 0
fi

# 远端新增的文件若与本地未跟踪文件同名，rebase 会失败；先查出来，不碰任何东西。
clash=()
while IFS= read -r f; do
  [ -n "$f" ] && [ -e "$f" ] && ! git ls-files --error-unmatch -- "$f" >/dev/null 2>&1 && clash+=("$f")
done < <(git diff --name-only --diff-filter=A "HEAD...$up")
if [ "${#clash[@]}" -gt 0 ]; then
  echo
  echo "这些文件远端新增了，本地也有同名的未跟踪文件："
  printf '%s\n' "${clash[@]}" | indent
  die 3 "没有拉取。先对比一下（多半内容相同，删掉本地的即可），或把它们移走，再运行一次。"
fi

stash_before="$(git stash list | wc -l)"
errlog="$(mktemp)"
trap 'rm -f "$errlog"' EXIT

echo
echo "→ rebase 到 $up …"
if ! git rebase --quiet --autostash "$up" 2>"$errlog"; then
  conflicted="$(git diff --name-only --diff-filter=U 2>/dev/null)"
  git rebase --abort >/dev/null 2>&1   # 回到拉取前（autostash 暂存的改动也会还原）
  echo
  if [ -n "$conflicted" ]; then
    echo "冲突的文件："
    printf '%s\n' "$conflicted" | indent
  else
    indent < "$errlog"
  fi
  die 2 "rebase 有冲突，已自动回滚，本地和拉取前完全一样。
  要手动处理：git pull --rebase，按提示解决冲突后 git rebase --continue"
fi

echo "✓ 已同步到 $(git log -1 --format='%h %s')"
ahead_now="$(git rev-list --count "$up..HEAD")"
[ "$ahead_now" -gt 0 ] && echo "  本地领先 $ahead_now 个提交还没推送，可以 git push"

if [ "$(git stash list | wc -l)" -gt "$stash_before" ]; then
  echo
  echo "⚠ 你本地未提交的改动和拉下来的内容冲突，没能自动放回，已安全保存在 stash 里："
  git stash list | head -1 | indent
  echo "  确认后用 git stash pop 取回，按提示解决冲突。"
  exit 4
fi

# 拉下来的内容是否需要额外动作
if printf '%s\n' "$incoming" | grep -q '^aijobrisk-go/.*\.go$'; then
  echo "  · Go 代码有更新：本地预览前重新 go run ."
fi
if printf '%s\n' "$incoming" | grep -qE '^(scripts/)?requirements\.txt$'; then
  echo "  · Python 依赖有更新：在 career-video 环境里重新 pip install -r requirements.txt"
fi
exit 0
