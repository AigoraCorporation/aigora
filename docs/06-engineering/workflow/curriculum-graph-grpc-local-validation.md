# Curriculum Graph gRPC API — Local Validation Playbook

This playbook validates the Curriculum Graph gRPC API end to end from a clean
checkout: Neo4j, graph publication and the API, all in Docker
([ADR-007](../../02-architecture/curriculum-graph/adr/ADR-007-read-only-grpc-api-foundation.md), RQ-5).

**Requirement:** Docker with Compose v2. Nothing else is installed on the host;
`grpcurl` runs in a container.

---

## 1. Start

From the repository root:

```bash
cp .env.example .env            # optional: override ports, credentials, versions
docker compose up -d --build
```

Startup is health-gated:

| Step | Service | Done when |
|------|---------|-----------|
| 1 | `neo4j` | `cypher-shell 'RETURN 1'` succeeds → `healthy` |
| 2 | `graph-publisher` | Publishes `data/graph/canonical/graph.json` and exits `0` |
| 3 | `curriculum-graph-api` | `HealthCheck` returns `SERVING` → `healthy` |

## 2. Check readiness

```bash
docker compose ps
```

Expected: `neo4j` and `curriculum-graph-api` show `(healthy)`;
`graph-publisher` shows `Exited (0)`.

```bash
docker compose logs graph-publisher | tail -1
```

Expected: a JSON line with `"event": "graph_published"` and
`"graph_version": "0.2.0"`.

## 3. Smoke tests

Run all checks:

```bash
scripts/smoke_grpc_api.sh
```

Expected last line: `smoke tests: 10 passed, 0 failed`.

The script wraps `grpcurl` like this (use it for ad-hoc calls):

```bash
docker run --rm --network aigora_default -v "$PWD/proto:/proto:ro" fullstorydev/grpcurl:v1.9.1 \
  -plaintext -import-path /proto -proto aigora/curriculum_graph/v1/curriculum_graph.proto \
  -d '{}' curriculum-graph-api:50051 aigora.curriculum_graph.v1.CurriculumGraphService/HealthCheck
```

With `grpcurl` installed on the host, target the published port instead:

```bash
grpcurl -plaintext -import-path proto -proto aigora/curriculum_graph/v1/curriculum_graph.proto \
  -d '{"node_id": "math.arithmetic.fractions"}' \
  localhost:50051 aigora.curriculum_graph.v1.CurriculumGraphService/GetNode
```

### Expected results (canonical graph `0.2.0`)

| Check | Request | Expected |
|-------|---------|----------|
| Health | `HealthCheck {}` | `SERVING_STATUS_SERVING`, `graphVersion: "0.2.0"` |
| Metadata | `GetGraphMetadata {}` | `nodeCount: 2`, `edgeCount: 1`, `profileIds: ["profile.sat-math"]` |
| Valid node | `GetNode {"node_id": "math.arithmetic.fractions"}` | `name: "Fractions"`, mastery levels `RECOGNISES`, `INDEPENDENT` |
| Unknown node | `GetNode {"node_id": "math.unknown"}` | `Code: NotFound` (`CG_NODE_NOT_FOUND`) |
| Listing | `ListNodes {"page_size": 10}` | both concepts, `totalSize: 2` |
| Prerequisites | `GetPrerequisites {"node_id": "math.algebra.linear-equations"}` | `math.arithmetic.fractions`, `PREREQUISITE_KIND_HARD` |
| Regression (empty) | `GetRegressionTargets {"node_id": "math.arithmetic.fractions"}` | no targets, `graphVersion: "0.2.0"` |
| Path | `GetLearningPath` fractions → linear-equations | `pathFound: true`, two nodes |
| Version mismatch | `GetNode` with `context.graph_version: "9.9.9"` | `Code: FailedPrecondition` (`CG_INVALID_GRAPH_VERSION`) |
| Invalid input | `GetNode {"node_id": ""}` | `Code: InvalidArgument` (`CG_INVALID_REQUEST`) |

`grpcurl` prints the status code and message. The canonical `ErrorDetail`
(`code`, `request_id`, `graph_version`) travels in the
`grpc-status-details-bin` trailer; see the
[contract](../../02-architecture/curriculum-graph/grpc-api-contract.md#error-model).

## 4. Publish another graph

```bash
GRAPH_PUBLISH_INPUT=data/graph/canonical/graph.yaml docker compose up -d --force-recreate graph-publisher
docker compose restart curriculum-graph-api
```

The API loads the snapshot at startup, so restart it after publishing.

## 5. Stop

```bash
docker compose down        # keep Neo4j data
docker compose down -v     # also remove the Neo4j volume (clean state)
```

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `curriculum-graph-api` never starts | `graph-publisher` failed | `docker compose logs graph-publisher`; fix the graph file or credentials and `docker compose up -d` again |
| API `unhealthy`, logs show `graph_load_failed` | No published graph, or a graph published before v0.2.2 (missing properties) | Re-run the publisher (section 4); the API retries every `GRAPH_LOAD_RETRY_SECONDS` (default 5 s) |
| `graph_load_failed` with "does not match the required version" | `GRAPH_VERSION_DEFAULT` differs from the published version | Unset it or publish that version |
| `neo4j` stays `starting` | Slow first start or not enough memory | Wait; lower `NEO4J_HEAP_MAX` in `.env` |
| `Bind for 0.0.0.0:7687 failed: port is already allocated` | Another Neo4j (e.g. `docker/neo4j`) is running | Stop it or change `NEO4J_BOLT_PORT` / `NEO4J_HTTP_PORT` / `GRPC_PORT` in `.env` |
| Smoke script: `network aigora_default not found` | Compose project not running, or a different project name | `docker compose up -d`; or set `COMPOSE_NETWORK` |
| `Code: Unavailable` on every call | API running without a loaded snapshot | Check `docker compose logs curriculum-graph-api` for `graph_load_failed` and its `reason` |
| Authentication errors in publisher logs | `.env` credentials changed after the volume was created | `docker compose down -v` to recreate Neo4j with the new password |

Every API call is logged as one JSON `grpc_request` line with `request_id`,
`grpc_status`, `error_code`, `graph_version` and `latency_ms`:

```bash
docker compose logs -f curriculum-graph-api
```
