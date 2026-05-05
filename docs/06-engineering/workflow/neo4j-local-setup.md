# Neo4j Local Setup

This guide explains how to run a local Neo4j instance for development.

---

## Prerequisites

- Docker installed
- Docker Compose available

---

## How to Run

From the project root:

```bash
cd docker/neo4j
cp .env.example .env
docker compose up -d
```

--- 

## Access
- Neo4j Browser: http://localhost:7474
- Bolt: bolt://localhost:7687

## Default Credentials
- User: neo4j
- Password: aigora-local-password

---

## Environment Variables (Required for Application)

To allow the application and CLI tools to connect to Neo4j, you must define the following environment variables **in your current terminal session**.

### PowerShell

```powershell
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="aigora-local-password"
$env:NEO4J_DATABASE="neo4j"
```

### CMD (Windows)

```bat
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USERNAME=neo4j
set NEO4J_PASSWORD=aigora-local-password
set NEO4J_DATABASE=neo4j
```

### Git Bash / Linux / macOS

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="aigora-local-password"
export NEO4J_DATABASE="neo4j"
```

> These variables must be set in the same terminal session where you run the application (e.g. CLI scripts or tests).

---

## Notes

* This setup is for local development only
* Data is persisted via Docker volumes
* Configuration is controlled via `.env`
* Neo4j Community Edition runs in **single database mode** (default: `neo4j`)
