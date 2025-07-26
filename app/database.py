import logging
import json
import asyncio
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration from environment
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"), 
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "financial_forecasting")
}

SQLITE_DB_PATH = "data/logs/forecast_requests.db"

class DatabaseManager:
    """Smart database manager with MySQL + SQLite fallback"""
    
    def __init__(self):
        self.db_type = None
        self.connection = None
        
    async def initialize(self):
        """Initialize database connection with auto-fallback"""
        
        # Try MySQL first if password provided
        mysql_password = MYSQL_CONFIG.get("password", "")
        if mysql_password:  # Only try MySQL if password is set
            try:
                import pymysql
                await self._init_mysql()
                self.db_type = "mysql"
                logger.info("✅ Connected to MySQL database")
                return
            except (ImportError, Exception) as e:
                logger.warning(f"MySQL not available, using SQLite fallback: {e}")
        else:
            logger.info("No MySQL password configured, using SQLite")
        
        # Fallback to SQLite (always works)
        try:
            await self._init_sqlite()
            self.db_type = "sqlite"
            logger.info("✅ Using SQLite database")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _init_mysql(self):
        """Initialize MySQL connection"""
        import pymysql
        
        # Create connection
        self.connection = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            charset='utf8mb4'
        )
        
        # Create database if not exists
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            cursor.execute(f"USE {MYSQL_CONFIG['database']}")
            
            # Create table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecast_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    endpoint VARCHAR(100) NOT NULL,
                    company_symbol VARCHAR(50) NOT NULL,
                    forecast_period VARCHAR(50),
                    request_data JSON,
                    response_data JSON,
                    processing_time DECIMAL(10,2),
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_company (company_symbol),
                    INDEX idx_created (created_at)
                )
            """)
        
        self.connection.commit()
    
    async def _init_sqlite(self):
        """Initialize SQLite connection"""
        
        # Ensure directory exists
        Path(SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection and table
        self.connection = sqlite3.connect(SQLITE_DB_PATH)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS forecast_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                company_symbol TEXT NOT NULL,
                forecast_period TEXT,
                request_data TEXT,
                response_data TEXT,
                processing_time REAL,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        
        # Create indexes for performance
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_company ON forecast_requests(company_symbol)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_created ON forecast_requests(created_at)")
        self.connection.commit()
    
    async def log_request(self, endpoint: str, request_data: Dict, 
                     response_data: Dict, processing_time: float,
                     error: Optional[str] = None):
        """Log request to database with detailed error handling"""
        
        try:
            company_symbol = request_data.get("company_symbol", "UNKNOWN")
            forecast_period = request_data.get("forecast_period", "")
            success = error is None
            
            logger.info(f"🔄 Attempting to log {company_symbol} to {self.db_type}")
            
            if self.db_type == "mysql":
                await self._log_mysql(endpoint, company_symbol, forecast_period, 
                                    request_data, response_data, processing_time, success, error)
            else:
                await self._log_sqlite(endpoint, company_symbol, forecast_period,
                                    request_data, response_data, processing_time, success, error)
                                    
            logger.info(f"✅ Successfully logged {endpoint} request for {company_symbol}")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to log {company_symbol} request: {e}")
    
    async def _log_mysql(self, endpoint, company_symbol, forecast_period, 
                    request_data, response_data, processing_time, success, error):
        """Log to MySQL with transaction safety"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO forecast_requests 
                    (endpoint, company_symbol, forecast_period, request_data, response_data, 
                    processing_time, success, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    endpoint, company_symbol, forecast_period,
                    json.dumps(request_data), json.dumps(response_data),
                    processing_time, success, error
                ))
            
            # CRITICAL: Ensure transaction is committed
            self.connection.commit()
            logger.info(f"✅ MySQL commit successful for {company_symbol}")
            
        except Exception as e:
            # Rollback on error
            self.connection.rollback()
            logger.error(f"❌ MySQL logging failed for {company_symbol}: {e}")
            raise e
    
    async def _log_sqlite(self, endpoint, company_symbol, forecast_period,
                         request_data, response_data, processing_time, success, error):
        """Log to SQLite"""
        self.connection.execute("""
            INSERT INTO forecast_requests 
            (endpoint, company_symbol, forecast_period, request_data, response_data,
             processing_time, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            endpoint, company_symbol, forecast_period,
            json.dumps(request_data), json.dumps(response_data),
            processing_time, success, error
        ))
        self.connection.commit()
    
    async def get_request_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if self.db_type == "mysql":
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM forecast_requests")
                    total_requests = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM forecast_requests WHERE success = 1")
                    successful_requests = cursor.fetchone()[0]
            else:
                cursor = self.connection.execute("SELECT COUNT(*) FROM forecast_requests")
                total_requests = cursor.fetchone()[0]
                
                cursor = self.connection.execute("SELECT COUNT(*) FROM forecast_requests WHERE success = 1")
                successful_requests = cursor.fetchone()[0]
            
            return {
                "database_type": self.db_type,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": f"{(successful_requests/total_requests*100):.1f}%" if total_requests > 0 else "0%"
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize database connection"""
    await db_manager.initialize()

async def log_request_response(endpoint: str, request_data: Dict, 
                              response_data: Dict, processing_time: float,
                              error: Optional[str] = None):
    """Log request/response to database"""
    await db_manager.log_request(endpoint, request_data, response_data, processing_time, error)

async def get_database_stats():
    """Get database statistics"""
    return await db_manager.get_request_stats()