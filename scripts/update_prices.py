"""
Signal prices update script - comprehensive version
Updates signal_prices.json with complete price data from yfinance
Covers Korean stocks, US stocks, and crypto
"""
import requests, json, time, os
import yfinance as yf
from datetime import datetime, timedelta

# Supabase config
BASE = 'https://arypzhotxflimroprmdk.supabase.co/rest/v1/'
KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMDYxMTAsImV4cCI6MjA4NzU4MjExMH0.qcqFIvYRiixwu609Wjj9H3HxscU8vNpo9nS_KQ3f00A'
HEADERS = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}

# Ticker mapping rules
TICKER_MAP = {
    # Korean stocks
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS',
    '현대차': '005380.KS',
    '현대건설': '000720.KS',
    '네이버': '035420.KS',
    '삼성바이오로직스': '207940.KS',
    '삼성SDI': '006400.KS',
    'LG화학': '051910.KS',
    'NC소프트': '036570.KS',
    '현대모비스': '012330.KS',
    '아모레퍼시픽': '090430.KS',
    '신세계': '004170.KS',
    'CGV': '079160.KS',
    '코스모신소재': '005070.KS',
    '두산에너빌리티': '034020.KS',
    'LS일렉트릭': '010120.KS',
    'HD현대일렉트릭': '267260.KS',
    '효성중공업': '298040.KS',
    '주성엔지니어링': '036930.KQ',
    '한미반도체': '042700.KQ',
    '테스': '095610.KQ',
    'HPSP': '403870.KQ',
    '원익IPS': '240810.KQ',
    '레인보우로보틱스': '277810.KQ',
    
    # US stocks
    '엔비디아': 'NVDA',
    'NVIDIA': 'NVDA',
    '테슬라': 'TSLA',
    'TSMC': 'TSM',
    'ASML': 'ASML',
    '마이크론': 'MU',
    'Micron': 'MU',
    '구글': 'GOOGL',
    '알파벳': 'GOOGL',
    'Alphabet': 'GOOGL',
    'Google': 'GOOGL',
    'AMD': 'AMD',
    'Intel': 'INTC',
    '인텔': 'INTC',
    'Apple': 'AAPL',
    '애플': 'AAPL',
    'Microsoft': 'MSFT',
    '마이크로소프트': 'MSFT',
    'Amazon': 'AMZN',
    '아마존': 'AMZN',
    
    # Crypto
    '비트코인': 'BTC-USD',
    'BTC': 'BTC-USD',
    'Bitcoin': 'BTC-USD',
    '이더리움': 'ETH-USD',
    'ETH': 'ETH-USD',
    'Ethereum': 'ETH-USD',
}

