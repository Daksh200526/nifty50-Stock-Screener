import pandas as pd

# ── 1. Load ──────────────────────────────────────────────
df = pd.read_csv("nifty50_data.csv")

# ── 2. Clean ─────────────────────────────────────────────
numeric_cols = ["Price", "Market Cap (Cr)", "P/E Ratio", "P/B Ratio",
                "Dividend Yield", "52W High", "52W Low", "EPS"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
def fix_dividend_yield(x):
    if pd.isna(x):
        return float("nan")
    if x > 10:          # clearly bad data (like 255)
        return float("nan")
    if x > 1:           # already a percentage e.g. 2.5 means 2.5%
        return x
    else:               # decimal form e.g. 0.015 means 1.5%
        return x * 100

df["Dividend Yield"] = df["Dividend Yield"].apply(fix_dividend_yield)

# ── 3. Filter functions ───────────────────────────────────
def filter_by_pe(df, min_pe, max_pe):
    return df[df["P/E Ratio"].between(min_pe, max_pe)]

def filter_by_market_cap(df, min_cap):
    return df[df["Market Cap (Cr)"] >= min_cap]

def filter_by_dividend(df, min_yield):
    return df[df["Dividend Yield"] >= min_yield]

def filter_by_52w(df, near_high=False, near_low=False):
    if near_high:
        return df[df["Price"] >= df["52W High"] * 0.90]
    if near_low:
        return df[df["Price"] <= df["52W Low"] * 1.10]
    return df

def filter_by_sector(df, sector):
    if sector == "All":
        return df
    return df[df["Sector"] == sector]

# ── 4. Signal logic ───────────────────────────────────────
def assign_signal(row):
    score = 0
    if pd.notna(row["P/E Ratio"]):
        if row["P/E Ratio"] < 20:   score += 1
        elif row["P/E Ratio"] > 40: score -= 1
    if pd.notna(row["P/B Ratio"]):
        if row["P/B Ratio"] < 3:    score += 1
        elif row["P/B Ratio"] > 7:  score -= 1
    if pd.notna(row["Dividend Yield"]):
        if row["Dividend Yield"] > 1.5: score += 1
    if pd.notna(row["EPS"]):
        if row["EPS"] > 0:   score += 1
        else:                score -= 2
    if score >= 3:   return "Green"
    elif score <= 0: return "Red"
    else:            return "Yellow"

df["Signal"] = df.apply(assign_signal, axis=1)

def compute_composite_score(row):
    """
    Score out of 100. Higher = more attractive fundamentally.
    Weightage based on importance to value investing.
    """
    score = 0

    # P/E score (30 points) — lower is better
    if pd.notna(row["P/E Ratio"]):
        if row["P/E Ratio"] < 10:    score += 30
        elif row["P/E Ratio"] < 15:  score += 25
        elif row["P/E Ratio"] < 20:  score += 20
        elif row["P/E Ratio"] < 30:  score += 10
        elif row["P/E Ratio"] < 40:  score += 5
        else:                        score += 0

    # P/B score (20 points) — lower is better
    if pd.notna(row["P/B Ratio"]):
        if row["P/B Ratio"] < 1:     score += 20
        elif row["P/B Ratio"] < 2:   score += 16
        elif row["P/B Ratio"] < 3:   score += 12
        elif row["P/B Ratio"] < 5:   score += 6
        else:                        score += 0

    # EPS score (25 points) — must be positive and high
    if pd.notna(row["EPS"]):
        if row["EPS"] > 100:   score += 25
        elif row["EPS"] > 50:  score += 20
        elif row["EPS"] > 20:  score += 15
        elif row["EPS"] > 0:   score += 8
        else:                  score += 0   # loss making

    # Dividend yield score (15 points)
    if pd.notna(row["Dividend Yield"]):
        if row["Dividend Yield"] > 3:    score += 15
        elif row["Dividend Yield"] > 2:  score += 12
        elif row["Dividend Yield"] > 1:  score += 8
        elif row["Dividend Yield"] > 0:  score += 4

    # 52-week position score (10 points) — near low = value opportunity
    if pd.notna(row["52W High"]) and pd.notna(row["52W Low"]) and pd.notna(row["Price"]):
        week_range  = row["52W High"] - row["52W Low"]
        if week_range > 0:
            position = (row["Price"] - row["52W Low"]) / week_range
            if position < 0.25:   score += 10   # near 52W low = value
            elif position < 0.50: score += 7
            elif position < 0.75: score += 4
            else:                 score += 1     # near 52W high

    return round(score, 1)


# Apply composite score
df["Composite Score"] = df.apply(compute_composite_score, axis=1)

# Sort by composite score descending
df = df.sort_values("Composite Score", ascending=False).reset_index(drop=True)

# ── 5. Test filters ───────────────────────────────────────
result = df.copy()
result = filter_by_pe(result, 5, 30)
result = filter_by_market_cap(result, 50000)
result = filter_by_sector(result, "All")

print(f"\nStocks passing filters: {len(result)}")
print(result[["Company", "Sector", "P/E Ratio", "Market Cap (Cr)", "Signal"]].to_string())

# ── 6. Save ───────────────────────────────────────────────
df.to_csv("nifty50_screened.csv", index=False)
print("\nSaved nifty50_screened.csv")

print(df["Signal"].value_counts())
print(df[["Company", "P/E Ratio", "P/B Ratio", "Dividend Yield", "EPS", "Signal"]].to_string())