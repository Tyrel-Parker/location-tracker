# Location Tracker API

A multi-environment Flask API for tracking GPS locations with PostgreSQL backend.

Works seamlessly with:
- **Traefik** (laptop with Cloudflare tunnel)
- **nginx** (homelab with Cloudflare tunnel)
- **Direct access** (no reverse proxy)

## Quick Start

### 1. Initial Setup (Same for Both Locations)

```bash
# Extract and enter directory
tar -xzf location-tracker.tar.gz
cd location-tracker

# Create environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 2. Configure for Your Location

#### On Laptop (Traefik):

Edit `.env`:
```bash
DOMAIN=laptop.tyrelparker.dev
ENVIRONMENT=laptop
PROXY_TYPE=traefik
```

Make sure the `web` network exists:
```bash
docker network create web
```

Start services:
```bash
docker-compose up -d
```

Traefik will automatically pick up the service via labels!

#### On Homelab (nginx):

Edit `.env`:
```bash
DOMAIN=homelab.tyrelparker.dev
ENVIRONMENT=homelab
PROXY_TYPE=nginx
API_PORT=5000  # Or any available port
```

If you don't have the `web` network, edit `docker-compose.yml` and comment out the `external: true` line under the `web` network.

Start services:
```bash
docker-compose up -d
```

Then set up nginx:
```bash
# Copy nginx config
sudo cp nginx/location-api.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/location-api.conf /etc/nginx/sites-enabled/

# Edit the config to match your domain
sudo nano /etc/nginx/sites-enabled/location-api.conf

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Verify It Works

```bash
# Check health locally
curl http://localhost:5000/location-tracker/health

# Or open the web interface in your browser
open http://localhost:5000/location-tracker

# Or via your domain (laptop)
curl https://laptop.tyrelparker.dev/location-tracker/health

# Or via your domain (homelab)
curl https://homelab.tyrelparker.dev/location-tracker/health
```

You should see a web interface where you can test submitting locations!

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "laptop" // or "homelab"
}
```

## API Endpoints

### Web Interface
Open your browser and go to:
- `http://localhost:5000/location-tracker` (local)
- `https://laptop.tyrelparker.dev/location-tracker` (laptop via Cloudflare)
- `https://homelab.tyrelparker.dev/location-tracker` (homelab via Cloudflare)

You'll see a simple web form to test submitting locations and view the last 10 submissions.

### Health Check
```bash
# Laptop
curl https://laptop.tyrelparker.dev/location-tracker/health

# Homelab
curl https://homelab.tyrelparker.dev/location-tracker/health

# Also available at root for backwards compatibility
curl https://homelab.tyrelparker.dev/health
```

### Add Location
```bash
# Using /location-tracker prefix (recommended)
curl -X POST https://homelab.tyrelparker.dev/location-tracker/api/location \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "my_phone",
    "latitude": 47.6588,
    "longitude": -117.4260,
    "timestamp": "2024-12-12T10:30:00Z"
  }'

# Also works at root /api/location for backwards compatibility
curl -X POST https://homelab.tyrelparker.dev/api/location \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "my_phone",
    "latitude": 47.6588,
    "longitude": -117.4260,
    "timestamp": "2024-12-12T10:30:00Z"
  }'
```

### Get Locations (last 24 hours)
```bash
curl https://homelab.tyrelparker.dev/location-tracker/api/locations
```

### Get Locations (last 6 hours)
```bash
curl https://homelab.tyrelparker.dev/location-tracker/api/locations?hours=6
```

### Get Locations for Specific Device
```bash
curl https://homelab.tyrelparker.dev/location-tracker/api/locations?device_id=my_phone
```

### Get Device List
```bash
curl https://homelab.tyrelparker.dev/location-tracker/api/devices
```

## Architecture

```
              Cloudflare Tunnel
                     |
        +------------+------------+
        |                         |
   laptop.tyrelparker.dev   homelab.tyrelparker.dev
        |                         |
    [Traefik]                 [nginx]
     (Laptop)                (Homelab)
        |                         |
        +------------+------------+
                     |
             [location_api]
                     |
               [postgres]
```

Each location has its own subdomain but runs identical code.

## Files Explained

- **`docker-compose.yml`** - Contains Traefik labels (ignored if not using Traefik)
- **`nginx/location-api.conf`** - nginx configuration (used only on homelab)
- **`.env`** - Your local configuration (not committed to git)
- **`.env.example`** - Template for configuration

## Switching Between Locations

The same codebase works in both places! Just:

1. Update `.env` with location-specific settings
2. Run `docker-compose up -d`
3. Configure reverse proxy if needed (nginx only)

## Database Access

Connect to PostgreSQL directly:
```bash
docker exec -it location_db psql -U tracker_user -d location_tracker
```

Sample queries:
```sql
-- See all locations
SELECT * FROM locations ORDER BY timestamp DESC;

-- Count locations per device
SELECT device_id, COUNT(*) FROM locations GROUP BY device_id;
```

## Stopping Services

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

## Android App Configuration

Your Android app should support both locations:

```kotlin
object ApiConfig {
    // Production endpoints
    const val LAPTOP_URL = "https://laptop.tyrelparker.dev"
    const val HOMELAB_URL = "https://homelab.tyrelparker.dev"
    
    // Dev/Test (when on same network as device)
    const val DEV_URL = "http://192.168.1.100:5000"
    
    // Default to homelab (always-on)
    var currentUrl = HOMELAB_URL
}
```

**Recommended approach:**
1. **Default to homelab** (always-on server)
2. **Add settings toggle** to switch to laptop when needed
3. **Auto-failover:** Try homelab first, fall back to laptop if unreachable

Example failover logic:
```kotlin
suspend fun getCurrentApiUrl(): String {
    return try {
        // Try homelab first
        testConnection(HOMELAB_URL)
        HOMELAB_URL
    } catch (e: Exception) {
        // Fall back to laptop
        LAPTOP_URL
    }
}
```

## Troubleshooting

### "network web declared as external, but could not be found"

On homelab (nginx setup), edit `docker-compose.yml`:
```yaml
web:
  # external: true  # Comment this out
  driver: bridge    # Add this
```

### Traefik not picking up the service

Make sure:
1. Traefik is running and configured
2. The `web` network exists: `docker network create web`
3. Your domain is set correctly in `.env`

### nginx showing 502 Bad Gateway

Check:
1. API is running: `docker ps`
2. API is healthy: `curl http://localhost:5000/health`
3. nginx config is correct: `sudo nginx -t`

## Next Steps

- Build Android app to send location data
- Add authentication (API keys)
- Add rate limiting
- Set up monitoring
