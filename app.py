import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Nifty 50 Stock Screener",
    page_icon="📈",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("nifty50_screened.csv")
    numeric_cols = ["Price", "Market Cap (Cr)", "P/E Ratio", "P/B Ratio",
                    "Dividend Yield", "52W High", "52W Low", "EPS", "Composite Score"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

# ── Build ticker maps ─────────────────────────────────────
# Used for dropdowns — plain string mapping avoids Streamlit type errors
all_ticker_map = dict(zip(df["Ticker"].astype(str), df["Company"].astype(str)))

# ── Title ─────────────────────────────────────────────────
st.title("Nifty 50 Stock Screener")
st.caption("Fundamental analysis tool — filter by P/E, market cap, sector & more")

# ── Sidebar filters ───────────────────────────────────────
st.sidebar.header("Filters")

sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("Sector", sectors)

pe_min, pe_max = st.sidebar.slider(
    "P/E Ratio range",
    min_value=0.0, max_value=100.0,
    value=(0.0, 50.0), step=0.5
)

mcap_min = st.sidebar.slider(
    "Min market cap (Cr)",
    min_value=0, max_value=1500000,
    value=10000, step=5000, format="%d"
)

div_min = st.sidebar.slider(
    "Min dividend yield (%)",
    min_value=0.0, max_value=5.0,
    value=0.0, step=0.1
)

signal_filter = st.sidebar.multiselect(
    "Signal",
    options=["Green", "Yellow", "Red"],
    default=["Green", "Yellow", "Red"]
)

week52 = st.sidebar.radio(
    "52-week position",
    options=["All", "Near 52W High", "Near 52W Low"]
)

# ── Apply filters ─────────────────────────────────────────
filtered = df.copy()

if selected_sector != "All":
    filtered = filtered[filtered["Sector"] == selected_sector]

filtered = filtered[filtered["P/E Ratio"].between(pe_min, pe_max, inclusive="both")]
filtered = filtered[filtered["Market Cap (Cr)"] >= mcap_min]
filtered = filtered[filtered["Dividend Yield"] >= div_min]
filtered = filtered[filtered["Signal"].isin(signal_filter)]

if week52 == "Near 52W High":
    filtered = filtered[filtered["Price"] >= filtered["52W High"] * 0.90]
elif week52 == "Near 52W Low":
    filtered = filtered[filtered["Price"] <= filtered["52W Low"] * 1.10]

# ── Summary metrics ───────────────────────────────────────
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Stocks shown",   len(filtered))
col2.metric("Green signals",  len(filtered[filtered["Signal"] == "Green"]))
col3.metric("Yellow signals", len(filtered[filtered["Signal"] == "Yellow"]))
col4.metric("Red signals",    len(filtered[filtered["Signal"] == "Red"]))
st.markdown("---")

# ── Color functions ───────────────────────────────────────
def color_signal(val):
    colors = {"Green": "#d4edda", "Yellow": "#fff3cd", "Red": "#f8d7da"}
    return f"background-color: {colors.get(val, '')}"

def color_pe(val):
    if pd.isna(val): return ""
    if val < 20: return "color: #1a7a3c"
    if val > 40: return "color: #c0392b"
    return ""

# ── Color-coded table ─────────────────────────────────────
display_cols = ["Company", "Sector", "Price", "Market Cap (Cr)",
                "P/E Ratio", "P/B Ratio", "Dividend Yield",
                "EPS", "Composite Score", "Signal"]

styled = (
    filtered[display_cols]
    .style
    .map(color_signal, subset=["Signal"])
    .map(color_pe,     subset=["P/E Ratio"])
    .format({
        "Price":           "₹{:.2f}",
        "Market Cap (Cr)": "{:,.0f}",
        "P/E Ratio":       "{:.1f}",
        "P/B Ratio":       "{:.2f}",
        "Dividend Yield":  "{:.2f}%",
        "EPS":             "{:.2f}",
        "Composite Score": "{:.0f}/100",
    }, na_rep="N/A")
)

st.dataframe(styled, use_container_width=True, height=400)

# ── Download button ───────────────────────────────────────
csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered results as CSV",
    data=csv,
    file_name="screened_stocks.csv",
    mime="text/csv"
)

# ── Stock deep-dive ───────────────────────────────────────
st.markdown("---")
st.subheader("Stock deep-dive")

filtered_ticker_map = dict(zip(filtered["Ticker"].astype(str), filtered["Company"].astype(str)))

selected_stock = st.selectbox(
    "Select a stock to analyse",
    options=list(filtered_ticker_map.keys()),
    format_func=lambda t: filtered_ticker_map.get(t, t)
)

