from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Allow requests from Android app

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Create a database connection"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/location', methods=['POST'])
def add_location():
    """Add a new location point"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['device_id', 'latitude', 'longitude', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        device_id = data['device_id']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timestamp = data['timestamp']
        
        # Insert into database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO locations (device_id, latitude, longitude, timestamp)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (device_id, latitude, longitude, timestamp)
        )
        location_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': location_id,
            'message': 'Location added successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid latitude or longitude format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get locations from the last N hours"""
    try:
        # Get hours parameter, default to 24
        hours = request.args.get('hours', default=24, type=int)
        
        # Get device_id parameter (optional filter)
        device_id = request.args.get('device_id', default=None, type=str)
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if device_id:
            cur.execute(
                """
                SELECT id, device_id, latitude, longitude, timestamp, created_at
                FROM locations
                WHERE timestamp >= %s AND device_id = %s
                ORDER BY timestamp DESC
                """,
                (cutoff_time, device_id)
            )
        else:
            cur.execute(
                """
                SELECT id, device_id, latitude, longitude, timestamp, created_at
                FROM locations
                WHERE timestamp >= %s
                ORDER BY timestamp DESC
                """,
                (cutoff_time,)
            )
        
        locations = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert to list of dicts and format timestamps
        result = []
        for loc in locations:
            result.append({
                'id': loc['id'],
                'device_id': loc['device_id'],
                'latitude': loc['latitude'],
                'longitude': loc['longitude'],
                'timestamp': loc['timestamp'].isoformat(),
                'created_at': loc['created_at'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'locations': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of unique device IDs"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT device_id, 
                   COUNT(*) as location_count,
                   MAX(timestamp) as last_seen
            FROM locations
            GROUP BY device_id
            ORDER BY last_seen DESC
            """
        )
        devices = cur.fetchall()
        cur.close()
        conn.close()
        
        result = []
        for device in devices:
            result.append({
                'device_id': device['device_id'],
                'location_count': device['location_count'],
                'last_seen': device['last_seen'].isoformat() if device['last_seen'] else None
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'devices': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