def get_price_at_date(ticker, date_str):
    """Get closing price at specific date"""
    try:
        dt = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
        start = dt - timedelta(days=7)  # Buffer for weekends/holidays
        end = dt + timedelta(days=3)
        
        yfin = yf.Ticker(ticker)
        hist = yfin.history(start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
        
        if hist.empty:
            return None
            
        # Remove timezone for comparison
        hist.index = hist.index.tz_localize(None)
        
        # Get closest price before or on the date
        before_or_on = hist[hist.index <= dt]
        if not before_or_on.empty:
            return float(before_or_on.iloc[-1]['Close'])
        
        # If no data before, get first available
        return float(hist.iloc[0]['Close'])
        
    except Exception as e:
        print(f"    Error getting price for {ticker} at {date_str}: {e}")
        return None

def get_current_price(ticker):
    """Get current/latest price"""
    try:
        yfin = yf.Ticker(ticker)
        hist = yfin.history(period='5d')
        
        if hist.empty:
            return None
            
        return float(hist.iloc[-1]['Close'])
        
    except Exception as e:
        print(f"    Error getting current price for {ticker}: {e}")
        return None

def load_existing_data():
    """Load existing signal_prices.json if it exists"""
    data_path = 'data/signal_prices.json'
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return {}

def save_data(data):
    """Save data to signal_prices.json"""
    os.makedirs('data', exist_ok=True)
    with open('data/signal_prices.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_signals():
    """Get all signals from Supabase with video data"""
    try:
        # Get signals with video published_at data
        url = BASE + 'influencer_signals?select=id,stock,ticker,market,signal,created_at,influencer_videos(published_at)'
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching signals: {e}")
        return []

def main():
    print("Starting signal prices update...")
    
    # Load existing data
    existing_data = load_existing_data()
    print(f"Loaded {len(existing_data)} existing price records")
    
    # Get all signals
    signals = get_all_signals()
    print(f"Found {len(signals)} total signals")
    
    if not signals:
        print("No signals found")
        return
    
    updated_data = existing_data.copy()
    stats = {'success': 0, 'skipped': 0, 'failed': 0}
    
    # Process in batches of 10
    for i in range(0, len(signals), 10):
        batch = signals[i:i+10]
        print(f"\nProcessing batch {i//10 + 1} ({i+1}-{min(i+10, len(signals))})...")
        
        for signal in batch:
            signal_id = signal['id']
            stock_name = signal['stock']
            market = signal['market']
            
            # Check if we already have complete data
            existing = updated_data.get(signal_id, {})
            if (existing.get('return_pct') is not None and 
                existing.get('return_pct') != "-" and
                existing.get('updated_at') == datetime.now().strftime('%Y-%m-%d')):
                print(f"  SKIP: {stock_name}: Already updated today")
                stats['skipped'] += 1
                continue
            
            # Map ticker
            ticker = TICKER_MAP.get(stock_name)
            if not ticker:
                # Check if it's a sector/ETF that should be skipped
                if any(keyword in stock_name.lower() for keyword in ['섹터', '셀', 'etf', '펀드']):
                    print(f"  SKIP: {stock_name}: Sector/ETF - skipped")
                    stats['skipped'] += 1
                    continue
                else:
                    print(f"  SKIP: {stock_name}: No ticker mapping")
                    stats['skipped'] += 1
                    continue
            
            # Get date - prefer published_at, fallback to created_at
            video_data = signal.get('influencer_videos')
            date_str = None
            if video_data and video_data.get('published_at'):
                date_str = video_data['published_at']
            else:
                date_str = signal['created_at']
            
            if not date_str:
                print(f"  FAIL: {stock_name}: No date found")
                stats['failed'] += 1
                continue
            
            try:
                print(f"  PROC: {stock_name} ({ticker})...")
                
                # Get prices
                price_at_signal = get_price_at_date(ticker, date_str)
                current_price = get_current_price(ticker)
                
                # Calculate return
                return_pct = None
                if price_at_signal and current_price:
                    return_pct = round((current_price - price_at_signal) / price_at_signal * 100, 2)
                
                # Update data
                if price_at_signal or current_price:
                    updated_data[signal_id] = {
                        'signal_id': signal_id,
                        'ticker': ticker,
                        'price_at_signal': price_at_signal,
                        'current_price': current_price,
                        'return_pct': return_pct,
                        'updated_at': datetime.now().strftime('%Y-%m-%d')
                    }
                    print(f"    OK: {price_at_signal} -> {current_price} ({return_pct}%)")
                    stats['success'] += 1
                else:
                    print(f"    FAIL: No price data available")
                    stats['failed'] += 1
                
            except Exception as e:
                print(f"    FAIL: Error processing {stock_name}: {e}")
                stats['failed'] += 1
        
        # Delay between batches
        if i + 10 < len(signals):
            print("Waiting 1 second...")
            time.sleep(1)
    
    # Save updated data
    save_data(updated_data)
    print(f"\nSaved {len(updated_data)} records to data/signal_prices.json")
    
    # Summary
    print(f"\nSummary:")
    print(f"  Success: {stats['success']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total records: {len(updated_data)}")

if __name__ == '__main__':
    main()