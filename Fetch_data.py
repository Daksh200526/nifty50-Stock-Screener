import yfinance as yf
import pandas as pd
import time

NIFTY150_TICKERS = [
    # Nifty 50
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS", "TECHM.NS",
    "BAJAJFINSV.NS", "NESTLEIND.NS", "TATAMOTORS.NS", "ADANIENT.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "INDUSINDBK.NS", "COALINDIA.NS", "DRREDDY.NS", "CIPLA.NS",
    "HINDALCO.NS", "GRASIM.NS", "DIVISLAB.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "BRITANNIA.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", "HEROMOTOCO.NS",
    "BPCL.NS", "SHRIRAMFIN.NS", "BAJAJ-AUTO.NS", "UPL.NS", "ADANIPORTS.NS",

    # Nifty Next 50
    "SIEMENS.NS", "HAVELLS.NS", "DABUR.NS", "MARICO.NS", "BERGEPAINT.NS",
    "PIDILITIND.NS", "LUPIN.NS", "TORNTPHARM.NS", "AMBUJACEM.NS", "ACC.NS",
    "BANDHANBNK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS", "BANKBARODA.NS",
    "CANBK.NS", "UNIONBANK.NS", "SAIL.NS", "NMDC.NS", "VEDL.NS",
    "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS", "DMART.NS", "TRENT.NS",
    "JUBLFOOD.NS", "MCDOWELL-N.NS", "UNITDSPR.NS", "RADICO.NS", "TATAPOWER.NS",
    "ADANIGREEN.NS", "ADANITRANS.NS", "ADANIGAS.NS", "IGL.NS", "MGL.NS",
    "GUJGASLTD.NS", "CONCOR.NS", "IRCTC.NS", "INDIANB.NS", "OBEROIRLTY.NS",
    "DLF.NS", "GODREJPROP.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS",

    # Nifty Midcap
    "MPHASIS.NS", "LTTS.NS", "PERSISTENT.NS", "COFORGE.NS", "KPITTECH.NS",
    "TATAELXSI.NS", "HAPPSTMNDS.NS", "VOLTAS.NS", "BLUESTARCO.NS", "CROMPTON.NS",
    "DIXON.NS", "AMBER.NS", "VGUARD.NS", "POLYCAB.NS", "KEI.NS",
    "APLAPOLLO.NS", "RATNAMANI.NS", "ASTRAL.NS", "PRINCEPIPE.NS", "SUPREMEIND.NS",
    "PAGEIND.NS", "RELAXO.NS", "BATA.NS", "ABFRL.NS", "RAYMOND.NS",
    "ALKEM.NS", "GRANULES.NS", "LALPATHLAB.NS", "METROPOLIS.NS", "MAXHEALTH.NS",
    "NH.NS", "FORTIS.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS",
    "SUNDARMFIN.NS", "AAVAS.NS", "HOMEFIRST.NS", "CANFINHOME.NS", "POONAWALLA.NS",
    "CREDITACC.NS", "MOTILALOFS.NS", "ANGELONE.NS", "BSE.NS", "MCX.NS",
    "CDSL.NS", "CRISIL.NS", "ICICIPRULI.NS", "HDFCAMC.NS", "NIPPONLIFE.NS",
    "ICICIGI.NS", "GICRE.NS", "NIACL.NS", "STARHEALTH.NS", "POLICYBZR.NS",
]


def fetch_fundamentals(tickers):
    records = []
    failed  = []

    for i, ticker_sym in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] Fetching {ticker_sym}...")
        try:
            ticker = yf.Ticker(ticker_sym)
            info   = ticker.info

            # Skip if no useful data returned
            if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
                print(f"  Skipping {ticker_sym} — no data")
                failed.append(ticker_sym)
                continue

            # Dividend yield fix
            raw_div = info.get("dividendYield", None)
            if raw_div is not None:
                if raw_div > 10:
                    raw_div = None  # bad data

            # ROE / ROA / Margins
            roe = info.get("returnOnEquity", None)
            roa = info.get("returnOnAssets", None)
            pm  = info.get("profitMargins", None)
            om  = info.get("operatingMargins", None)
            rg  = info.get("revenueGrowth", None)
            eg  = info.get("earningsGrowth", None)
            ph  = info.get("heldPercentInsiders", None)
            ih  = info.get("heldPercentInstitutions", None)
            fcf = info.get("freeCashflow", None)

            records.append({
                "Ticker":               ticker_sym,
                "Company":              info.get("longName", "N/A"),
                "Sector":               info.get("sector", "N/A"),
                "Industry":             info.get("industry", "N/A"),

                # Price
                "Price":                info.get("currentPrice", None),
                "52W High":             info.get("fiftyTwoWeekHigh", None),
                "52W Low":              info.get("fiftyTwoWeekLow", None),

                # Size
                "Market Cap (Cr)":      round(info.get("marketCap", 0) / 1e7, 2),

                # Valuation
                "P/E Ratio":            info.get("trailingPE", None),
                "Forward P/E":          info.get("forwardPE", None),
                "P/B Ratio":            info.get("priceToBook", None),
                "PEG Ratio":            info.get("pegRatio", None),
                "EV/EBITDA":            info.get("enterpriseToEbitda", None),
                "EPS":                  info.get("trailingEps", None),

                # Profitability
                "ROE (%)":              round(roe * 100, 2) if roe else None,
                "ROA (%)":              round(roa * 100, 2) if roa else None,
                "Profit Margin (%)":    round(pm  * 100, 2) if pm  else None,
                "Operating Margin (%)": round(om  * 100, 2) if om  else None,
                "Revenue Growth (%)":   round(rg  * 100, 2) if rg  else None,
                "Earnings Growth (%)":  round(eg  * 100, 2) if eg  else None,

                # Financial health
                "Debt/Equity":          info.get("debtToEquity", None),
                "Current Ratio":        info.get("currentRatio", None),
                "Free Cash Flow (Cr)":  round(fcf / 1e7, 2) if fcf else None,

                # Dividend
                "Dividend Yield":       raw_div,

                # Holding pattern
                "Promoter Holding (%)": round(ph * 100, 2) if ph else None,
                "Inst. Holding (%)":    round(ih * 100, 2) if ih else None,
            })

        except Exception as e:
            print(f"  Error for {ticker_sym}: {e}")
            failed.append(ticker_sym)

        time.sleep(0.5)  # be polite to the API

    print(f"\nFetched: {len(records)} | Failed: {len(failed)}")
    if failed:
        print(f"Failed tickers: {failed}")

    return pd.DataFrame(records)


# Run
df = fetch_fundamentals(NIFTY150_TICKERS)
df.to_csv("nifty50_data.csv", index=False)
print(f"\nSaved {len(df)} stocks to nifty50_data.csv")
print(df.head(5).to_string())