# incomplete-trading-bot — Security Review

## ⚠️ CRITICAL: Real Money Trading Risk

This is an **algorithmic trading bot** that interacts with real financial APIs. Misconfiguration, bugs, or market conditions could result in significant financial losses. Review carefully before any use.

---

## CRITICAL: Hardcoded API Keys Pattern

**File:** `gvars.py` (lines 18-21)
```python
API_KEY = ""
API_SECRET_KEY = ""
```

The code checks for empty keys and raises `ValueError` at startup — good. However, if a user edits `gvars.py` to add their API key, that file could be accidentally committed to version control, exposing live trading credentials.

**Recommendation:** Use environment variables instead of editing `gvars.py`:
```python
import os
API_KEY = os.environ.get("ALPACA_API_KEY", "")
API_SECRET_KEY = os.environ.get("ALPACA_API_SECRET_KEY", "")
```

## HIGH: Uses Paper Trading URL by Default (Safe But Misleading)

**File:** `gvars.py` (line 21)
```python
ALPACA_API_URL = "https://paper-api.alpaca.markets"
```

This is actually safe — it defaults to paper trading. However, there's no guard preventing someone from switching to the live endpoint (`https://api.alpaca.markets`) without realizing it.

**Risk:** User switches to live URL, bot makes real trades with real money.

## HIGH: No Order Price Validation

**File:** `traderlib.py` (lines 200-230)
```python
limit_price = orderDict['limit_price'] * (1+self.pctMargin)
```

No check that the adjusted limit price is within reasonable bounds (e.g., not 10× the current price). A bug in upstream price calculation could result in vastly overpriced orders.

**Recommendation:** Add price sanity checks:
```python
if limit_price > current_price * 1.5 or limit_price < current_price * 0.5:
    raise ValueError("Adjusted limit price too far from market")
```

## MEDIUM: Thread Safety — AssetHandler Race Condition

**File:** `assetHandler.py` (lines 39-53)
```python
self.availableAssets = self.tradeableAssets
self.availableAssets -= self.usedAssets
...
chosenAsset = random.choice(list(self.availableAssets))
```

Between checking `availableAssets` and calling `random.choice()`, another thread could modify `usedAssets` or `lockedAssets`. While Python set operations are atomic, the compound operations here are not.

**Risk:** Race condition could cause the same asset to be selected by multiple threads simultaneously.

## MEDIUM: No Rate Limiting Against Alpaca API

**File:** `traderlib.py`  
The code has aggressive polling loops:
- `get_last_price()`: `time.sleep(10)` retry — could be 10+ seconds
- `load_historical_data()`: `time.sleep(gvars.sleepTimes['LH'])` = 5 seconds between retries
- `get_general_trend()`: `time.sleep(gvars.sleepTimes['GT'])` = 10 minutes

Alpaca has rate limits (~200 requests/minute for market data). With 10 workers, this could be exceeded, resulting in API errors.

**Recommendation:** Use Alpaca's WebSocket stream for real-time data instead of polling.

## LOW: Bundled alpaca_trade_api SDK

**File:** `alpaca_trade_api/` directory  
The repository includes a bundled copy of `alpaca_trade_api` rather than installing from PyPI. This copy may have known security vulnerabilities that have been patched in the official package.

**Recommendation:** Delete the bundled SDK and use `pip install alpaca-trade-api`.

## LOW: No Input Validation on `_raw_assets.csv`

**File:** `assetHandler.py` (line 25)
```python
self.rawAssets = set(pd.read_csv(gvars.RAW_ASSETS))
```

No validation that the CSV contains valid ticker symbols. Malformed data could cause crashes or unexpected behavior.

## Info: `block_thread()` Creates Unkillable Process

**File:** `other_functions.py` (lines 19-31)  
`block_thread()` runs an infinite `while True` loop with `time.sleep(10)`. This cannot be terminated via Python's standard `Thread.join()` mechanism. If called, the thread will run until the entire process is killed.

**Risk:** A single fatal error could cause one worker to block forever, creating a zombie thread.

## Summary Table

| Issue | Severity | Status |
|-------|----------|--------|
| API key storage in source file | HIGH | Must use env vars |
| No order price validation | HIGH | Open |
| AssetHandler race condition | MEDIUM | Open |
| No API rate limiting | MEDIUM | Open |
| Bundled alpaca_trade_api SDK | LOW | Replace with PyPI |
| `block_thread()` unkillable | LOW | Open |
| CSV input not validated | LOW | Open |
| Paper→Live URL switch risk | LOW | Add guard |