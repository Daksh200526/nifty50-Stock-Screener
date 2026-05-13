import yfinance as yf
import pandas as pd
import time

# Nifty 50 tickers (NSE format)
NIFTY50_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "TECHM.NS",
    "BAJAJFINSV.NS", "NESTLEIND.NS", "TATAMOTORS.NS", "ADANIENT.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "INDUSINDBK.NS", "COALINDIA.NS", "DRREDDY.NS", "CIPLA.NS",
    "HINDALCO.NS", "GRASIM.NS", "DIVISLAB.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "BRITANNIA.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", "HEROMOTOCO.NS",
    "BPCL.NS", "SHRIRAMFIN.NS", "BAJAJ-AUTO.NS", "UPL.NS", "ADANIPORTS.NS"
]

def fetch_fundamentals(tickers):
    records = []

    for ticker_sym in tickers:
        print(f"Fetching {ticker_sym}...")
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info

            records.append({
                "Ticker":          ticker_sym,
                "Company":         info.get("longName", "N/A"),
                "Sector":          info.get("sector", "N/A"),
                "Price":           info.get("currentPrice", None),
                "Market Cap (Cr)": round(info.get("marketCap", 0) / 1e7, 2),  # convert to Crores
                "P/E Ratio":       info.get("trailingPE", None),
                "P/B Ratio":       info.get("priceToBook", None),
                "Dividend Yield":  info.get("dividendYield", None),
                "52W High":        info.get("fiftyTwoWeekHigh", None),
                "52W Low":         info.get("fiftyTwoWeekLow", None),
                "EPS":             info.get("trailingEps", None),
            })

            time.sleep(0.5)  

        except Exception as e:
            print(f"  Failed for {ticker_sym}: {e}")
            continue

    return pd.DataFrame(records)


df = fetch_fundamentals(NIFTY50_TICKERS)

df.to_csv("nifty50_data.csv", index=False)

print("\nDone! Here's a preview:")
print(df.head(10).to_string())