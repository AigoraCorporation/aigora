#!/usr/bin/env bash
# grpcurl smoke tests for the Curriculum Graph gRPC API (ADR-007, RQ-5).
#
# Runs grpcurl in a container attached to the compose network, so the only
# host requirement is Docker. Assumes `docker compose up -d --build` is running
# with the canonical graph (data/graph/canonical/graph.json) published.
#
# Usage: scripts/smoke_grpc_api.sh
# Env:   COMPOSE_NETWORK (default aigora_default), API_TARGET (default curriculum-graph-api:50051)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NETWORK="${COMPOSE_NETWORK:-aigora_default}"
TARGET="${API_TARGET:-curriculum-graph-api:50051}"
GRPCURL_IMAGE="fullstorydev/grpcurl:v1.9.1"
SERVICE="aigora.curriculum_graph.v1.CurriculumGraphService"
PROTO="aigora/curriculum_graph/v1/curriculum_graph.proto"

pass=0
fail=0

grpc() {  # grpc <method> <json-body>
  docker run --rm --network "$NETWORK" -v "$ROOT/proto:/proto:ro" "$GRPCURL_IMAGE" \
    -plaintext -import-path /proto -proto "$PROTO" -d "$2" "$TARGET" "$SERVICE/$1" 2>&1
}

check() {  # check <name> <method> <json-body> <expected-substring>...
  local name="$1" method="$2" body="$3"
  shift 3
  local output
  output="$(grpc "$method" "$body" || true)"
  for expected in "$@"; do
    if ! grep -qF -- "$expected" <<<"$output"; then
      echo "FAIL  $name: expected '$expected'"
      echo "$output" | sed 's/^/      /'
      fail=$((fail + 1))
      return
    fi
  done
  echo "PASS  $name"
  pass=$((pass + 1))
}

check "HealthCheck is SERVING" HealthCheck '{}' \
  '"status": "SERVING_STATUS_SERVING"' '"graphVersion": "0.2.0"'
check "GetGraphMetadata" GetGraphMetadata '{}' \
  '"graphVersion": "0.2.0"' '"nodeCount": 2' '"edgeCount": 1' '"profile.sat-math"'
check "GetNode (valid id)" GetNode '{"node_id": "math.arithmetic.fractions"}' \
  '"id": "math.arithmetic.fractions"' '"name": "Fractions"' '"MASTERY_LEVEL_RECOGNISES"'
check "GetNode (unknown id)" GetNode '{"node_id": "math.unknown", "context": {"request_id": "smoke-1"}}' \
  'Code: NotFound' 'Node not found'
check "ListNodes" ListNodes '{"page_size": 10}' \
  '"math.algebra.linear-equations"' '"math.arithmetic.fractions"' '"totalSize": 2'
check "GetPrerequisites" GetPrerequisites '{"node_id": "math.algebra.linear-equations"}' \
  '"id": "math.arithmetic.fractions"' '"kind": "PREREQUISITE_KIND_HARD"'
check "GetRegressionTargets (empty, versioned)" GetRegressionTargets '{"node_id": "math.arithmetic.fractions"}' \
  '"graphVersion": "0.2.0"'
check "GetLearningPath" GetLearningPath \
  '{"start_node_id": "math.arithmetic.fractions", "target_node_id": "math.algebra.linear-equations"}' \
  '"pathFound": true' '"id": "math.algebra.linear-equations"'
check "Invalid version selector" GetNode \
  '{"node_id": "math.arithmetic.fractions", "context": {"graph_version": "9.9.9"}}' \
  'Code: FailedPrecondition'
check "Invalid request" GetNode '{"node_id": ""}' 'Code: InvalidArgument'

echo
echo "smoke tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
