#!/usr/bin/env python3

import logging
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_market_data_tool():
    """Test MarketDataTool with live TCS data and context analysis"""
    
    print("🧪 Testing MarketDataTool with live TCS data + Analysis")
    print("=" * 60)
    
    try:
        from tools.market_data import MarketDataTool
        
        # Initialize tool
        tool = MarketDataTool()
        print("✅ MarketDataTool initialized")
        
        # Fetch TCS market data
        print(f"\n📈 Fetching live TCS market data...")
        market_data = tool.get_stock_data("TCS")
        
        if not market_data:
            print(f"❌ Failed to fetch market data")
            return False
            
        print(f"\n💰 TCS Market Data:")
        print(f"   Current Price: ₹{market_data.current_price:,.2f}")
        print(f"   Price Change: ₹{market_data.price_change:+.2f} ({market_data.price_change_percent:+.2f}%)")
        print(f"   Volume: {market_data.volume:,}")
        print(f"   Market Cap: ₹{market_data.market_cap:,.0f} Crores" if market_data.market_cap else "   Market Cap: Not available")
        print(f"   P/E Ratio: {market_data.pe_ratio:.1f}" if market_data.pe_ratio else "   P/E Ratio: Not available")
        print(f"   52-Week Range: ₹{market_data.week_52_low:,.2f} - ₹{market_data.week_52_high:,.2f}")
        
        # Test market context analysis
        print(f"\n🧠 Analyzing market context...")
        market_context = tool.analyze_market_context(market_data)
        
        if market_context:
            print(f"\n📊 Market Analysis:")
            print(f"   Valuation: {market_context.current_valuation.upper()}")
            print(f"   Momentum: {market_context.price_momentum.upper()}")
            print(f"   Risk Level: {market_context.risk_level.upper()}")
            print(f"   Position vs 52W High: -{market_context.price_vs_52w_high:.1f}%")
            print(f"   Position vs 52W Low: +{market_context.price_vs_52w_low:.1f}%")
            
            print(f"\n💡 Key Insights:")
            for i, observation in enumerate(market_context.key_observations, 1):
                print(f"   {i}. {observation}")
            
            print(f"\n🎉 Complete market analysis successful!")
            return True
        else:
            print(f"❌ Market context analysis failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure yfinance is installed: pip install yfinance")
        return False
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_market_data_tool()
    sys.exit(0 if success else 1)