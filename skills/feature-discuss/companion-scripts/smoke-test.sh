#!/usr/bin/env bash
# Smoke test for the brainstorm companion HTTP surface.
#
# Standalone dev tool — NOT a plugin dependency and NOT a test framework.
# Requires only `node` and `curl`. Starts server.cjs on a random loopback port
# with a fixed token, exercises the critical runtime behaviours flagged in the
# major-v5 review, then kills the server. Exits non-zero on any FAIL.
#
# Scope is deliberately limited to HTTP. NOT covered here (manual TODO):
#   - WebSocket Origin enforcement (isAllowedWebSocketOrigin)
#   - bootstrap-after-compact / session resume
#   - idle-timeout / owner-death lifecycle
# Do not read a green run as full runtime coverage.
#
# Usage: bash smoke-test.sh

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER="$SCRIPT_DIR/server.cjs"

TOKEN="0123456789abcdef0123456789abcdef"
PORT=$(( 49152 + (RANDOM % 16000) ))
TMP="$(mktemp -d)"
mkdir -p "$TMP/content" "$TMP/state"

fail_count=0
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; fail_count=$((fail_count + 1)); }

cleanup() {
  if [[ -n "${SRV_PID:-}" ]]; then
    kill "$SRV_PID" 2>/dev/null
    wait "$SRV_PID" 2>/dev/null   # reap quietly, no job-control "Terminated" noise
  fi
  rm -rf "$TMP"
}
trap cleanup EXIT

BRAINSTORM_DIR="$TMP" BRAINSTORM_HOST=127.0.0.1 BRAINSTORM_PORT="$PORT" \
  BRAINSTORM_TOKEN="$TOKEN" node "$SERVER" >"$TMP/log" 2>&1 &
SRV_PID=$!

# Wait for the server to announce it bound.
for _ in $(seq 1 50); do
  grep -q 'server-started' "$TMP/log" 2>/dev/null && break
  kill -0 "$SRV_PID" 2>/dev/null || { echo "FAIL: server died on startup"; cat "$TMP/log"; exit 1; }
  sleep 0.1
done

BASE="http://127.0.0.1:$PORT"
COOKIE="brainstorm-key-$PORT=$TOKEN"

# (1) GET / without a valid token → 403 (server.cjs isAuthorized gate).
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/")
[[ "$code" == "403" ]] && pass "unauth GET / → 403" || fail "unauth GET / → expected 403, got $code"

# (2) GET / with a valid token → 200 (waiting page, no screens yet).
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Cookie: $COOKIE" "$BASE/")
[[ "$code" == "200" ]] && pass "auth GET / → 200" || fail "auth GET / → expected 200, got $code"

# (3) Path traversal → 404 (path.basename + regular-file guard).
code=$(curl -s -o /dev/null -w '%{http_code}' -H "Cookie: $COOKIE" "$BASE/files/../etc/passwd")
[[ "$code" == "404" ]] && pass "traversal /files/../etc/passwd → 404" || fail "traversal → expected 404, got $code"

# (4) Response CSP carries default-src 'none' and a script-src nonce.
csp=$(curl -s -D - -o /dev/null -H "Cookie: $COOKIE" "$BASE/" | tr -d '\r' | grep -i '^content-security-policy:')
if grep -q "default-src 'none'" <<<"$csp" && grep -q "script-src 'nonce-" <<<"$csp"; then
  pass "CSP has default-src 'none' + script-src 'nonce-"
else
  fail "CSP missing default-src 'none' or script-src 'nonce- (got: $csp)"
fi

# (5) Bonus: a screen with active content is rejected, not rendered verbatim.
printf '<h2>x</h2><script>alert(1)</script>' > "$TMP/content/evil.html"
sleep 0.3
body=$(curl -s -H "Cookie: $COOKIE" "$BASE/")
if grep -q 'Screen blocked' <<<"$body" && ! grep -q 'alert(1)' <<<"$body"; then
  pass "active-content screen rejected (no alert(1) leak)"
else
  fail "active-content screen NOT rejected (leak or missing block page)"
fi

echo "---"
if [[ "$fail_count" -eq 0 ]]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "$fail_count CHECK(S) FAILED"
  exit 1
fi
