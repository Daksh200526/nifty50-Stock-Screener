import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import ta as ta_lib

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Nifty 150 Stock Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark theme CSS ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0a0a0f !important;
    font-family: 'Inter', sans-serif !important;
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] {
    background-color: #0f0f1a !important;
    border-right: 1px solid #1e1e2e !important;
}

[data-testid="stSidebar"] * { color: #c0c0d0 !important; }

h1 {
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

h2, h3 { color: #00d4aa !important; font-weight: 600 !important; }

[data-testid="stCaptionContainer"] p {
    color: #6b7280 !important;
    font-size: 13px !important;
}

[data-testid="stMetric"] {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
}

[data-testid="stDownloadButton"] button {
    background: #00d4aa !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #00b894 !important;
}

[data-testid="stExpander"] {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #0f0f1a !important;
    border-bottom: 1px solid #1e1e2e !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #6b7280 !important;
    font-size: 13px !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa !important;
}

hr { border-color: #1e1e2e !important; }

[data-testid="stAlert"] {
    background: #0f0f1a !important;
    border-color: #1e1e2e !important;
    color: #c0c0d0 !important;
}

@media (max-width: 768px) {
    h1 { font-size: 1.4rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetric"] { padding: 10px !important; }
}

.counter-wrap {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}

.counter-label {
    color: #6b7280;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.counter-value { font-size: 2rem; font-weight: 700; color: #ffffff; }
.counter-green  { color: #00d4aa !important; }
.counter-yellow { color: #f59e0b !important; }
.counter-red    { color: #ef4444 !important; }

.ticker-badge {
    display: inline-block;
    background: #00d4aa22;
    border: 1px solid #00d4aa55;
    color: #00d4aa;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
    font-family: monospace;
}

.section-label {
    color: #6b7280;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("nifty50_screened.csv")
    numeric_cols = [
        "Price", "Market Cap (Cr)", "P/E Ratio", "Forward P/E",
        "P/B Ratio", "PEG Ratio", "EV/EBITDA", "EPS",
        "ROE (%)", "ROA (%)", "Profit Margin (%)", "Operating Margin (%)",
        "Revenue Growth (%)", "Earnings Growth (%)",
        "Debt/Equity", "Current Ratio", "Free Cash Flow (Cr)",
        "Dividend Yield", "52W High", "52W Low",
        "Promoter Holding (%)", "Inst. Holding (%)", "Composite Score"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────
st.markdown("# 📈 Nifty 150 Stock Screener")
st.caption("Fundamental analysis · NSE India · Data via yfinance · Refreshes every hour")
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Filters")

sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("🏭 Sector", sectors)

industries = ["All"] + sorted(df["Industry"].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("🏗️ Industry", industries)

st.sidebar.markdown("---")

pe_min, pe_max = st.sidebar.slider("📊 P/E Ratio range", 0.0, 100.0, (0.0, 60.0), 0.5)
mcap_min       = st.sidebar.slider("💰 Min market cap (Cr)", 0, 1500000, 5000, 5000, format="%d")
div_min        = st.sidebar.slider("💵 Min dividend yield (%)", 0.0, 5.0, 0.0, 0.1)
roe_min        = st.sidebar.slider("📈 Min ROE (%)", 0.0, 50.0, 0.0, 0.5)
debt_max       = st.sidebar.slider("🏦 Max Debt/Equity", 0.0, 5.0, 5.0, 0.1)

st.sidebar.markdown("---")

signal_filter = st.sidebar.multiselect(
    "🚦 Signal",
    options=["Green", "Yellow", "Red"],
    default=["Green", "Yellow", "Red"]
)

week52 = st.sidebar.radio(
    "📅 52-week position",
    options=["All", "Near 52W High", "Near 52W Low"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='color:#6b7280;font-size:11px;text-align:center'>"
    "Nifty 150 Stock Screener<br>Data from NSE via yfinance<br>Not financial advice"
    "</div>",
    unsafe_allow_html=True
)

# ── Apply filters ─────────────────────────────────────────
filtered = df.copy()

if selected_sector != "All":
    filtered = filtered[filtered["Sector"] == selected_sector]

if selected_industry != "All":
    filtered = filtered[filtered["Industry"] == selected_industry]

filtered = filtered[filtered["P/E Ratio"].between(pe_min, pe_max, inclusive="both")]
filtered = filtered[filtered["Market Cap (Cr)"] >= mcap_min]
filtered = filtered[filtered["Dividend Yield"] >= div_min]
filtered = filtered[filtered["Signal"].isin(signal_filter)]

if roe_min > 0:
    filtered = filtered[filtered["ROE (%)"] >= roe_min]

if debt_max < 5.0:
    filtered = filtered[filtered["Debt/Equity"] <= debt_max]

if week52 == "Near 52W High":
    filtered = filtered[filtered["Price"] >= filtered["52W High"] * 0.90]
elif week52 == "Near 52W Low":
    filtered = filtered[filtered["Price"] <= filtered["52W Low"] * 1.10]

# ── Summary counters ──────────────────────────────────────
n_total  = len(filtered)
n_green  = len(filtered[filtered["Signal"] == "Green"])
n_yellow = len(filtered[filtered["Signal"] == "Yellow"])
n_red    = len(filtered[filtered["Signal"] == "Red"])

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="counter-wrap">
        <div class="counter-label">Stocks shown</div>
        <div class="counter-value">{n_total}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="counter-wrap">
        <div class="counter-label">Green signals</div>
        <div class="counter-value counter-green">{n_green}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="counter-wrap">
        <div class="counter-label">Yellow signals</div>
        <div class="counter-value counter-yellow">{n_yellow}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="counter-wrap">
        <div class="counter-label">Red signals</div>
        <div class="counter-value counter-red">{n_red}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Color functions ───────────────────────────────────────
def color_signal(val):
    colors = {"Green": "#0d2b1f", "Yellow": "#2b2200", "Red": "#2b0d0d"}
    text   = {"Green": "#00d4aa", "Yellow": "#f59e0b", "Red": "#ef4444"}
    return f"background-color: {colors.get(val, '')}; color: {text.get(val, '')}; font-weight: 600;"

def color_pe(val):
    if pd.isna(val): return ""
    if val < 20: return "color: #00d4aa"
    if val > 40: return "color: #ef4444"
    return "color: #e0e0e0"

def color_roe(val):
    if pd.isna(val): return ""
    if val > 20: return "color: #00d4aa"
    if val < 5:  return "color: #ef4444"
    return "color: #e0e0e0"

def color_debt(val):
    if pd.isna(val): return ""
    if val < 1:  return "color: #00d4aa"
    if val > 2:  return "color: #ef4444"
    return "color: #e0e0e0"

# ── Stock table ───────────────────────────────────────────
st.markdown("### 📋 Stock table")

display_cols = [
    "Company", "Sector", "Price", "Market Cap (Cr)",
    "P/E Ratio", "P/B Ratio", "ROE (%)", "Debt/Equity",
    "Dividend Yield", "EPS", "Composite Score", "Signal"
]

styled = (
    filtered[display_cols]
    .style
    .map(color_signal, subset=["Signal"])
    .map(color_pe,     subset=["P/E Ratio"])
    .map(color_roe,    subset=["ROE (%)"])
    .map(color_debt,   subset=["Debt/Equity"])
    .format({
        "Price":           "₹{:.2f}",
        "Market Cap (Cr)": "{:,.0f}",
        "P/E Ratio":       "{:.1f}",
        "P/B Ratio":       "{:.2f}",
        "ROE (%)":         "{:.1f}%",
        "Debt/Equity":     "{:.2f}",
        "Dividend Yield":  "{:.2f}%",
        "EPS":             "{:.2f}",
        "Composite Score": "{:.0f}/100",
    }, na_rep="N/A")
    .set_properties(**{
        "background-color": "#0f0f1a",
        "color": "#e0e0e0",
        "border-color": "#1e1e2e"
    })
)

st.dataframe(styled, use_container_width=True, height=420)

# ── Download ──────────────────────────────────────────────
csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download filtered results as CSV",
    data=csv,
    file_name="screened_stocks.csv",
    mime="text/csv"
)

# ── Stock deep-dive ───────────────────────────────────────
st.markdown("---")
st.markdown("### 🔍 Stock deep-dive")

filtered_company_map = dict(zip(
    filtered["Company"].astype(str),
    filtered["Ticker"].astype(str)
))

selected_company = st.selectbox(
    "Select a stock to analyse",
    options=list(filtered_company_map.keys())
)

selected_stock = filtered_company_map.get(selected_company, None)

if selected_stock:
    stock_row = filtered[filtered["Ticker"] == selected_stock].iloc[0]

    # Ticker badge
    st.markdown(
        f'<span class="ticker-badge">{selected_stock.replace(".NS","")}</span>'
        f'<span style="color:#6b7280;font-size:13px">{stock_row["Sector"]} · {stock_row.get("Industry","")}</span>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Top metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price",          f"₹{stock_row['Price']:.2f}"          if pd.notna(stock_row["Price"])          else "N/A")
    m2.metric("Market Cap",     f"₹{stock_row['Market Cap (Cr)']:,.0f}Cr" if pd.notna(stock_row["Market Cap (Cr)"]) else "N/A")
    m3.metric("P/E Ratio",      f"{stock_row['P/E Ratio']:.1f}"       if pd.notna(stock_row["P/E Ratio"])      else "N/A")
    m4.metric("Composite Score",f"{stock_row['Composite Score']:.0f}/100" if pd.notna(stock_row["Composite Score"]) else "N/A")
    m5.metric("Signal",         str(stock_row["Signal"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed fundamental tabs ─────────────────────────
    st.markdown("#### 📊 Detailed fundamental analysis")
    tab1, tab2, tab3 = st.tabs(["📊 Valuation", "💰 Profitability", "🏦 Financial Health"])

    with tab1:
        v1, v2, v3, v4, v5 = st.columns(5)
        v1.metric("P/E Ratio",    f"{stock_row['P/E Ratio']:.1f}"    if pd.notna(stock_row["P/E Ratio"])   else "N/A")
        v2.metric("Forward P/E",  f"{stock_row['Forward P/E']:.1f}"  if pd.notna(stock_row.get("Forward P/E")) else "N/A")
        v3.metric("P/B Ratio",    f"{stock_row['P/B Ratio']:.2f}"    if pd.notna(stock_row["P/B Ratio"])   else "N/A")
        v4.metric("PEG Ratio",    f"{stock_row['PEG Ratio']:.2f}"    if pd.notna(stock_row.get("PEG Ratio")) else "N/A")
        v5.metric("EV/EBITDA",    f"{stock_row['EV/EBITDA']:.1f}"    if pd.notna(stock_row.get("EV/EBITDA")) else "N/A")

        with st.expander("What do these mean?"):
            st.markdown("""
            - **P/E Ratio** — Price vs trailing earnings. Below 20 = reasonable. Above 40 = expensive.
            - **Forward P/E** — Based on expected future earnings. Lower than P/E = earnings expected to grow.
            - **P/B Ratio** — Price vs book value. Below 1 = trading below asset value (value opportunity).
            - **PEG Ratio** — P/E divided by growth rate. Below 1 = undervalued for its growth rate.
            - **EV/EBITDA** — Enterprise value vs earnings. Below 10 = generally cheap. Above 20 = expensive.
            """)

    with tab2:
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("ROE",              f"{stock_row['ROE (%)']:.1f}%"            if pd.notna(stock_row.get("ROE (%)"))            else "N/A")
        p2.metric("ROA",              f"{stock_row['ROA (%)']:.1f}%"            if pd.notna(stock_row.get("ROA (%)"))            else "N/A")
        p3.metric("Profit Margin",    f"{stock_row['Profit Margin (%)']:.1f}%"  if pd.notna(stock_row.get("Profit Margin (%)"))  else "N/A")
        p4.metric("Operating Margin", f"{stock_row['Operating Margin (%)']:.1f}%" if pd.notna(stock_row.get("Operating Margin (%)")) else "N/A")
        p5.metric("Revenue Growth",   f"{stock_row['Revenue Growth (%)']:.1f}%" if pd.notna(stock_row.get("Revenue Growth (%)")) else "N/A")

        with st.expander("What do these mean?"):
            st.markdown("""
            - **ROE** — Return on Equity. Above 15% = good. Above 20% = excellent. Your money working hard.
            - **ROA** — Return on Assets. Above 5% = efficient use of assets.
            - **Profit Margin** — Net profit as % of revenue. Higher = more money left after all expenses.
            - **Operating Margin** — Operating profit as % of revenue. Measures core business efficiency.
            - **Revenue Growth** — Year-over-year revenue growth. Positive and high = growing business.
            """)

    with tab3:
        f1, f2, f3, f4, f5 = st.columns(5)
        f1.metric("Debt/Equity",      f"{stock_row['Debt/Equity']:.2f}"           if pd.notna(stock_row.get("Debt/Equity"))          else "N/A")
        f2.metric("Current Ratio",    f"{stock_row['Current Ratio']:.2f}"          if pd.notna(stock_row.get("Current Ratio"))         else "N/A")
        f3.metric("Free Cash Flow",   f"₹{stock_row['Free Cash Flow (Cr)']:.0f}Cr" if pd.notna(stock_row.get("Free Cash Flow (Cr)"))  else "N/A")
        f4.metric("Promoter Holding", f"{stock_row['Promoter Holding (%)']:.1f}%"  if pd.notna(stock_row.get("Promoter Holding (%)")) else "N/A")
        f5.metric("Inst. Holding",    f"{stock_row['Inst. Holding (%)']:.1f}%"     if pd.notna(stock_row.get("Inst. Holding (%)"))    else "N/A")

        with st.expander("What do these mean?"):
            st.markdown("""
            - **Debt/Equity** — How much debt vs equity. Below 1 = low leverage. Above 2 = risky.
            - **Current Ratio** — Can it pay short-term debts? Above 1.5 = healthy. Below 1 = warning.
            - **Free Cash Flow** — Cash after capex. Positive and growing = financially strong.
            - **Promoter Holding** — % held by founders. Above 50% = high confidence. Falling = red flag.
            - **Inst. Holding** — % held by institutions (mutual funds, FIIs). Rising = smart money interest.
            """)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Price chart ───────────────────────────────────────
    st.markdown(f"#### 📈 {stock_row['Company']} — 6 month price chart")

    @st.cache_data(ttl=3600)
    def get_chart_data(ticker):
        try:
            hist = yf.Ticker(ticker).history(period="6mo")
            if hist.empty:
                return None
            return hist
        except Exception:
            return None

    hist = get_chart_data(selected_stock)

    if hist is not None and not hist.empty:
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()
        hist["RSI"]  = ta_lib.momentum.RSIIndicator(hist["Close"], window=14).rsi()

        chart_type = st.radio(
            "Chart view",
            ["Price + Moving Averages", "RSI"],
            horizontal=True
        )

        dark_layout = dict(
            paper_bgcolor="#0a0a0f",
            plot_bgcolor="#0f0f1a",
            font=dict(color="#c0c0d0", family="Inter"),
            xaxis=dict(gridcolor="#1e1e2e", title="Date"),
            margin=dict(l=0, r=0, t=10, b=0),
            hovermode="x unified",
            height=400
        )

        if chart_type == "Price + Moving Averages":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"],
                mode="lines", line=dict(color="#00d4aa", width=2),
                name="Close price"
            ))
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA20"],
                mode="lines", line=dict(color="#f59e0b", width=1.5, dash="dash"),
                name="20-day MA"
            ))
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA50"],
                mode="lines", line=dict(color="#ef4444", width=1.5, dash="dot"),
                name="50-day MA"
            ))
            fig.update_layout(
                **dark_layout,
                yaxis=dict(gridcolor="#1e1e2e", title="Price (₹)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            bgcolor="rgba(0,0,0,0)", font=dict(color="#c0c0d0"))
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("What do these indicators mean?"):
                st.markdown("""
                - **20-day MA** — short-term trend. Price above MA20 = bullish momentum.
                - **50-day MA** — medium-term trend. Stronger signal than MA20.
                - **Golden Cross** — MA20 crosses above MA50 = strong bullish signal.
                - **Death Cross** — MA20 crosses below MA50 = bearish signal.
                """)

        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["RSI"],
                mode="lines", line=dict(color="#a78bfa", width=2),
                name="RSI (14)"
            ))
            fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Overbought (70)")
            fig.add_hline(y=30, line_dash="dash", line_color="#00d4aa", annotation_text="Oversold (30)")
            fig.update_layout(
                **dark_layout,
                yaxis=dict(gridcolor="#1e1e2e", title="RSI", range=[0, 100])
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("What is RSI?"):
                st.markdown("""
                **RSI (Relative Strength Index)** measures momentum on a scale of 0–100.
                - **RSI > 70** → Overbought — may be due for a pullback
                - **RSI < 30** → Oversold — may be due for a bounce
                - **RSI 40–60** → Neutral zone
                """)
    else:
        st.warning("Chart data not available for this stock.")

# ── Stock comparison ──────────────────────────────────────
st.markdown("---")
st.markdown("### ⚖️ Compare stocks")

company_names = df["Company"].astype(str).tolist()

selected_companies = st.multiselect(
    "Select 2 or 3 stocks to compare (max 3)",
    options=company_names
)

if len(selected_companies) > 3:
    st.warning("Please select a maximum of 3 stocks.")
    selected_companies = selected_companies[:3]

if len(selected_companies) >= 2:
    compare_cols = [
        "Company", "Sector", "Price", "P/E Ratio", "P/B Ratio",
        "ROE (%)", "Debt/Equity", "Profit Margin (%)",
        "Dividend Yield", "EPS", "Composite Score", "Signal"
    ]

    compare_df = df[df["Company"].isin(selected_companies)][compare_cols].set_index("Company")

    st.dataframe(
        compare_df.style
        .map(color_signal, subset=["Signal"])
        .map(color_roe,    subset=["ROE (%)"])
        .map(color_debt,   subset=["Debt/Equity"])
        .format({
            "Price":            "₹{:.2f}",
            "P/E Ratio":        "{:.1f}",
            "P/B Ratio":        "{:.2f}",
            "ROE (%)":          "{:.1f}%",
            "Debt/Equity":      "{:.2f}",
            "Profit Margin (%)":"{:.1f}%",
            "Dividend Yield":   "{:.2f}%",
            "EPS":              "{:.2f}",
            "Composite Score":  "{:.0f}/100",
        }, na_rep="N/A")
        .set_properties(**{
            "background-color": "#0f0f1a",
            "color": "#e0e0e0",
            "border-color": "#1e1e2e"
        }),
        use_container_width=True
    )

    # Radar chart
    categories  = ["P/E Score", "P/B Score", "ROE Score", "Div Yield", "Composite"]
    colors_radar = ["#00d4aa", "#f59e0b", "#a78bfa"]
    fig_radar   = go.Figure()

    for i, company in enumerate(selected_companies):
        row  = df[df["Company"] == company].iloc[0]
        name = company.split()[0]
        c    = colors_radar[i % len(colors_radar)]

        pe_score  = max(0, 10 - (row["P/E Ratio"] / 5))   if pd.notna(row["P/E Ratio"])       else 0
        pb_score  = max(0, 10 - (row["P/B Ratio"] * 1.5)) if pd.notna(row["P/B Ratio"])       else 0
        roe_score = min(10, row["ROE (%)"] / 3)            if pd.notna(row.get("ROE (%)"))     else 0
        div_score = min(10, row["Dividend Yield"] * 3)     if pd.notna(row["Dividend Yield"])  else 0
        comp      = row["Composite Score"] / 10            if pd.notna(row["Composite Score"]) else 0

        fig_radar.add_trace(go.Scatterpolar(
            r=[pe_score, pb_score, roe_score, div_score, comp],
            theta=categories,
            fill="toself",
            name=name,
            line=dict(color=c)
        ))

    fig_radar.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        font=dict(color="#c0c0d0", family="Inter"),
        polar=dict(
            bgcolor="#0f0f1a",
            radialaxis=dict(visible=True, range=[0, 10],
                            gridcolor="#1e1e2e", color="#6b7280"),
            angularaxis=dict(gridcolor="#1e1e2e", color="#c0c0d0")
        ),
        height=450,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#c0c0d0"))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

elif len(selected_companies) == 1:
    st.info("Select at least one more stock to compare.")

# ── Footer ────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6b7280;font-size:12px;padding:10px'>"
    "Nifty 150 Stock Screener · Built with Python & Streamlit · "
    "Data from NSE via yfinance · Not financial advice"
    "</div>",
    unsafe_allow_html=True
)