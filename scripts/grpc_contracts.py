"""Code generation, reference docs and compatibility gate for gRPC contracts.

Usage (from the repository root):

    python scripts/grpc_contracts.py generate   # regenerate code, docs and lock
    python scripts/grpc_contracts.py check      # fail if anything is stale or breaking

`generate` refuses to update the contract lock when the change is breaking
(ADR-007: v1 is additive-only). `check` is what CI runs.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from google.protobuf import descriptor_pb2

ROOT = Path(__file__).resolve().parent.parent
PROTO_ROOT = ROOT / "proto"
OUT_ROOT = ROOT / "src"


@dataclass(frozen=True)
class Contract:
    """One versioned contract package (one .proto file)."""

    proto: str  # path relative to PROTO_ROOT
    lock: Path
    reference_doc: Path
    title: str

    @property
    def package_dir(self) -> str:
        return str(Path(self.proto).parent)


CONTRACTS = [
    Contract(
        proto="aigora/curriculum_graph/v1/curriculum_graph.proto",
        lock=PROTO_ROOT / "aigora/curriculum_graph/v1/contract.lock.json",
        reference_doc=ROOT / "docs/02-architecture/curriculum-graph/grpc-api-reference.md",
        title="Curriculum Graph gRPC API — v1 Reference",
    ),
]

GENERATED_SUFFIXES = ("_pb2.py", "_pb2.pyi", "_pb2_grpc.py")
INIT_TEXT = '"""Generated gRPC contract package. Do not edit; run scripts/grpc_contracts.py generate."""\n'


# ---------------------------------------------------------------------------
# protoc
# ---------------------------------------------------------------------------

def run_protoc(contract: Contract, out_dir: Path) -> descriptor_pb2.FileDescriptorSet:
    out_dir.mkdir(parents=True, exist_ok=True)
    descriptor_path = out_dir / "descriptor.binpb"
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{PROTO_ROOT}",
        f"--python_out={out_dir}",
        f"--pyi_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        f"--descriptor_set_out={descriptor_path}",
        "--include_source_info",
        str(PROTO_ROOT / contract.proto),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"protoc failed for {contract.proto}:\n{result.stderr}")
    descriptor_set = descriptor_pb2.FileDescriptorSet()
    descriptor_set.ParseFromString(descriptor_path.read_bytes())
    descriptor_path.unlink()
    pkg = out_dir / contract.package_dir
    (pkg / "__init__.py").write_text(INIT_TEXT)
    return descriptor_set


def generated_files(base: Path, contract: Contract) -> dict[str, str]:
    pkg = base / contract.package_dir
    files = {}
    for path in sorted(pkg.iterdir()) if pkg.exists() else []:
        if path.name == "__init__.py" or path.name.endswith(GENERATED_SUFFIXES):
            files[str(path.relative_to(base))] = path.read_text()
    return files


# ---------------------------------------------------------------------------
# Contract lock (shape used for compatibility checks)
# ---------------------------------------------------------------------------

def build_lock(fd: descriptor_pb2.FileDescriptorProto) -> dict:
    pkg = fd.package
    messages: dict[str, dict] = {}
    enums: dict[str, dict] = {}

    def add_enum(full: str, enum: descriptor_pb2.EnumDescriptorProto) -> None:
        enums[full] = {str(v.number): v.name for v in enum.value}

    def add_message(full: str, msg: descriptor_pb2.DescriptorProto) -> None:
        messages[full] = {
            "fields": {
                str(f.number): {
                    "name": f.name,
                    "type": descriptor_pb2.FieldDescriptorProto.Type.Name(f.type),
                    "type_name": f.type_name,
                    "label": descriptor_pb2.FieldDescriptorProto.Label.Name(f.label),
                    "proto3_optional": f.proto3_optional,
                }
                for f in msg.field
            },
            "reserved_numbers": sorted(n for r in msg.reserved_range for n in range(r.start, r.end)),
            "reserved_names": sorted(msg.reserved_name),
        }
        for nested in msg.nested_type:
            add_message(f"{full}.{nested.name}", nested)
        for enum in msg.enum_type:
            add_enum(f"{full}.{enum.name}", enum)

    for msg in fd.message_type:
        add_message(f".{pkg}.{msg.name}", msg)
    for enum in fd.enum_type:
        add_enum(f".{pkg}.{enum.name}", enum)
    services = {
        f".{pkg}.{svc.name}": {
            m.name: {
                "input": m.input_type,
                "output": m.output_type,
                "client_streaming": m.client_streaming,
                "server_streaming": m.server_streaming,
            }
            for m in svc.method
        }
        for svc in fd.service
    }
    return {"package": pkg, "services": services, "messages": messages, "enums": enums}


def breaking_changes(old: dict, new: dict) -> list[str]:
    """Return human-readable breaking changes from `old` to `new` (empty = compatible)."""
    problems: list[str] = []
    if old["package"] != new["package"]:
        problems.append(f"package changed: {old['package']} -> {new['package']}")

    for svc, methods in old["services"].items():
        if svc not in new["services"]:
            problems.append(f"service removed: {svc}")
            continue
        for name, sig in methods.items():
            cur = new["services"][svc].get(name)
            if cur is None:
                problems.append(f"rpc removed: {svc}.{name}")
            elif cur != sig:
                problems.append(f"rpc signature changed: {svc}.{name}: {sig} -> {cur}")

    for msg, spec in old["messages"].items():
        cur = new["messages"].get(msg)
        if cur is None:
            problems.append(f"message removed: {msg}")
            continue
        cur_names = {f["name"]: num for num, f in cur["fields"].items()}
        for num, field in spec["fields"].items():
            now = cur["fields"].get(num)
            if now is None:
                problems.append(f"field removed: {msg}.{field['name']} (= {num})")
            elif now != field:
                changed = {k: (field[k], now[k]) for k in field if field[k] != now[k]}
                problems.append(f"field changed: {msg}.{field['name']} (= {num}): {changed}")
            if field["name"] in cur_names and cur_names[field["name"]] != num:
                problems.append(f"field renumbered: {msg}.{field['name']} {num} -> {cur_names[field['name']]}")
        for num in spec["reserved_numbers"]:
            if str(num) in cur["fields"]:
                problems.append(f"reserved tag reused: {msg} = {num}")
        for name in spec["reserved_names"]:
            if name in cur_names:
                problems.append(f"reserved name reused: {msg}.{name}")

    for enum, values in old["enums"].items():
        cur = new["enums"].get(enum)
        if cur is None:
            problems.append(f"enum removed: {enum}")
            continue
        for num, name in values.items():
            if cur.get(num) != name:
                problems.append(f"enum value changed or removed: {enum}.{name} (= {num})")
    return problems


def dump_lock(lock: dict) -> str:
    return json.dumps(lock, indent=2, sort_keys=True) + "\n"


# ---------------------------------------------------------------------------
# Reference documentation (Markdown generated from descriptors + comments)
# ---------------------------------------------------------------------------

# FileDescriptorProto / DescriptorProto field numbers used in SourceCodeInfo paths.
_FILE_MESSAGE, _FILE_ENUM, _FILE_SERVICE = 4, 5, 6
_MSG_FIELD, _MSG_NESTED, _MSG_ENUM = 2, 3, 4
_ENUM_VALUE, _SVC_METHOD = 2, 2


def _comments(fd: descriptor_pb2.FileDescriptorProto) -> dict[tuple[int, ...], str]:
    out = {}
    for loc in fd.source_code_info.location:
        text = (loc.leading_comments or loc.trailing_comments).strip()
        if text:
            out[tuple(loc.path)] = " ".join(line.strip() for line in text.splitlines())
    return out


def _type_label(f: descriptor_pb2.FieldDescriptorProto, pkg: str) -> str:
    if f.type_name:
        base = f.type_name.removeprefix(f".{pkg}.")
    else:
        base = descriptor_pb2.FieldDescriptorProto.Type.Name(f.type).removeprefix("TYPE_").lower()
    if f.label == descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED:
        return f"repeated {base}"
    if f.proto3_optional:
        return f"optional {base}"
    return base


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def build_reference(contract: Contract, fd: descriptor_pb2.FileDescriptorProto) -> str:
    pkg = fd.package
    com = _comments(fd)
    lines = [
        f"# {contract.title}",
        "",
        "<!-- Generated by scripts/grpc_contracts.py from "
        f"proto/{contract.proto}. Do not edit by hand. -->",
        "",
        f"**Package:** `{pkg}`  ",
        f"**Source:** [`proto/{contract.proto}`](../../../proto/{contract.proto})",
        "",
    ]
    for si, svc in enumerate(fd.service):
        lines += [f"## Service `{svc.name}`", "", com.get((_FILE_SERVICE, si), ""), "",
                  "| RPC | Request | Response | Description |", "|-----|---------|----------|-------------|"]
        for mi, m in enumerate(svc.method):
            desc = com.get((_FILE_SERVICE, si, _SVC_METHOD, mi), "")
            lines.append(
                f"| `{m.name}` | [`{m.input_type.rsplit('.', 1)[-1]}`](#{m.input_type.rsplit('.', 1)[-1].lower()}) "
                f"| [`{m.output_type.rsplit('.', 1)[-1]}`](#{m.output_type.rsplit('.', 1)[-1].lower()}) | {_cell(desc)} |"
            )
        lines.append("")

    lines += ["## Messages", ""]

    def message(msg: descriptor_pb2.DescriptorProto, path: tuple[int, ...], prefix: str) -> None:
        name = f"{prefix}{msg.name}"
        lines.extend([f"### {name}", ""])
        if com.get(path):
            lines.extend([com[path], ""])
        if msg.field:
            lines.extend(["| Field | Number | Type | Description |", "|-------|--------|------|-------------|"])
            for fi, f in enumerate(msg.field):
                desc = com.get(path + (_MSG_FIELD, fi), "")
                lines.append(f"| `{f.name}` | {f.number} | `{_type_label(f, pkg)}` | {_cell(desc)} |")
        else:
            lines.append("_No fields._")
        lines.append("")
        for ei, enum in enumerate(msg.enum_type):
            enum_doc(enum, path + (_MSG_ENUM, ei), f"{name}.")
        for ni, nested in enumerate(msg.nested_type):
            message(nested, path + (_MSG_NESTED, ni), f"{name}.")

    def enum_doc(enum: descriptor_pb2.EnumDescriptorProto, path: tuple[int, ...], prefix: str) -> None:
        lines.extend([f"### {prefix}{enum.name}", ""])
        if com.get(path):
            lines.extend([com[path], ""])
        lines.extend(["| Value | Number | Description |", "|-------|--------|-------------|"])
        for vi, v in enumerate(enum.value):
            lines.append(f"| `{v.name}` | {v.number} | {_cell(com.get(path + (_ENUM_VALUE, vi), ''))} |")
        lines.append("")

    for mi, msg in enumerate(fd.message_type):
        message(msg, (_FILE_MESSAGE, mi), "")
    if fd.enum_type:
        lines += ["## Enums", ""]
        for ei, enum in enumerate(fd.enum_type):
            enum_doc(enum, (_FILE_ENUM, ei), "")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _file_descriptor(ds: descriptor_pb2.FileDescriptorSet, contract: Contract) -> descriptor_pb2.FileDescriptorProto:
    return next(f for f in ds.file if f.name == contract.proto)


def cmd_generate() -> int:
    status = 0
    for contract in CONTRACTS:
        with tempfile.TemporaryDirectory() as tmp:
            ds = run_protoc(contract, Path(tmp))
            fd = _file_descriptor(ds, contract)
            new_lock = build_lock(fd)
            if contract.lock.exists():
                problems = breaking_changes(json.loads(contract.lock.read_text()), new_lock)
                if problems:
                    print(f"[BREAKING] {contract.proto} — lock not updated:")
                    print("\n".join(f"  - {p}" for p in problems))
                    status = 1
                    continue
            target = OUT_ROOT / contract.package_dir
            target.mkdir(parents=True, exist_ok=True)
            for old in target.iterdir():
                if old.name.endswith(GENERATED_SUFFIXES):
                    old.unlink()
            for rel, text in generated_files(Path(tmp), contract).items():
                (OUT_ROOT / rel).write_text(text)
            contract.lock.write_text(dump_lock(new_lock))
            contract.reference_doc.write_text(build_reference(contract, fd))
            print(f"[OK] generated {contract.proto}")
    return status


def cmd_check() -> int:
    status = 0
    for contract in CONTRACTS:
        with tempfile.TemporaryDirectory() as tmp:
            ds = run_protoc(contract, Path(tmp))
            fd = _file_descriptor(ds, contract)
            new_lock = build_lock(fd)
            if not contract.lock.exists():
                print(f"[FAIL] missing contract lock {contract.lock.relative_to(ROOT)}")
                status = 1
                continue
            old_lock = json.loads(contract.lock.read_text())
            problems = breaking_changes(old_lock, new_lock)
            if problems:
                print(f"[FAIL] breaking changes in {contract.proto} (v1 is additive-only):")
                print("\n".join(f"  - {p}" for p in problems))
                status = 1
            if dump_lock(new_lock) != contract.lock.read_text():
                print(f"[FAIL] contract lock is stale for {contract.proto}; run generate")
                status = 1
            expected = generated_files(Path(tmp), contract)
            actual = generated_files(OUT_ROOT, contract)
            if expected != actual:
                stale = sorted(set(expected) ^ set(actual) | {k for k in expected if expected.get(k) != actual.get(k)})
                print(f"[FAIL] generated code is stale for {contract.proto}: {stale}; run generate")
                status = 1
            if not contract.reference_doc.exists() or contract.reference_doc.read_text() != build_reference(contract, fd):
                print(f"[FAIL] reference doc is stale: {contract.reference_doc.relative_to(ROOT)}; run generate")
                status = 1
            if status == 0:
                print(f"[OK] {contract.proto}: generated code, docs and lock are up to date; no breaking changes")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["generate", "check"])
    args = parser.parse_args(argv)
    return cmd_generate() if args.command == "generate" else cmd_check()


if __name__ == "__main__":
    raise SystemExit(main())
