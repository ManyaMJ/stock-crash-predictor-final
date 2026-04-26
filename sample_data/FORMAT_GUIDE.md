# Expected CSV Format

Your CSV file must have at minimum the following columns (case-insensitive):

| Column | Description | Required |
|--------|-------------|----------|
| Date   | Trading date (any standard format) | Recommended |
| Open   | Opening price | ✅ Yes |
| High   | Daily high price | ✅ Yes |
| Low    | Daily low price | ✅ Yes |
| Close  | Closing price | ✅ Yes |
| Volume | Trading volume | Optional |

## Example row:
```
Date,Open,High,Low,Close,Volume
2020-01-02,12182.50,12311.20,12168.35,12282.20,185400000
```

## Notes:
- Minimum 100 rows required
- Data is auto-sorted by date (oldest first)
- NIFTY 50 data can be downloaded from NSE India or Yahoo Finance (^NSEI)
