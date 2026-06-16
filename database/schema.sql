"""Database schema"""

CREATE_CONNECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    device_name TEXT NOT NULL,
    device_ip TEXT NOT NULL,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disconnected_at TIMESTAMP,
    duration_seconds INTEGER,
    status TEXT DEFAULT 'connected'
);
"""

CREATE_ACTIVITIES_TABLE = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    activity_data TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES connections(id)
);
"""

CREATE_SCREENSHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    screenshot_path TEXT NOT NULL,
    file_size INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (connection_id) REFERENCES connections(id)
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_connections_device_id ON connections(device_id);
CREATE INDEX IF NOT EXISTS idx_connections_timestamp ON connections(connected_at);
CREATE INDEX IF NOT EXISTS idx_activities_connection_id ON activities(connection_id);
CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp);
"""
