-- Create the heart_rate table with time + value only
CREATE TABLE IF NOT EXISTS heart_rate (
    timestamp TIMESTAMPTZ PRIMARY KEY,
    value DOUBLE PRECISION
);

-- Convert to hypertable
SELECT create_hypertable('heart_rate', 'timestamp', if_not_exists => TRUE);
