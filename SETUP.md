# Quick Setup Guide

## What's Included

- `docker-compose.yml` - Uses environment variables from .env
- `.env.example` - Template for your credentials (SAFE to commit)
- `.gitignore` - Keeps .env out of version control
- `api/` - Flask application and database schema
- `README.md` - Full documentation

## First Time Setup

1. **Extract the files:**
   ```bash
   tar -xzf location-tracker.tar.gz
   cd location-tracker
   ```

2. **Create your .env file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env with your credentials:**
   ```bash
   nano .env
   ```
   
   Change at minimum:
   - `POSTGRES_PASSWORD` to something secure
   
   Optionally change:
   - `POSTGRES_USER` if you want a different username
   - `POSTGRES_PORT` if 5432 conflicts with existing services
   - `API_PORT` if 5000 conflicts with existing services

4. **Start the services:**
   ```bash
   docker-compose up -d
   ```

5. **Verify it's running:**
   ```bash
   curl http://localhost:5000/health
   ```

## If You Want to Use Git

```bash
git init
git add .
git commit -m "Initial commit"
```

The `.gitignore` ensures your `.env` file (with real credentials) won't be committed.
Only `.env.example` (with placeholder values) will be tracked.

## When Deploying to Your Server

Replace `localhost` in curl commands with your server's IP address:
```bash
curl http://192.168.1.100:5000/health
```

Your Android app will also use this IP to connect to the API.
