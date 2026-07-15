#!/usr/bin/env bash
set -euo pipefail

HOST=""
USER_NAME=""
REMOTE_ROOT="/var/www/career-guides"
LOCAL_DIST="site/dist"
METHOD="rsync"
PORT="22"
IDENTITY_FILE=""
KEEP_RELEASES="3"
RELEASE_NAME="$(date +%Y%m%d-%H%M%S)"
DRY_RUN="0"

usage() {
  cat <<'EOF'
Deploy a locally built Astro dist directory over SSH without touching the live
directory until upload succeeds.

Examples:
  scripts/deploy_dist.sh --host example.com --user deploy
  scripts/deploy_dist.sh --host example.com --user deploy --remote-root /srv/career-guides
  scripts/deploy_dist.sh --host example.com --user deploy --method scp --identity-file ~/.ssh/id_ed25519

Expected server layout:
  /var/www/career-guides/
    current -> releases/20260713-153000
    releases/
      20260713-153000/

Point nginx root at:
  /var/www/career-guides/current

Options:
  --host            SSH host or IP. Required.
  --user            SSH username. Required.
  --remote-root     Remote deploy root. Default: /var/www/career-guides
  --local-dist      Local dist path. Default: site/dist
  --method          rsync or scp. Default: rsync
  --port            SSH port. Default: 22
  --identity-file   Optional private key path.
  --keep-releases   Number of old releases to keep. Default: 3
  --release-name    Optional release folder name. Default: yyyyMMdd-HHmmss
  --dry-run         Print commands without running them.
  -h, --help        Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --user) USER_NAME="$2"; shift 2 ;;
    --remote-root) REMOTE_ROOT="$2"; shift 2 ;;
    --local-dist) LOCAL_DIST="$2"; shift 2 ;;
    --method) METHOD="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --identity-file) IDENTITY_FILE="$2"; shift 2 ;;
    --keep-releases) KEEP_RELEASES="$2"; shift 2 ;;
    --release-name) RELEASE_NAME="$2"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$HOST" || -z "$USER_NAME" ]]; then
  usage
  echo "host and user are required." >&2
  exit 1
fi

if [[ "$METHOD" != "rsync" && "$METHOD" != "scp" ]]; then
  echo "method must be rsync or scp." >&2
  exit 1
fi

if [[ ! -d "$LOCAL_DIST" ]]; then
  echo "Local dist directory not found: $LOCAL_DIST" >&2
  exit 1
fi

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

quote_remote() {
  printf "'%s'" "$(printf "%s" "$1" | sed "s/'/'\\\\''/g")"
}

run_cmd() {
  printf '\n> '
  printf '%q ' "$@"
  printf '\n'
  if [[ "$DRY_RUN" == "0" ]]; then
    "$@"
  fi
}

require_tool ssh
if [[ "$METHOD" == "rsync" ]]; then
  require_tool rsync
else
  require_tool scp
fi

REMOTE="${USER_NAME}@${HOST}"
RELEASE_DIR="${REMOTE_ROOT}/releases/${RELEASE_NAME}"
CURRENT_LINK="${REMOTE_ROOT}/current"
NEXT_LINK="${REMOTE_ROOT}/current.next"

SSH_ARGS=(-p "$PORT")
SCP_ARGS=(-P "$PORT")
if [[ -n "$IDENTITY_FILE" ]]; then
  SSH_ARGS+=(-i "$IDENTITY_FILE")
  SCP_ARGS+=(-i "$IDENTITY_FILE")
fi

SSH_TRANSPORT="ssh -p $PORT"
if [[ -n "$IDENTITY_FILE" ]]; then
  SSH_TRANSPORT+=" -i $IDENTITY_FILE"
fi

REMOTE_PREPARE="set -e
mkdir -p $(quote_remote "$RELEASE_DIR")
"
run_cmd ssh "${SSH_ARGS[@]}" "$REMOTE" "$REMOTE_PREPARE"

if [[ "$METHOD" == "rsync" ]]; then
  run_cmd rsync -az --delete --info=progress2 -e "$SSH_TRANSPORT" "${LOCAL_DIST%/}/" "${REMOTE}:${RELEASE_DIR}/"
else
  echo "Warning: scp fallback uploads all files every time. For an 8GB dist, rsync is much faster after the first deploy." >&2
  run_cmd scp "${SCP_ARGS[@]}" -r "${LOCAL_DIST%/}/." "${REMOTE}:${RELEASE_DIR}/"
fi

REMOTE_SWITCH="set -e
test -f $(quote_remote "$RELEASE_DIR/index.html")
ln -sfn $(quote_remote "$RELEASE_DIR") $(quote_remote "$NEXT_LINK")
mv -Tf $(quote_remote "$NEXT_LINK") $(quote_remote "$CURRENT_LINK")
find $(quote_remote "$REMOTE_ROOT/releases") -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -rn | tail -n +$((KEEP_RELEASES + 1)) | cut -d' ' -f2- | xargs -r rm -rf
echo \"Activated $RELEASE_DIR\"
"
run_cmd ssh "${SSH_ARGS[@]}" "$REMOTE" "$REMOTE_SWITCH"

echo
echo "Deploy complete."
echo "Live symlink: $CURRENT_LINK -> $RELEASE_DIR"
