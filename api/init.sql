-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX idx_timestamp ON locations(timestamp DESC);
CREATE INDEX idx_device_timestamp ON locations(device_id, timestamp DESC);

-- Insert some test data for initial testing
INSERT INTO locations (device_id, latitude, longitude, timestamp) VALUES
    ('test_device', 47.6588, -117.4260, NOW() - INTERVAL '1 hour'),
    ('test_device', 47.6590, -117.4265, NOW() - INTERVAL '30 minutes'),
    ('test_device', 47.6592, -117.4270, NOW());
