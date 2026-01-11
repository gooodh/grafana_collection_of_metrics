# Grafana Collection of Metrics

This project demonstrates a complete monitoring and log collection system using a modern stack of tools: **Grafana**, **Loki**, **Prometheus**, and **Promtail**.

## Project Goal

The main goal of the project is to show how to integrate and configure an observability system for a FastAPI web application:

- **Grafana** — visualization of metrics and logs through dashboards
- **Prometheus** — collection and storage of application metrics
- **Loki** — aggregation and storage of logs
- **Promtail** — agent for collecting logs and sending them to Loki
- **Postgres Exporter** — экспортер метрик PostgreSQL для мониторинга состояния базы данных

The project includes a ready-made FastAPI application with an authentication system that generates metrics and logs to demonstrate monitoring capabilities.

![Grafana Dashboard - Metrics Overview](temp/imgs/screenshot_1.png)
![Grafana Dashboard - DOWN APP](temp/imgs/screenshot_2.png)
![Postrges - UNHEALTHY](temp/imgs/screenshot_3.png)
![Postgres_exporter - System Monitoring](temp/imgs/screenshot_4.png)
![Postgres_exporter - System Monitoring](temp/imgs/screenshot_4.png)

## Project Architecture

```
├── app/                          # FastAPI application
│   ├── auth/                     # Authentication module
│   ├── dao/                      # Data Access Objects
│   ├── migration/                # Database migrations
│   ├── static/                   # Static files
│   ├── config.py                 # Application configuration
│   ├── main.py                   # FastAPI entry point
│   └── exceptions.py             # Exception handling
├── grafana/                      # Grafana configuration
├── ab/                          # Load testing results
├── prometheus.yml               # Prometheus configuration
├── loki-config.yml             # Loki configuration
├── promtail-config.yaml        # Promtail configuration
├── docker-compose.yml          # Main Docker configuration
├── docker-compose.staging.yml  # Staging environment
├── docker-compose.prod.yml     # Production environment
└── docker-compose.test.yml     # Test environment
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/gooodh/grafana_collection_of_metrics.git
cd grafana_collection_of_metrics
```

### 2. Start the Monitoring System
```bash
docker compose up --build -d
```

### 3. Access Services

After startup, the following services will be available:

- **FastAPI Application**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **Postgres Exporter**: http://localhost:9187 (метрики PostgreSQL)

### 4. Generate Test Data

To demonstrate the monitoring system, you can generate load:

```bash
# Install Apache Bench (if not installed)
sudo apt-get install apache2-utils

# Generate HTTP requests
ab -n 1000 -c 10 http://localhost:8000/
```

## Monitoring Configuration

### Health Check Endpoints

The app provides advanced health check endpoints with Prometheus integration:

- `GET /health` - basic health check
- `GET /health/detaile` - detailed check with the database and system resources  
- `GET /health/read` - readiness probe for Kubernetes
- `GET /health/liv` - liveness probe for Kubernetes
- `GET /health/metric` - health metrics in JSON format
- `GET /metrics` - Prometheus metrics

```bash
# Тестирование health endpoints
make health-check

# Просмотр метрик здоровья
make health-metrics
```

### Prometheus Metrics

The application automatically exports the following metrics:

**Standard FastAPI metrics:**

- `http_requests_total` - total number of HTTP requests
- `http_request_duration_seconds` - request execution time
- `http_requests_inprogress` - requests in progress

**Custom health metrics:**
- `database_connection_status` - the status of connection to the database
- `database_response_time_seconds` - DB response time
- `system_cpu_percent` - CPU usage
- `system_memory_percent` - memory usage
- `system_disk_percent` - disk usage
- `health_check_requests_total` - number of health check requests
- `fast_requests_total` - number of fast requests (< 100ms)
- `slow_requests_total` - number of slow requests (> 1s)

**PostgreSQL metrics (via postgres_exporter):**
- `pg_up` - статус доступности PostgreSQL
- `pg_stat_database_*` - статистика по базам данных
- `pg_stat_user_tables_*` - статистика по пользовательским таблицам
- `pg_locks_count` - количество блокировок
- `pg_stat_activity_count` - количество активных соединений
- `pg_database_size_bytes` - размер базы данных в байтах
- `pg_stat_bgwriter_*` - статистика фонового процесса записи

## PostgreSQL Monitoring с Postgres Exporter

Postgres Exporter is a specialized metric exporter for PostgreSQL that collects detailed information about the status and performance of the database.

### Main features

**Performance monitoring:**
- Query execution statistics
- Database response time
- Number of active connections
- Using indexes

**Resource monitoring:**
- Size of databases and tables
- Disk space usage
- Cache statistics
- Blockages and conflicts

**Availability monitoring:**
- The status of the connection to PostgreSQL
- Checking the functionality of replicas
- Monitoring of PostgreSQL processes

### Configuration

Postgres Exporter is configured via environment variables in docker-compose.yml:

```yaml
postgres_exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://username:password@postgres:5432/database?sslmode=disable"
  ports:
    - "9187:9187"
```

### Key metrics for monitoring

**Performance:**
- `pg_stat_database_tup_returned` - the number of rows returned
- `pg_stat_database_tup_fetched` - number of extracted rows
- `pg_stat_database_xact_commit` - number of recorded transactions
- `pg_stat_database_xact_rollback` - number of transactions rolled out

**Connections:**
- `pg_stat_activity_count` - current number of connections
- `pg_settings_max_connections` - maximum number of connections

**Dimensions:**
- `pg_database_size_bytes` - the size of the database
- `pg_stat_user_tables_n_tup_ins` - number of inserted rows
- `pg_stat_user_tables_n_tup_upd` - number of updated rows
- `pg_stat_user_tables_n_tup_del` - number of deleted rows

### Alerts and notifications

Recommended alerts for PostgreSQL:

```yaml
# Высокое количество соединений
- alert: PostgreSQLTooManyConnections
  expr: pg_stat_activity_count > (pg_settings_max_connections * 0.8)
  
# Низкая производительность
- alert: PostgreSQLSlowQueries
  expr: rate(pg_stat_database_tup_returned[5m]) < 100
  
# Проблемы с доступностью
- alert: PostgreSQLDown
  expr: pg_up == 0
```

## Monitoring in Different Environments

The project supports different configurations for various environments:

- **Development**: `docker-compose.yml`
- **Testing**: `docker-compose.test.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`

```bash
# Run in staging environment
docker compose -f docker-compose.staging.yml up -d

# Run in production environment
docker compose -f docker-compose.prod.yml up -d
```
