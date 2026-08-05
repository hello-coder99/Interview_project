# URL Shortener

A production-style URL Shortener built using **Flask**, **MySQL**, **Redis**, **Nginx**, and **Docker Compose**.

The application allows users to generate short URLs, redirect to the original URLs, and uses Redis to cache frequently accessed URLs for improved performance.

---

## Features

* Generate short URLs
* Redirect using generated short URLs
* Store URLs permanently in MySQL
* Cache URLs in Redis
* Nginx reverse proxy
* Docker Compose deployment
* Modular Flask project structure
* SQL Injection protection using parameterized queries

---

## Tech Stack

| Component        | Technology     |
| ---------------- | -------------- |
| Backend          | Flask          |
| Database         | MySQL 5.7      |
| Cache            | Redis 7        |
| Reverse Proxy    | Nginx          |
| Containerization | Docker Compose |

---

## Project Structure

```text
url-shortener/
│
├── docker-compose.yml
├── README.md
│
├── web-flask/
│   ├── app.py
│   ├── routes/
│   ├── databases/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── Dockerfile
│   └── requirements.txt
│
├── maria_db/
│   └── init.sql
│
└── rev-nginx/
    └── nginx.conf
```

---

## Architecture

```text
                 Browser
                    │
                    ▼
                 Nginx
                    │
                    ▼
                Flask API
              ┌─────┴─────┐
              │           │
          Redis Cache   MySQL
```

---

## Request Flow

### Create Short URL

```text
Browser
    │
POST /shorten
    │
    ▼
Flask
    │
Generate Short Code
    │
    ▼
Store in MySQL
    │
    ▼
Return Short URL
```

---

### Redirect

```text
Browser
    │
GET /abc123
    │
    ▼
Flask
    │
    ▼
Redis Cache
 │        │
 │ Hit    │ Miss
 ▼        ▼
Return   MySQL
           │
           ▼
      Store in Redis
           │
           ▼
Redirect User
```

---

## Getting Started

### Clone the repository

```bash
git clone <repository-url>
cd url-shortener
```

### Build the containers

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

---

## Docker Services

| Service | Port            |
| ------- | --------------- |
| Nginx   | 80              |
| Flask   | 5000 (internal) |
| MySQL   | 3306            |
| Redis   | 6379            |

---

## Database Initialization

The database schema is automatically created during the first startup using:

```text
maria_db/init.sql
```

The initialization script creates:

* Database
* Tables
* Initial schema

**Note:** If the database volume already exists, Docker will not execute the initialization script again.

To recreate the database:

```bash
docker compose down -v
docker compose up --build
```

---

## Redis Cache Strategy

The application uses the **Cache-Aside Pattern**.

1. Check Redis.
2. If found, return immediately.
3. Otherwise query MySQL.
4. Store the result in Redis.
5. Return the URL.

This significantly reduces database queries for frequently accessed URLs.

---

## API Overview

### Home

```
GET /
```

Displays the URL shortening page.

---

### Generate Short URL

```
POST /shorten
```

Creates a new short URL.

---

### Redirect

```
GET /<short_code>
```

Redirects to the original URL.

---

## Environment Variables

The application expects the following environment variables:

```text
MYSQL_HOST
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DATABASE
REDIS_HOST
```

These are configured in `docker-compose.yml`.

---

## Future Improvements

* User authentication
* Click analytics
* Custom aliases
* QR code generation
* URL expiration
* REST API
* Rate limiting
* Admin dashboard
* HTTPS support
* Connection pooling
* Health checks
* Docker healthcheck support
* Database migrations

---

## Author

**Aman**

Built as a learning project to understand backend development, Docker, caching, reverse proxies, and scalable web application architecture.

