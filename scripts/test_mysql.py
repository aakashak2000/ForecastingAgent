#!/usr/bin/env python3
"""
Test MySQL integration specifically
"""

import sys
import asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

async def test_mysql_connection():
    """Test MySQL database connection and logging"""
    print("🗄️ TESTING MYSQL DATABASE INTEGRATION")
    print("=" * 50)
    
    try:
        from app.database import DatabaseManager
        
        # Force MySQL connection
        db = DatabaseManager()
        await db.initialize()
        
        if db.db_type == "mysql":
            print("✅ MySQL connection successful")
            
            # Test logging functionality
            test_request = {"company_symbol": "TCS", "forecast_period": "Q2-2025"}
            test_response = {"recommendation": "BUY", "confidence": 0.85}
            
            await db.log_request("/forecast", test_request, test_response, 45.5)
            print("✅ Request logging successful")
            
            # Test stats retrieval
            stats = await db.get_request_stats()
            print(f"✅ Database stats: {stats}")
            
            return True
        else:
            print(f"❌ Expected MySQL but got: {db.db_type}")
            return False
            
    except Exception as e:
        print(f"❌ MySQL test failed: {e}")
        print("💡 Make sure MySQL is installed and running")
        print("💡 Database and user created as shown above")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mysql_connection())
    
    if success:
        print("\n🎉 MySQL integration working perfectly!")
        print("✅ Ready for production deployment")
    else:
        print("\n⚠️ MySQL setup needed - see instructions above")
    
    sys.exit(0 if success else 1)