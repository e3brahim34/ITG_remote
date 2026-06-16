"""Database Manager"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from utils.logger import Logger

logger = Logger(__name__)

class DatabaseManager:
    """Manages SQLite database for logging connections and activities"""
    
    DB_FILE = "itg_remote.db"
    
    def __init__(self):
        """Initialize database manager"""
        self.db_file = self.DB_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create connections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    device_ip TEXT NOT NULL,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    disconnected_at TIMESTAMP,
                    duration_seconds INTEGER,
                    status TEXT DEFAULT 'connected'
                )
            """)
            
            # Create activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    connection_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (connection_id) REFERENCES connections(id)
                )
            """)
            
            # Create screenshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    connection_id INTEGER NOT NULL,
                    screenshot_path TEXT NOT NULL,
                    file_size INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (connection_id) REFERENCES connections(id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_connections_device_id ON connections(device_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_connections_timestamp ON connections(connected_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_connection_id ON activities(connection_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp)")
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
    
    def log_connection(self, device_id: str, device_name: str, device_ip: str) -> Optional[int]:
        """Log a new connection
        
        Args:
            device_id: Device ID
            device_name: Device name
            device_ip: Device IP address
            
        Returns:
            Connection ID or None
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO connections (device_id, device_name, device_ip, status)
                VALUES (?, ?, ?, 'connected')
            """, (device_id, device_name, device_ip))
            
            connection_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Connection logged: {device_name} ({device_id})")
            return connection_id
        except Exception as e:
            logger.error(f"Failed to log connection: {str(e)}")
            return None
    
    def end_connection(self, connection_id: int):
        """End a connection
        
        Args:
            connection_id: Connection ID
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get connection start time
            cursor.execute("SELECT connected_at FROM connections WHERE id = ?", (connection_id,))
            result = cursor.fetchone()
            
            if result:
                connected_at = datetime.fromisoformat(result[0])
                now = datetime.now()
                duration = int((now - connected_at).total_seconds())
                
                cursor.execute("""
                    UPDATE connections
                    SET disconnected_at = CURRENT_TIMESTAMP, 
                        duration_seconds = ?,
                        status = 'disconnected'
                    WHERE id = ?
                """, (duration, connection_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Connection ended: {connection_id}")
        except Exception as e:
            logger.error(f"Failed to end connection: {str(e)}")
    
    def log_activity(self, connection_id: int, activity_type: str, activity_data: str = None):
        """Log an activity
        
        Args:
            connection_id: Connection ID
            activity_type: Type of activity
            activity_data: Activity data (optional)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO activities (connection_id, activity_type, activity_data)
                VALUES (?, ?, ?)
            """, (connection_id, activity_type, activity_data))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
    
    def get_connections(self, limit: int = 100) -> List[Dict]:
        """Get recent connections
        
        Args:
            limit: Maximum number of connections to retrieve
            
        Returns:
            List of connection dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM connections
                ORDER BY connected_at DESC
                LIMIT ?
            """, (limit,))
            
            connections = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return connections
        except Exception as e:
            logger.error(f"Failed to get connections: {str(e)}")
            return []
    
    def get_activities(self, connection_id: int) -> List[Dict]:
        """Get activities for a connection
        
        Args:
            connection_id: Connection ID
            
        Returns:
            List of activity dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM activities
                WHERE connection_id = ?
                ORDER BY timestamp DESC
            """, (connection_id,))
            
            activities = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return activities
        except Exception as e:
            logger.error(f"Failed to get activities: {str(e)}")
            return []
