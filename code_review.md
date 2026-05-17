# incomplete-trading-bot — Code Review

## ⚠️ WARNING: This Repository Contains Active Trading Code

**Exercise extreme caution. This code places real orders via the Alpaca API. A misconfiguration can result in real financial losses.**

---

## Overview
**Repo:** thotasos/incomplete-trading-bot  
**Purpose:** Alpaca-based algorithmic trading bot using EMA crossover, RSI, and stochastic indicators  
**Language:** Python  
**Forked from:** alpaca-finance/alpaca-green-trading-bot  
**Status:** Incomplete/unmaintained

## Components

| File | Purpose |
|------|---------|
| `tbot.py` | Main entry point, multi-threaded worker orchestration |
| `traderlib.py` | Core `Trader` class — order submission, position management, indicator calculations |
| `gvars.py` | Global configuration constants (API keys, timeouts, limits) |
| `stocklib.py` | Simple `Stock` dataclass |
| `assetHandler.py` | `AssetHandler` — manages tradeable/locked/used asset sets |
| `other_functions.py` | Logging helpers, param loading, folder creation |
| `alpaca_trade_api/` | Bundled Alpaca SDK (forked/modified copy, NOT the official package) |

## Architecture
- Multi-threaded: `MAX_WORKERS` threads each running `run_tbot()`
- Each thread has its own `Trader` instance sharing the same Alpaca API connection
- Asset selection is **random** among available assets — not based on any analysis
- Entry signals: EMA crossover (9/26/50) confirmed by RSI and Stochastic
- Exit: stop-loss (EMA50) and take-profit (1.5× risk ratio)
- **NOTE:** Uses paper-trading API URL by default (`https://paper-api.alpaca.markets`)

## Key Code Issues

### Critical
- **`is` comparison for string values** — `direction is 'buy'` (line 47, 78, 204, 208, etc.) uses identity comparison instead of `==`. Python may not intern these strings, so comparisons could silently fail. Example: `if direction is 'buy'` would be `False` even when `direction == 'buy'` is `True`.
- **Bare `except:` clauses** — Most functions have bare `except:` that catch ALL exceptions including `KeyboardInterrupt`, `SystemExit`, and `MemoryError`. This masks bugs and prevents proper shutdown.
- **`pdb.set_trace()` left in code** — `tbot.py` line 76: `import pdb; pdb.set_trace()`. If reached, drops into interactive debugger, blocking the thread.
- **Infinite blocking on `block_thread()`** — `other_functions.block_thread()` loops forever with no escape mechanism.

### High
- **No position size limits** — `operEquity = 10000` means each order could be $10K. Combined with leverage, losses could be substantial.
- **No API key validation** — If `gvars.API_KEY` is empty string, it raises `ValueError` at startup — good. But no check if keys are valid.
- **No rate limiting on Alpaca API** — The code polls aggressively (`load_historical_data` in tight loops). Could hit Alpaca rate limits.
- **`get_barset` deprecated** — Alpaca REST API v2 no longer supports `get_barset`. This code uses the old API. Live trading would fail.

### Medium
- **Global mutable state in `AssetHandler`** — `usedAssets`, `lockedAssets` etc. are shared across threads without locks. Python set operations are atomic but compound operations (check-then-modify) are not. Race conditions possible.
- **No order fill verification** — After `submit_order`, no check that the order actually filled before setting stop-loss/take-profit.
- **`time.sleep` in `unlock_assets` loop** — Unlocks ALL locked assets after 10 minutes regardless of individual lock reasons.
- **Missing dependency: `tulipy`** — Technical indicator library used throughout but not in `requirements.txt`.
- **No virtual environment support** — No `requirements.txt` or `setup.py` for dependencies.

### Low
- **`# encoding: utf-8` on every file** — Unnecessary in Python 3 (UTF-8 is default).
- **Hardcoded paper trading URL** — Good for safety, but no way to switch to live without code modification.
- **`PARAMS_PATH` referenced but not defined in `gvars.py`** — `other_functions.py` line 84 references `gvars.PARAMS_PATH` which doesn't exist in gvars.
- **Commented-out code** — Large blocks of commented code remain in the repository.
- **No type hints** — Entire codebase uses no type annotations.

## Security Notes
- API keys stored in `gvars.py` (not environment). While empty by default, if someone fills them in, the file could be committed.
- API keys passed to `tradeapi.REST()` — not stored in plain text files at runtime.
- No input validation on `_raw_assets.csv` — if tampered with, could cause unexpected behavior.
- Uses bundled `alpaca_trade_api` instead of the official PyPI package — could have unpatched vulnerabilities.