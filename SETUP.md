# Quick Setup Guide

## TL;DR

```bash
# Extract
tar -xzf location-tracker.tar.gz && cd location-tracker

# On Laptop:
cp .env.laptop .env
docker network create web
docker-compose up -d

# On Homelab:
cp .env.homelab .env
# Edit docker-compose.yml: comment out "external: true" under web network
docker-compose up -d
sudo cp nginx/location-api.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/location-api.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## The Key Insight

**Same domain, different reverse proxies:**
- Laptop: Traefik handles routing automatically via Docker labels
- Homelab: nginx proxies to the container port

**The app doesn't need to know or care** - it just listens on port 5000 internally.

## File Customization by Location

You only need to change **one file**: `.env`

**Laptop (.env.laptop):**
```bash
ENVIRONMENT=laptop
PROXY_TYPE=traefik
```

**Homelab (.env.homelab):**
```bash
ENVIRONMENT=homelab
PROXY_TYPE=nginx
```

Everything else stays the same!

## Docker Compose Network Note

**Laptop:** Needs the `web` network for Traefik
```bash
docker network create web
```

**Homelab:** If you don't use Traefik globally, edit `docker-compose.yml`:
```yaml
networks:
  web:
    # external: true  # Comment this out
    driver: bridge    # Add this
```

## Testing

```bash
# Local test (both locations)
curl http://localhost:5000/health

# Through reverse proxy - Laptop
curl https://laptop.tyrelparker.dev/health

# Through reverse proxy - Homelab
curl https://homelab.tyrelparker.dev/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "laptop"  // or "homelab"
}
```

## What Makes This Work Everywhere?

1. **Traefik labels** in docker-compose.yml - Ignored if Traefik isn't running
2. **Port exposure** - Direct access works even with reverse proxy
3. **Same domain** - Your Android app uses one URL for both
4. **Environment variables** - Easy to switch configurations

## Android App URLs

**For the Android app**, you'll want to support both locations:

```kotlin
// Production (works from anywhere via Cloudflare tunnel)
const val LAPTOP_URL = "https://laptop.tyrelparker.dev"
const val HOMELAB_URL = "https://homelab.tyrelparker.dev"

// Dev/Local (when on same network)
const val DEV_URL = "http://192.168.1.100:5000"  // Your local IP
```

**Recommended strategy:**
- **Default to homelab** (always-on, more reliable)
- **Add a settings toggle** to manually switch to laptop
- **Bonus:** Implement auto-failover that tries homelab first, falls back to laptop

## Common Issues

**"web network not found"** → Comment out `external: true` in docker-compose.yml

**"Traefik not routing"** → Check domain in .env matches Cloudflare tunnel

**"nginx 502"** → Make sure container is running: `docker ps`

## Next: Build the Android App!

See README.md for full API documentation and Android app development next steps.
