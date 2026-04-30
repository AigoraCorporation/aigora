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

## Notes

- This setup is for local development only
- Data is persisted via Docker volumes
- Configuration is controlled via .env