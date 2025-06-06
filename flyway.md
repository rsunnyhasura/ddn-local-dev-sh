# Flyway DB Migrations Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Flyway via CLI](#flyway-via-cli)
   - [Step 1: Download and Install Flyway CLI](#step-1-download-and-install-flyway-cli)
   - [Step 2: Create/Initialize Your Database](#step-2-createinitialize-your-database)
   - [Step 3: Create a `flyway.conf` File](#step-3-create-a-flywayconf-file)
   - [Step 4: Baseline an Existing Database](#step-4-baseline-an-existing-database)
   - [Step 5: Run Flyway Migrations](#step-5-run-flyway-migrations)
   - [Step 6: Inspect and Manage Migrations](#step-6-inspect-and-manage-migrations)
4. [Flyway via Docker](#flyway-via-docker)
   - [Step 1: Create a `flyway.conf` File](#step-1-create-a-flywayconf-file-1)
   - [Step 2: Create a `migrations` Directory](#step-2-create-a-migrations-directory-1)
   - [Step 3: Run Flyway Migrations Using Docker](#step-3-run-flyway-migrations-using-docker-1)
5. [Flyway via Desktop](#flyway-via-desktop)
   - [Step 1: Download and Install Flyway Desktop](#step-1-download-and-install-flyway-desktop)
   - [Step 2: Create a New Flyway Project](#step-2-create-a-new-flyway-project)
   - [Step 3: Configure Flyway](#step-3-configure-flyway)
   - [Step 4: Run Flyway Migrations](#step-4-run-flyway-migrations)
6. [Troubleshooting](#troubleshooting)
7. [Code Examples](#code-examples)

---

## Introduction

Flyway is a powerful open-source tool for managing database migrations. It supports version-controlled changes to your database schema and data, helping teams maintain consistency across development, testing, and production environments. This document covers how to use Flyway via **CLI**, **Docker**, and **Flyway Desktop**.

---

## Prerequisites

- Java 8+ (for Flyway CLI and Desktop)
- PostgreSQL (or another supported database engine)
- Docker (for Flyway via Docker)
- `psql` or other database client (for initializing databases)

---

## Flyway via CLI

### Step 1: Download and Install Flyway CLI

1. Visit [Flyway Downloads](https://flywaydb.org/download) and download the appropriate package for your OS.
2. Unzip or untar the package to a directory, e.g., `/opt/flyway` or `C:lyway`.
3. Add the `flyway` executable to your `PATH`.

```bash
# Example on macOS/Linux
unzip flyway-commandline-*.zip -d /opt/flyway
export PATH="/opt/flyway/flyway-*/:$PATH"
```

Verify installation:

```bash
flyway -v
```

---

### Step 2: Create/Initialize Your Database

If your target database does not exist, create it using your DB client (`psql` for PostgreSQL).

```bash
# Using psql to create a new database named 'mydatabase'
psql -h localhost -U postgres -c "CREATE DATABASE mydatabase;"
```

For Docker-based Postgres, ensure the container is running and exposed to the host, e.g.:

```yaml
# docker-compose snippet
services:
  postgresschema:
    image: postgres:12
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: schema_password
```

---

### Step 3: Create a `flyway.conf` File

In your project root, create a `flyway.conf`:

```properties
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/mydatabase
flyway.user=postgres
flyway.password=schema_password
flyway.schemas=public
flyway.locations=filesystem:./migrations
flyway.baselineOnMigrate=true
flyway.table=flyway_schema_history
```

- `flyway.baselineOnMigrate=true`: Automatically baseline version 1 if no metadata table exists.
- `flyway.table`: Customize the metadata table name if desired.

---

### Step 4: Baseline an Existing Database

If you already have an existing schema and want Flyway to start tracking from a specific version:

```bash
flyway -configFiles=flyway.conf baseline -baselineVersion=1 -baselineDescription="Initial version"
```

This creates the `flyway_schema_history` table and marks version 1 as applied without running any scripts.

---

### Step 5: Run Flyway Migrations

Place your versioned SQL scripts in `./migrations`. Each file must follow the naming convention: `V<version>__<description>.sql`.

For example:
```
migrations/
  V1__create_users_table.sql
  V2__add_orders_table.sql
  V3__alter_users_add_email.sql
```

Run migrations:

```bash
flyway -configFiles=flyway.conf migrate
```

This command:
- Scans the `migrations` directory.
- Checks the `flyway_schema_history` table.
- Applies any pending migrations.

---

### Step 6: Inspect and Manage Migrations

- **Info**: View applied and pending migrations:
  ```bash
  flyway -configFiles=flyway.conf info
  ```
- **Validate**: Validate applied migrations against available scripts:
  ```bash
  flyway -configFiles=flyway.conf validate
  ```
- **Clean**: Drop all objects in the configured schemas (use with caution):
  ```bash
  flyway -configFiles=flyway.conf clean
  ```
- **Repair**: Remove failed migration entries or correct checksum mismatches:
  ```bash
  flyway -configFiles=flyway.conf repair
  ```

---

## Flyway via Docker

### Step 1: Create a `flyway.conf` File

Create `flyway.conf` in your project root:

```properties
flyway.url=jdbc:postgresql://localhost:5432/mydatabase
flyway.user=postgres
flyway.password=schema_password
flyway.schemas=public
flyway.locations=filesystem:./migrations
flyway.baselineOnMigrate=true
flyway.table=flyway_schema_history
```

---

### Step 2: Create a `migrations` Directory

```bash
mkdir migrations
```

Add your SQL migration scripts here.

---

### Step 3: Run Flyway Migrations Using Docker

Execute this command from your project root:

```bash
docker run -it --rm   -v $(pwd)/flyway.conf:/flyway/conf/flyway.conf   -v $(pwd)/migrations:/flyway/sql   flyway/flyway:latest migrate
```

For other commands, replace `migrate` with `info`, `validate`, `clean`, `repair`, etc.:

```bash
# View migration info
docker run --rm   -v $(pwd)/flyway.conf:/flyway/conf/flyway.conf   -v $(pwd)/migrations:/flyway/sql   flyway/flyway:latest info
```

---

## Flyway via Desktop

### Step 1: Download and Install Flyway Desktop

Download Flyway Desktop from [https://flywaydb.org/download](https://flywaydb.org/download) and follow the installation instructions for your OS.

### Step 2: Create a New Flyway Project

- Launch Flyway Desktop
- Go to `File > New Project`

### Step 3: Configure Flyway

- Select database type (e.g., PostgreSQL)
- Enter host, port, database name, username, password
- Set `Baseline Version`, `Schemas`, `Locations` to your `migrations` folder

### Step 4: Run Flyway Migrations

Click `Migrate` or use the UI to run other commands like `Baseline`, `Info`, `Clean`, `Validate`, and `Repair`.

---

## Troubleshooting

- Ensure `flyway.conf` is correctly placed and formatted.
- Check that your database is running and accessible on the configured host/port.
- Filenames in `migrations/` must follow `V<version>__<description>.sql`.
- Use `info` and `validate` to inspect the migration state.
- If you encounter version conflicts or failed migrations, use `repair`.

---


## Code Examples

### Sample `flyway.conf`

```properties
flyway.url=jdbc:postgresql://localhost:5432/mydatabase
flyway.user=postgres
flyway.password=schema_password
flyway.schemas=public
flyway.locations=filesystem:./migrations
flyway.baselineOnMigrate=true
flyway.table=flyway_schema_history
```

### Flyway CLI Commands

```bash
# Baseline an existing database
flyway -configFiles=flyway.conf baseline -baselineVersion=1 -baselineDescription="Initial version"

# Run migrations
flyway -configFiles=flyway.conf migrate

# Show migration info
flyway -configFiles=flyway.conf info

# Validate migrations
flyway -configFiles=flyway.conf validate

# Clean database (DROP ALL objects)
flyway -configFiles=flyway.conf clean

# Repair metadata table
flyway -configFiles=flyway.conf repair
```

### Flyway Docker Commands

```bash
# Run migrate
docker run -it --rm \
  -v $(pwd)/flyway.conf:/flyway/conf/flyway.conf \
  -v $(pwd)/migrations:/flyway/sql \
  flyway/flyway:latest migrate

# Run info
docker run --rm \
  -v $(pwd)/flyway.conf:/flyway/conf/flyway.conf \
  -v $(pwd)/migrations:/flyway/sql \
  flyway/flyway:latest info
```

---

References:

https://www.red-gate.com/products/flyway/community/download/

https://documentation.red-gate.com/fd/command-line-277579359.html

https://documentation.red-gate.com/fd/database-development-using-flyway-138346953.html

https://documentation.red-gate.com/fd/generating-migrations-138347054.html