if selected_stock:
    stock_row = filtered[filtered["Ticker"] == selected_stock].iloc[0]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Price",          f"₹{stock_row['Price']:.2f}"          if pd.notna(stock_row['Price'])          else "N/A")
    m2.metric("P/E Ratio",      f"{stock_row['P/E Ratio']:.1f}"       if pd.notna(stock_row['P/E Ratio'])      else "N/A")
    m3.metric("P/B Ratio",      f"{stock_row['P/B Ratio']:.2f}"       if pd.notna(stock_row['P/B Ratio'])      else "N/A")
    m4.metric("Dividend Yield", f"{stock_row['Dividend Yield']:.2f}%" if pd.notna(stock_row['Dividend Yield']) else "N/A")
    m5.metric("EPS",            f"₹{stock_row['EPS']:.2f}"            if pd.notna(stock_row['EPS'])            else "N/A")

    st.markdown(f"#### {stock_row['Company']} — 6 month price chart")

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
        import pandas_ta as ta

        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()
        hist["RSI"]  = ta.rsi(hist["Close"], length=14)

        chart_type = st.radio(
            "Chart view",
            ["Price + Moving Averages", "RSI"],
            horizontal=True
        )

        if chart_type == "Price + Moving Averages":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"],
                mode="lines", line=dict(color="#1f77b4", width=2),
                name="Close price"
            ))
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA20"],
                mode="lines", line=dict(color="#f39c12", width=1.5, dash="dash"),
                name="20-day MA"
            ))
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA50"],
                mode="lines", line=dict(color="#e74c3c", width=1.5, dash="dot"),
                name="50-day MA"
            ))
            fig.update_layout(
                xaxis_title="Date", yaxis_title="Price (₹)",
                height=400, margin=dict(l=0, r=0, t=10, b=0),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("What do these indicators mean?"):
                st.markdown("""
                - **20-day MA** — average closing price over last 20 days. Price above MA20 = short-term bullish.
                - **50-day MA** — average closing price over last 50 days. When MA20 crosses above MA50 = **Golden Cross** (bullish signal).
                - **RSI** — see RSI view for details.
                """)

        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["RSI"],
                mode="lines", line=dict(color="#9b59b6", width=2),
                name="RSI (14)"
            ))
            fig.add_hline(y=70, line_dash="dash", line_color="red",   annotation_text="Overbought (70)")
            fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
            fig.update_layout(
                xaxis_title="Date", yaxis_title="RSI",
                yaxis=dict(range=[0, 100]),
                height=400, margin=dict(l=0, r=0, t=10, b=0),
                hovermode="x unified"
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
# ── Stock comparison ──────────────────────────────────────
st.markdown("---")
st.subheader("Compare stocks")

company_names = df["Company"].astype(str).tolist()

selected_companies = st.multiselect(
    "Select 2 or 3 stocks to compare (max 3)",
    options=company_names
)

if len(selected_companies) > 3:
    st.warning("Please select a maximum of 3 stocks.")
    selected_companies = selected_companies[:3]

if len(selected_companies) >= 2:
    compare_df = df[df["Company"].isin(selected_companies)][
        ["Company", "Sector", "Price", "P/E Ratio", "P/B Ratio",
         "Dividend Yield", "EPS", "Composite Score", "Signal"]
    ].set_index("Company")

    st.dataframe(
        compare_df.style
        .map(color_signal, subset=["Signal"])
        .format({
            "Price":           "₹{:.2f}",
            "P/E Ratio":       "{:.1f}",
            "P/B Ratio":       "{:.2f}",
            "Dividend Yield":  "{:.2f}%",
            "EPS":             "{:.2f}",
            "Composite Score": "{:.0f}/100",
        }, na_rep="N/A"),
        use_container_width=True
    )

    categories = ["P/E Score", "P/B Score", "EPS Score", "Div Yield", "Composite"]
    fig_radar = go.Figure()

    for company in selected_companies:
        row = df[df["Company"] == company].iloc[0]
        name = company.split()[0]

        pe_score  = max(0, 10 - (row["P/E Ratio"] / 5))   if pd.notna(row["P/E Ratio"])       else 0
        pb_score  = max(0, 10 - (row["P/B Ratio"] * 1.5)) if pd.notna(row["P/B Ratio"])       else 0
        eps_score = min(10, row["EPS"] / 15)               if pd.notna(row["EPS"])             else 0
        div_score = min(10, row["Dividend Yield"] * 3)     if pd.notna(row["Dividend Yield"])  else 0
        comp      = row["Composite Score"] / 10            if pd.notna(row["Composite Score"]) else 0

        fig_radar.add_trace(go.Scatterpolar(
            r=[pe_score, pb_score, eps_score, div_score, comp],
            theta=categories,
            fill="toself",
            name=name
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

elif len(selected_companies) == 1:
    st.info("Select at least one more stock to compare.")