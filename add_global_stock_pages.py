#!/usr/bin/env python3
"""
작업 4: 해외주식/코인 종목 페이지 추가
- 현재 한국 종목만 종목 페이지 있음 (app/stock/[code])
- 해외주식(IREN, PLTR 등), 코인(BTC, ETH, SOL 등)은 ticker 기반 페이지 필요
- getStaticPaths에 해외 종목 추가
- 차트: Yahoo Finance(해외주식), CoinGecko(코인) 가격 연동
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

SUPABASE_HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json'
}

# 해외주식/코인 구분
GLOBAL_STOCKS = {
    # 해외주식 (Yahoo Finance 티커)
    'stocks': [
        'IREN', 'PLTR', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 
        'META', 'NFLX', 'AMD', 'INTC', 'CRM', 'ADBE', 'ORCL', 'IBM',
        'MSTR', 'COIN', 'RBLX', 'SNOW', 'DDOG', 'NET', 'OKTA', 'ZS',
        'BLK', 'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS'
    ],
    # 코인 (CoinGecko ID)
    'crypto': [
        'bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot', 'chainlink',
        'litecoin', 'bitcoin-cash', 'ethereum-classic', 'monero',
        'dogecoin', 'shiba-inu', 'avalanche-2', 'polygon', 'uniswap',
        'maker', 'compound', 'aave', 'yearn-finance', 'synthetix'
    ]
}

# 종목명 매핑 (DB에서 사용되는 이름 -> 실제 티커/ID)
STOCK_MAPPING = {
    # 해외주식
    '팔란티어': 'PLTR',
    '팰런티어': 'PLTR', 
    'PLTR': 'PLTR',
    'Palantir': 'PLTR',
    
    '아이리스 에너지': 'IREN',
    '아이렌': 'IREN',
    'IREN': 'IREN',
    'Iris Energy': 'IREN',
    
    '엔비디아': 'NVDA',
    'NVDA': 'NVDA',
    'NVIDIA': 'NVDA',
    
    '테슬라': 'TSLA',
    'TSLA': 'TSLA',
    'Tesla': 'TSLA',
    
    '마이크로소프트': 'MSFT',
    '마이크로스트래티지': 'MSTR',
    'MicroStrategy': 'MSTR',
    
    # 코인
    '비트코인': 'bitcoin',
    'BTC': 'bitcoin', 
    'Bitcoin': 'bitcoin',
    
    '이더리움': 'ethereum',
    'ETH': 'ethereum',
    'Ethereum': 'ethereum',
    
    '솔라나': 'solana',
    'SOL': 'solana',
    'Solana': 'solana',
    
    '에이다': 'cardano',
    'ADA': 'cardano',
    'Cardano': 'cardano',
    
    '폴카닷': 'polkadot', 
    'DOT': 'polkadot',
    'Polkadot': 'polkadot',
    
    '체인링크': 'chainlink',
    'LINK': 'chainlink',
    'Chainlink': 'chainlink',
    
    '라이트코인': 'litecoin',
    'LTC': 'litecoin',
    'Litecoin': 'litecoin',
    
    '도지코인': 'dogecoin',
    'DOGE': 'dogecoin',
    'Dogecoin': 'dogecoin'
}

def get_all_signal_stocks():
    """모든 시그널에서 사용된 종목 조회"""
    url = f"{SUPABASE_URL}/rest/v1/influencer_signals"
    params = {'select': 'stock'}
    
    response = requests.get(url, headers=SUPABASE_HEADERS, params=params)
    
    if response.status_code == 200:
        signals = response.json()
        stocks = set(signal['stock'] for signal in signals)
        return list(stocks)
    else:
        print(f"Error getting signals: {response.status_code}")
        return []

def categorize_stocks(stocks):
    """종목을 한국주식/해외주식/코인으로 분류"""
    korean_stocks = []
    global_stocks = []
    crypto_stocks = []
    unknown_stocks = []
    
    for stock in stocks:
        # 매핑 테이블에서 찾기
        if stock in STOCK_MAPPING:
            mapped = STOCK_MAPPING[stock]
            if mapped in GLOBAL_STOCKS['stocks']:
                global_stocks.append((stock, mapped))
            elif mapped in GLOBAL_STOCKS['crypto']:
                crypto_stocks.append((stock, mapped))
            else:
                unknown_stocks.append(stock)
        
        # 직접 매칭
        elif stock in GLOBAL_STOCKS['stocks']:
            global_stocks.append((stock, stock))
        elif stock in GLOBAL_STOCKS['crypto']:
            crypto_stocks.append((stock, stock))
        
        # 한국 주식인지 확인 (6자리 숫자)
        elif stock.isdigit() and len(stock) == 6:
            korean_stocks.append(stock)
        
        # 기타 한국 주식 (한글명)
        elif any(c >= '가' and c <= '힣' for c in stock):
            korean_stocks.append(stock)
        
        else:
            unknown_stocks.append(stock)
    
    return {
        'korean': korean_stocks,
        'global': global_stocks, 
        'crypto': crypto_stocks,
        'unknown': unknown_stocks
    }

def generate_nextjs_paths():
    """Next.js getStaticPaths용 경로 생성"""
    
    # 모든 종목 조회
    all_stocks = get_all_signal_stocks()
    print(f"📊 Found {len(all_stocks)} unique stocks in signals")
    
    # 분류
    categorized = categorize_stocks(all_stocks)
    
    print(f"🇰🇷 Korean stocks: {len(categorized['korean'])}")
    print(f"🌍 Global stocks: {len(categorized['global'])}")  
    print(f"₿ Crypto: {len(categorized['crypto'])}")
    print(f"❓ Unknown: {len(categorized['unknown'])}")
    
    # Next.js paths 생성
    paths = []
    
    # 한국 주식
    for stock in categorized['korean']:
        paths.append({
            'params': {'code': stock},
            'type': 'korean',
            'name': stock
        })
    
    # 해외 주식
    for original_name, ticker in categorized['global']:
        paths.append({
            'params': {'code': ticker},
            'type': 'global_stock',
            'name': original_name,
            'ticker': ticker
        })
    
    # 코인
    for original_name, coin_id in categorized['crypto']:
        paths.append({
            'params': {'code': coin_id},
            'type': 'crypto', 
            'name': original_name,
            'coin_id': coin_id
        })
    
    return {
        'paths': paths,
        'categorized': categorized,
        'total_stocks': len(all_stocks)
    }

def create_stock_config_file(paths_data):
    """종목 설정 파일 생성 (Next.js에서 사용)"""
    
    config = {
        'korean_stocks': paths_data['categorized']['korean'],
        'global_stocks': {
            ticker: original_name for original_name, ticker in paths_data['categorized']['global']
        },
        'crypto': {
            coin_id: original_name for original_name, coin_id in paths_data['categorized']['crypto'] 
        },
        'stock_mapping': STOCK_MAPPING,
        'paths': [
            {
                'code': path['params']['code'],
                'type': path['type'],
                'name': path['name']
            }
            for path in paths_data['paths']
        ]
    }
    
    # JSON 파일로 저장
    with open('public/stock-config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("📄 Created public/stock-config.json")
    
    return config

def create_sample_page_code():
    """샘플 페이지 코드 생성"""
    
    page_code = '''// app/stock/[code]/page.tsx
import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import stockConfig from '../../../public/stock-config.json';

interface StockPageProps {
  params: { code: string };
}

export async function generateStaticParams() {
  return stockConfig.paths.map((path) => ({
    code: path.code,
  }));
}

export async function generateMetadata({ params }: StockPageProps): Promise<Metadata> {
  const stockPath = stockConfig.paths.find(p => p.code === params.code);
  
  if (!stockPath) {
    return { title: '종목을 찾을 수 없습니다' };
  }
  
  return {
    title: `${stockPath.name} 투자 시그널`,
    description: `${stockPath.name}에 대한 인플루언서 투자 시그널과 분석`,
  };
}

export default function StockPage({ params }: StockPageProps) {
  const stockPath = stockConfig.paths.find(p => p.code === params.code);
  
  if (!stockPath) {
    notFound();
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{stockPath.name}</h1>
      
      {/* 차트 컴포넌트 */}
      <div className="mb-8">
        {stockPath.type === 'korean' && (
          <KoreanStockChart code={params.code} />
        )}
        {stockPath.type === 'global_stock' && (
          <YahooFinanceChart ticker={params.code} />
        )}
        {stockPath.type === 'crypto' && (
          <CoinGeckoChart coinId={params.code} />
        )}
      </div>
      
      {/* 시그널 목록 */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">투자 시그널</h2>
        <StockSignals stockName={stockPath.name} />
      </div>
    </div>
  );
}

// 차트 컴포넌트들 (별도 파일로 분리 권장)
function KoreanStockChart({ code }: { code: string }) {
  // 한국 주식 차트 (기존 구현)
  return <div>한국주식 차트: {code}</div>;
}

function YahooFinanceChart({ ticker }: { ticker: string }) {
  // Yahoo Finance API 사용
  return <div>해외주식 차트: {ticker}</div>;
}

function CoinGeckoChart({ coinId }: { coinId: string }) {
  // CoinGecko API 사용
  return <div>코인 차트: {coinId}</div>;
}

function StockSignals({ stockName }: { stockName: string }) {
  // 해당 종목의 시그널 목록 표시
  return <div>시그널 목록: {stockName}</div>;
}'''
    
    with open('sample_stock_page.tsx', 'w', encoding='utf-8') as f:
        f.write(page_code)
    
    print("📄 Created sample_stock_page.tsx")

def main():
    print("🌍 Adding global stock pages...")
    
    # 종목 경로 생성
    paths_data = generate_nextjs_paths()
    
    print(f"\n📊 Generated {len(paths_data['paths'])} static paths:")
    print(f"  Korean stocks: {len([p for p in paths_data['paths'] if p['type'] == 'korean'])}")
    print(f"  Global stocks: {len([p for p in paths_data['paths'] if p['type'] == 'global_stock'])}")
    print(f"  Crypto: {len([p for p in paths_data['paths'] if p['type'] == 'crypto'])}")
    
    # 설정 파일 생성
    config = create_stock_config_file(paths_data)
    
    # 샘플 코드 생성
    create_sample_page_code()
    
    # 미지의 종목 리스트
    if paths_data['categorized']['unknown']:
        print(f"\n❓ Unknown stocks need manual classification:")
        for stock in paths_data['categorized']['unknown'][:10]:  # 처음 10개만
            print(f"  {stock}")
    
    # 결과 저장
    result = {
        'total_stocks': paths_data['total_stocks'],
        'korean_stocks': len(paths_data['categorized']['korean']),
        'global_stocks': len(paths_data['categorized']['global']),
        'crypto_stocks': len(paths_data['categorized']['crypto']),
        'unknown_stocks': len(paths_data['categorized']['unknown']),
        'generated_paths': len(paths_data['paths']),
        'unknown_list': paths_data['categorized']['unknown'],
        'timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('global_stock_pages_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Global stock pages setup completed!")
    print(f"  Results saved to global_stock_pages_result.json")
    print(f"  Stock config saved to public/stock-config.json")
    print(f"  Sample code saved to sample_stock_page.tsx")

if __name__ == "__main__":
    main()