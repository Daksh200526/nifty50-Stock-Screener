import pandas as pd

# ── 1. Load ───────────────────────────────────────────────
df = pd.read_csv("nifty50_data.csv")

# ── 2. Clean ──────────────────────────────────────────────
numeric_cols = [
    "Price", "Market Cap (Cr)", "P/E Ratio", "Forward P/E",
    "P/B Ratio", "PEG Ratio", "EV/EBITDA", "EPS",
    "ROE (%)", "ROA (%)", "Profit Margin (%)", "Operating Margin (%)",
    "Revenue Growth (%)", "Earnings Growth (%)",
    "Debt/Equity", "Current Ratio", "Free Cash Flow (Cr)",
    "Dividend Yield", "52W High", "52W Low",
    "Promoter Holding (%)", "Inst. Holding (%)"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Dividend yield — already in % from fetch_data.py
# Cap anything unrealistic
df["Dividend Yield"] = df["Dividend Yield"].apply(
    lambda x: float("nan") if pd.isna(x) or x > 10 else x
)

# ── 3. Signal logic ───────────────────────────────────────
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

    if pd.notna(row["ROE (%)"]):
        if row["ROE (%)"] > 15:   score += 1
        elif row["ROE (%)"] < 5:  score -= 1

    if pd.notna(row["Debt/Equity"]):
        if row["Debt/Equity"] < 1:  score += 1
        elif row["Debt/Equity"] > 2: score -= 1

    if score >= 4:   return "Green"
    elif score <= 0: return "Red"
    else:            return "Yellow"

df["Signal"] = df.apply(assign_signal, axis=1)

# ── 4. Composite score ────────────────────────────────────
def compute_composite_score(row):
    score = 0

    # P/E (25 points)
    if pd.notna(row["P/E Ratio"]):
        if row["P/E Ratio"] < 10:    score += 25
        elif row["P/E Ratio"] < 15:  score += 20
        elif row["P/E Ratio"] < 20:  score += 15
        elif row["P/E Ratio"] < 30:  score += 8
        elif row["P/E Ratio"] < 40:  score += 3

    # P/B (15 points)
    if pd.notna(row["P/B Ratio"]):
        if row["P/B Ratio"] < 1:     score += 15
        elif row["P/B Ratio"] < 2:   score += 12
        elif row["P/B Ratio"] < 3:   score += 8
        elif row["P/B Ratio"] < 5:   score += 4

    # ROE (20 points)
    if pd.notna(row["ROE (%)"]):
        if row["ROE (%)"] > 25:   score += 20
        elif row["ROE (%)"] > 20: score += 16
        elif row["ROE (%)"] > 15: score += 12
        elif row["ROE (%)"] > 10: score += 6

    # EPS (10 points)
    if pd.notna(row["EPS"]):
        if row["EPS"] > 100:   score += 10
        elif row["EPS"] > 50:  score += 8
        elif row["EPS"] > 20:  score += 5
        elif row["EPS"] > 0:   score += 2

    # Dividend yield (10 points)
    if pd.notna(row["Dividend Yield"]):
        if row["Dividend Yield"] > 3:    score += 10
        elif row["Dividend Yield"] > 2:  score += 8
        elif row["Dividend Yield"] > 1:  score += 5
        elif row["Dividend Yield"] > 0:  score += 2

    # Debt/Equity (10 points)
    if pd.notna(row["Debt/Equity"]):
        if row["Debt/Equity"] < 0.5:  score += 10
        elif row["Debt/Equity"] < 1:  score += 7
        elif row["Debt/Equity"] < 2:  score += 3

    # 52W position (10 points)
    if pd.notna(row["52W High"]) and pd.notna(row["52W Low"]) and pd.notna(row["Price"]):
        week_range = row["52W High"] - row["52W Low"]
        if week_range > 0:
            position = (row["Price"] - row["52W Low"]) / week_range
            if position < 0.25:    score += 10
            elif position < 0.50:  score += 7
            elif position < 0.75:  score += 4
            else:                  score += 1

    return round(score, 1)

df["Composite Score"] = df.apply(compute_composite_score, axis=1)

# Sort by composite score
df = df.sort_values("Composite Score", ascending=False).reset_index(drop=True)

# ── 5. Save ───────────────────────────────────────────────
df.to_csv("nifty50_screened.csv", index=False)

print(f"Saved {len(df)} stocks to nifty50_screened.csv")
print(f"\nSignal distribution:")
print(df["Signal"].value_counts())
print(f"\nTop 10 by Composite Score:")
print(df[["Company", "P/E Ratio", "ROE (%)", "Composite Score", "Signal"]].head(10).to_string())