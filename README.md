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
DOMAIN=location-api.yourdomain.com
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
DOMAIN=location-api.yourdomain.com
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
# Check health
curl http://localhost:5000/health

# Or via your domain
curl https://location-api.yourdomain.com/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "laptop" // or "homelab"
}
```

## API Endpoints

### Health Check
```bash
curl https://location-api.yourdomain.com/health
```

### Add Location
```bash
curl -X POST https://location-api.yourdomain.com/api/location \
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
curl https://location-api.yourdomain.com/api/locations
```

### Get Locations (last 6 hours)
```bash
curl https://location-api.yourdomain.com/api/locations?hours=6
```

### Get Locations for Specific Device
```bash
curl https://location-api.yourdomain.com/api/locations?device_id=my_phone
```

### Get Device List
```bash
curl https://location-api.yourdomain.com/api/devices
```

## Architecture

```
                     Cloudflare Tunnel
                            |
              +-------------+-------------+
              |                           |
         [Traefik]                    [nginx]
          (Laptop)                   (Homelab)
              |                           |
              +-------------+-------------+
                            |
                    [location_api]
                            |
                      [postgres]
```

Both setups route through Cloudflare tunnels to the same domain, but use different reverse proxies locally.

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

Your Android app should use:
- **Production URL**: `https://location-api.yourdomain.com`
- **Dev/Test URL**: `http://192.168.x.x:5000` (direct to laptop/homelab IP)

Add a settings toggle in the app to switch between prod and dev.

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
