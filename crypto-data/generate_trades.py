import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NUM_TRADES = 100000
SYMBOLS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'MATIC-USD', 'AVAX-USD']
EXCHANGES = ['Coinbase', 'Binance', 'Kraken', 'Gemini']
START_DATE = datetime.now() - timedelta(days=90)
BASE_PRICES = {'BTC-USD': 45000, 'ETH-USD': 2500, 'SOL-USD': 100, 'MATIC-USD': 0.80, 'AVAX-USD': 35}

trades = []
for i in range(NUM_TRADES):
    symbol = random.choice(SYMBOLS)
    price = BASE_PRICES[symbol] * (1 + random.uniform(-0.05, 0.05))
    trades.append({
        'trade_id': f'TRADE{i:08d}',
        'symbol': symbol,
        'price': round(price, 2),
        'volume': round(random.uniform(0.001, 10.0), 8),
        'trade_type': random.choice(['buy', 'sell']),
        'exchange': random.choice(EXCHANGES),
        'timestamp': START_DATE + timedelta(seconds=random.randint(0, 90*24*60*60)),
        'user_id': f'user{random.randint(1, 1000):04d}'
    })

df = pd.DataFrame(trades).sort_values('timestamp')
df.to_parquet('crypto_trades.parquet', index=False)
print(f"✓ Generated {len(df)} trades")
print(df.head())
