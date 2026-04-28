---
name: Cache Management Rules
description: Critical rules for cache management to prevent sample data caching
---

# Cache Management Rules - MUST FOLLOW

## Core Principle
**NEVER cache sample/generated data. Only cache real API data.**

## Critical Rules

### Rule 1: Sample Data Must Never Be Cached
- When AKShare API fails, return sample data but DO NOT cache it
- Sample data is for emergency fallback only
- Users must retry API on every call when API is failing

### Rule 2: Clear Cache on Every Run (Development/Debug)
- Use `start_final.bat --clear-cache` to ensure clean state
- Clear ALL cache types: JSON, logs, pycache, temporary files
- Never remove this cache clearing logic

### Rule 3: API Failure Handling
- When API returns error/None: log error, return sample data (no cache)
- When API succeeds: validate data quality, then cache only if valid
- Always retry API on subsequent calls (don't use cached sample data)

## Implementation Details

### Cache Clearing Locations
1. `start_final.bat` - Main startup script with --clear-cache option
2. `clear_cache.bat` - Standalone cache clearing script
3. `clear_cache.py` - Python programmatic cache clearing
4. `CacheManager.clear_all()` - Programmatic cache clearing

### Files/Directories to Clear
- `data/cache/*.json` - Main cache files
- `data/cache/*.log` - Error logs
- `data/processed_data/*` - Processed data cache
- `**/__pycache__` - Python cache directories
- `*.tmp`, `*.temp` - Temporary files

### Cache Keys Used
- `(stock_code, "financial", period)` - Main financial data cache
- `f"{stock_code}_a_financial_{period}"` - A股 specific cache
- `f"{stock_code}_hk_financial_{period}"` - 港股 specific cache

## Error Scenarios

### AKShare API Failures (Current State)
- `stock_profit_sheet_by_report_em`: 'NoneType' object is not subscriptable
- `stock_balance_sheet_by_report_em`: 'NoneType' object is not subscriptable  
- `stock_cash_flow_sheet_by_report_em`: 'NoneType' object is not subscriptable
- `stock_info_search_code`: module has no attribute (removed in new version)

### Expected Behavior During API Failures
1. First click: API call → failure → sample data (no cache)
2. Second click: API call → failure → sample data (no cache)
3. Response times should be similar (indicating API retry)

## Validation Checklist
- [ ] Sample data is never cached
- [ ] API is retried on every call when failing
- [ ] Cache clearing scripts exist and work
- [ ] Error logging captures all API failures
- [ ] Real data is cached only when successfully retrieved

## Future Considerations
- If AKShare API recovers, system should automatically start caching real data
- Cache TTL should be reasonable (currently 7 days)
- Cache validation should ensure data quality before caching

**IMPORTANT: Never remove or disable cache clearing logic. This is critical for system reliability.**