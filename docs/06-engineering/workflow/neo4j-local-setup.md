# Neo4j Local Setup

This guide explains how to run and validate a local Neo4j instance for development.

---

## Prerequisites

- Docker and Docker Compose installed
- Access to the repository root
- `.env.example` available at `docker/neo4j/.env.example`

---

## Step 1 — Configure Environment Variables

Copy the example environment file and adjust values if needed:

```bash
cd docker/neo4j
cp .env.example .env
```

The `.env` file must define:

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `aigora-local-password` |
| `NEO4J_HTTP_PORT` | HTTP port for Neo4j Browser | `7474` |
| `NEO4J_BOLT_PORT` | Bolt protocol port | `7687` |
| `NEO4J_HEAP_INITIAL` | Initial JVM heap size | `512m` |
| `NEO4J_HEAP_MAX` | Maximum JVM heap size | `1G` |
| `NEO4J_PAGECACHE_SIZE` | Page cache size | `512m` |

> **Note:** Do not commit the `.env` file. It is gitignored.

---

## Step 2 — Start Neo4j

From the `docker/neo4j/` directory:

```bash
docker compose up -d
```

Expected output:

```
[+] Running 1/1
 ✔ Container aigora-neo4j-local  Started
```

---

## Step 3 — Validate Neo4j Browser Access

Open a browser and navigate to:

```
http://localhost:7474
```

**Expected result:** Neo4j Browser login page is displayed.

---

## Step 4 — Validate Authentication

In Neo4j Browser, log in using:

- **Connection URL:** `bolt://localhost:7687`
- **Username:** value from `NEO4J_USER` (default: `neo4j`)
- **Password:** value from `NEO4J_PASSWORD` (default: `aigora-local-password`)

**Expected result:** Successful login and access to Neo4j Browser dashboard.

---

## Step 5 — Validate Bolt Connectivity

Run the following command to confirm Bolt is accessible:

```bash
curl -s http://localhost:7474 | grep -i "neo4j" && echo "HTTP OK"
```

Or test via cypher-shell (if available):

```bash
cypher-shell -u neo4j -p aigora-local-password "RETURN 1 AS check;"
```

**Expected result:** Returns `1` without errors.

---

## Step 6 — Validate Data Persistence

### Write test data

In Neo4j Browser, run:

```cypher
CREATE (:TestNode {id: 'persistence-check'}) RETURN count(*);
```

### Stop the container

```bash
docker compose down
```

### Restart the container

```bash
docker compose up -d
```

### Verify data survived restart

In Neo4j Browser, run:

```cypher
MATCH (n:TestNode {id: 'persistence-check'}) RETURN n;
```

**Expected result:** The `TestNode` is still present after restart.

### Clean up

In Neo4j Browser, run:

```cypher
MATCH (n:TestNode) DELETE n;
```

---

## Stopping and Removing

### Stop (preserve data volumes):

```bash
docker compose down
```

### Stop and remove all data volumes:

```bash
docker compose down -v
```

> **Warning:** `-v` permanently deletes all persisted graph data.

---

## Validation Summary

| Check | Command / Action | Expected Result |
|-------|-----------------|----------------|
| Container starts | `docker compose up -d` | Container running |
| HTTP accessible | `http://localhost:7474` | Login page visible |
| Authentication works | Login in Neo4j Browser | Dashboard accessible |
| Bolt accessible | `curl` or `cypher-shell` | Returns result |
| Data persists | Write → restart → read | Data still present |

---

## Troubleshooting

### Container fails to start

- Verify Docker is running: `docker info`
- Check for port conflicts: `lsof -i :7474` and `lsof -i :7687`
- Inspect logs: `docker compose logs neo4j`

### Authentication fails

- Confirm `.env` values match the credentials used in Neo4j Browser
- On first run, Neo4j may require a password change — use the default and update if prompted

### Bolt connection refused

- Ensure the container is fully started (may take 10–20 seconds)
- Verify `NEO4J_BOLT_PORT` in `.env` matches the port you are connecting to

### Data not persisting

- Confirm you did not use `docker compose down -v` (which removes volumes)
- Check that `neo4j_data` volume exists: `docker volume ls | grep neo4j`

---

## Related Documents

- [docker/neo4j/docker-compose.yml](../../../docker/neo4j/docker-compose.yml)
- [docker/neo4j/.env.example](../../../docker/neo4j/.env.example)
