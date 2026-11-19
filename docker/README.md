# Docker

Container definitions for local development and integration.

| Path | Purpose |
|------|---------|
| [`../docker-compose.yml`](../docker-compose.yml) | Local runtime: `neo4j` + one-shot `graph-publisher` + `curriculum-graph-api` (gRPC on `50051`) |
| [`curriculum-graph-api/Dockerfile`](curriculum-graph-api/Dockerfile) | Image for the Curriculum Graph gRPC API and the graph publisher |
| [`neo4j/`](neo4j/) | Standalone Neo4j for running publication or integration tests from the host |

Start the full runtime from the repository root:

```bash
docker compose up -d --build
docker compose ps        # neo4j and curriculum-graph-api report "healthy"
```

Startup order is health-gated: Neo4j must be healthy before the publisher runs,
and the API starts after the publisher completes. The API image's health check
calls the `HealthCheck` RPC and passes only when it reports `SERVING`.

See the [local validation playbook](../docs/06-engineering/workflow/curriculum-graph-grpc-local-validation.md)
for smoke tests with `grpcurl` and troubleshooting.
