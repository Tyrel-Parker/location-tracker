# Location Tracker API

A simple Flask API for tracking GPS locations with PostgreSQL backend.

## Project Structure

```
location-tracker/
├── docker-compose.yml
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── init.sql
└── README.md
```

## Setup

1. Make sure Docker and Docker Compose are installed

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Check if services are running:
   ```bash
   docker-compose ps
   ```

4. Check logs:
   ```bash
   docker-compose logs -f
   ```

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Add Location
```bash
curl -X POST http://localhost:5000/api/location \
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
curl http://localhost:5000/api/locations
```

### Get Locations (last 6 hours)
```bash
curl http://localhost:5000/api/locations?hours=6
```

### Get Locations for Specific Device
```bash
curl http://localhost:5000/api/locations?device_id=my_phone
```

### Get Device List
```bash
curl http://localhost:5000/api/devices
```

## Testing

The database is initialized with some test data. You can query it immediately:

```bash
curl http://localhost:5000/api/locations
```

## Stopping Services

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

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

## Next Steps

- Build Android app to send location data
- Add authentication (API keys)
- Add HTTPS/TLS
- Deploy to your home server
