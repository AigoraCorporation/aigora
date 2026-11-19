# Protobuf Contracts

Versioned gRPC contracts. Each package directory (`<component>/vN/`) is a
compatibility boundary: inside a version only additive changes are allowed
(see [ADR-007](../docs/02-architecture/curriculum-graph/adr/ADR-007-read-only-grpc-api-foundation.md)).

| Contract | Package | Generated Python | Reference |
|----------|---------|------------------|-----------|
| [`aigora/curriculum_graph/v1/curriculum_graph.proto`](aigora/curriculum_graph/v1/curriculum_graph.proto) | `aigora.curriculum_graph.v1` | `src/aigora/curriculum_graph/v1/` | [API reference](../docs/02-architecture/curriculum-graph/grpc-api-reference.md) |

## Workflow

```bash
pip install -e ".[dev]"                     # grpcio-tools is a dev dependency

python scripts/grpc_contracts.py generate   # regenerate code, reference docs and lock
python scripts/grpc_contracts.py check      # verify everything is in sync and compatible
```

- **Generated code** (`*_pb2.py`, `*_pb2.pyi`, `*_pb2_grpc.py`) is committed so the
  package runs without `protoc`. Never edit it by hand.
- **`contract.lock.json`** records the shape of the contract (RPC signatures,
  field numbers, types, labels, enum values). `generate` refuses to update it
  when a change is breaking; `check` fails on breaking changes, stale code,
  stale docs or a stale lock.
- **Reference docs** are generated from the `.proto` comments. Document every
  RPC, message and field in the `.proto`, not in the generated Markdown.
- CI runs `check` on every pull request that touches contracts
  (`.github/workflows/grpc-contracts.yml`).

## Making a change

1. Edit the `.proto` additively (new RPCs, new fields with new numbers, new enum values).
2. Run `generate` and commit the `.proto`, generated code, lock and reference doc together.
3. If `generate` reports `[BREAKING]`, the change belongs in a new `vN+1` package.

Java consumers (Tutor Orchestrator) generate their own stubs from the same
`.proto` (`java_package = com.aigora.curriculumgraph.v1`).
