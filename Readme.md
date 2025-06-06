# Local Development Setup for Hasura DDN

## Prerequisites

Ensure the following tools are installed on your system:

- [DDN CLI](https://hasura.io/docs/latest/ddn/)
- [Docker](https://www.docker.com/)
- [Flyway](https://www.red-gate.com/products/flyway/community/download/)

---

## Step-by-Step Guide

### 1. Start Databases via Docker

Launch the local PostgreSQL instances for schema and migration by running the `docker-compose.yaml` in the root directory:

```bash
docker-compose up -d
```

---

### 2. Run Flyway Migrations

Apply schema migrations using Flyway. Steps to run migrations are documented in [`flyway.md`](./flyway.md).

---

### 3. Navigate to the DDN Project Directory

```bash
cd ddn-project
```

---

### 4. Introspect Your Data Source

Generate Hasura metadata by introspecting the database schema:

```bash
ddn connector introspect my_connector
```

> **Note:** Replace `my_connector` with your actual connector name.

This will populate your schema metadata inside `app/connector/my_connector/configuration.json`.

---

### 5. Add Resources to Your Supergraph

Generate metadata for models, commands, and relationships in your supergraph:

```bash
ddn model add my_connector '*'
ddn command add my_connector '*'
ddn relationship add my_connector '*'
```

> **Note:** Replace `my_connector` with your actual connector name.

The generated Hasura Metadata Language (HML) will be stored under the `app/metadata/` directory.

---

### 6. Build the Supergraph

Build an immutable version of your supergraph and local assets:

```bash
ddn supergraph build local
```

You can access the local console at: [https://console.hasura.io/local/graphql](https://console.hasura.io/local/graphql)

---

### 7. Start Your Supergraph

Start all required services (engine, connector, etc.) using Docker:

```bash
ddn run docker-start
```

Check running containers:

```bash
docker ps
```

---

### 8. Verify Everything Works

Execute a test query in your local Hasura console to verify that the setup is successful and your data is accessible.

---

### 9. Commit and Create a Build

Once you've verified everything, commit your metadata and configuration files to version control to prepare for production builds.

---

Reference:

![Notepad - Frame 9](https://github.com/user-attachments/assets/08277549-8f26-4e48-a563-146806a39bd3)





