import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("INDIA_GOV_API_KEY", "").strip()

API_URL = (
    "https://api.data.gov.in/resource/"
    "9ef84268-d588-465a-a308-a864a43d0070"
)

COMMON_MANDIS = [
    "Bangalore",
    "Mysore",
    "Tumkur",
    "Davanagere",
    "Hubli",
    "Belgaum",
    "Shimoga",
    "Hassan",
    "Kolar",
    "Chitradurga",
]

COMMON_COMMODITIES = [
    "Arecanut",
    "Banana",
    "Cotton",
    "Maize",
    "Onion",
    "Paddy",
    "Potato",
    "Rice",
    "Tomato",
]

COMMON_DISTRICTS = [
    "Bangalore Urban",
    "Belgaum",
    "Chitradurga",
    "Davanagere",
    "Hassan",
    "Kolar",
    "Mysore",
    "Shimoga",
    "Tumkur",
    "Udupi",
]

# =========================================================
# PROFESSIONAL UI
# =========================================================

st.markdown(
    """
<style>
.stApp { background: #f4f6f0; }

.market-header {
    background: linear-gradient(
        135deg,
        #1E5620 0%,
        #2D7D32 55%,
        #E5A93C 100%
    );
    color: white;
    padding: 32px 36px;
    border-radius: 22px;
    margin-bottom: 24px;
    box-shadow: 0 12px 32px rgba(30,86,32,0.2);
}

.market-header h1 {
    margin: 0;
    font-size: 36px;
    font-weight: 800;
}

.market-header p {
    margin: 8px 0 0;
    color: #F5F5DC;
    font-size: 15px;
}

.search-intro {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin: 26px 0 10px;
}

.search-title {
    color: #1E5620;
    font-size: 24px;
    font-weight: 800;
    margin: 0;
}

.search-subtitle {
    color: #6D4C41;
    font-size: 13px;
    margin: 4px 0 0;
}

.search-status {
    color: #166534;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
}

.filter-panel {
    background: white;
    padding: 18px 20px 20px;
    border-radius: 18px;
    border: 1px solid #dce9de;
    box-shadow: 0 8px 24px rgba(30, 86, 32, 0.06);
    margin-bottom: 22px;
}

.filter-label {
    color: #526458;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin: 0 0 4px;
}

div[data-testid="stSelectbox"] label {
    color: #415247;
    font-size: 13px;
    font-weight: 700;
}

div[data-testid="stSelectbox"] > div > div {
    border-radius: 10px;
    border-color: #cbdacf;
    min-height: 42px;
}

.filter-actions {
    border-top: 1px solid #e8efe9;
    margin-top: 10px;
    padding-top: 15px;
}

.active-filter {
    color: #526458;
    font-size: 12px;
    margin: 8px 0 18px;
}

.section-title {
    color: #245b2a;
    font-size: 21px;
    font-weight: 800;
    margin: 22px 0 12px;
}

.price-card {
    background: white;
    border: 1px solid #dfe9e1;
    border-radius: 18px;
    padding: 21px;
    min-height: 135px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.04);
}

.price-icon {
    font-size: 26px;
}

.price-label {
    color: #748078;
    font-size: 13px;
    margin-top: 5px;
}

.price-value {
    color: #1b5e20;
    font-size: 29px;
    font-weight: 800;
    margin-top: 5px;
}

.price-unit {
    color: #89938b;
    font-size: 11px;
}

.best-market {
    background: linear-gradient(
        135deg,
        #eaf7ec,
        #f7fcf7
    );
    border: 1px solid #cce3cf;
    border-radius: 18px;
    padding: 22px;
    margin-top: 20px;
}

.best-market-title {
    color: #33691e;
    font-size: 18px;
    font-weight: 800;
}

.best-market-name {
    color: #1b5e20;
    font-size: 25px;
    font-weight: 800;
    margin-top: 5px;
}

.info-box {
    background: #f7faf7;
    border-left: 5px solid #43a047;
    padding: 18px;
    border-radius: 13px;
    margin-top: 22px;
    color: #526056;
}

.source-box {
    background: #f1f8f3;
    border: 1px solid #d5e7d8;
    border-radius: 15px;
    padding: 17px;
    margin-top: 22px;
}

.empty-state {
    text-align: center;
    padding: 75px 20px;
    background: #f8fcf8;
    border: 1px dashed #c9dccb;
    border-radius: 22px;
}

.empty-icon {
    font-size: 65px;
}

.status-live {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}

@media (max-width: 700px) {
    .market-header { padding: 23px 20px; border-radius: 16px; }
    .market-header h1 { font-size: 29px; }
    .search-intro { display: block; }
    .search-status { display: inline-block; margin-top: 10px; }
    .filter-panel { padding: 15px; }
}

</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="market-header">

        <h1>📈 Live Market Intelligence</h1>

        <p>
            Government-sourced mandi prices to help farmers
            compare markets and make better selling decisions.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# API FUNCTION
# =========================================================

@st.cache_data(ttl=600, show_spinner=False)
def fetch_market_data(
    commodity=None,
    state=None,
    district=None,
    market=None,
    limit=1000
):

    if not API_KEY:

        return {
            "success": False,
            "message": (
                "Government API key is missing. "
                "Please check INDIA_GOV_API_KEY in your .env file."
            )
        }

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit
    }

    if commodity:
        params["filters[commodity]"] = commodity

    if state:
        params["filters[state]"] = state

    if district:
        params["filters[district]"] = district

    if market:
        params["filters[market]"] = market

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=20
        )

        if response.status_code != 200:

            return {
                "success": False,
                "message": (
                    f"Government market API returned "
                    f"HTTP {response.status_code}."
                )
            }

        data = response.json()

        records = data.get("records", [])

        return {
            "success": True,
            "records": records,
            "total": data.get("total", len(records))
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "message": (
                "Market data service timed out. "
                "Please try again."
            )
        }

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "message": (
                "Unable to connect to Government market "
                "data service."
            )
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Market data error: {e}"
        }


# =========================================================
# SESSION STATE
# =========================================================

if "market_records" not in st.session_state:
    st.session_state["market_records"] = None

if "market_loaded" not in st.session_state:
    st.session_state["market_loaded"] = False

if "market_query" not in st.session_state:
    st.session_state["market_query"] = {}


def option_values(records, field, fallback=None):
    values = {
        str(record.get(field, "")).strip()
        for record in records or []
        if str(record.get(field, "")).strip()
    }
    values.update(fallback or [])
    return ["All"] + sorted(values)


if not st.session_state["market_loaded"] and st.session_state["market_records"] is None:
    with st.spinner("📡 Loading today's official mandi prices..."):
        initial_result = fetch_market_data(limit=500)

    if initial_result["success"] and initial_result["records"]:
        st.session_state["market_records"] = initial_result["records"]
        st.session_state["market_loaded"] = True
        st.session_state["market_query"] = {}
    elif not initial_result["success"]:
        st.warning(initial_result["message"])


# =========================================================
# FILTER PANEL
# =========================================================

st.markdown(
    """
    <div class="search-intro">
        <div>
            <div class="search-title">Find today’s mandi prices</div>
            <div class="search-subtitle">Choose any combination of filters. Use All to compare a wider area.</div>
        </div>
        <div class="search-status">● Official data</div>
    </div>
    <div class="filter-label">Search filters</div>
    """,
    unsafe_allow_html=True
)

available_records = st.session_state["market_records"] or []

col1, col2 = st.columns(2)

with col1:

    commodity = st.selectbox(
        "🌾 Commodity",
        option_values(available_records, "commodity", COMMON_COMMODITIES),
        key="market_commodity",
    )

with col2:

    state = st.selectbox(
        "🇮🇳 State",
        option_values(available_records, "state", ["Karnataka"]),
        key="market_state",
    )

col3, col4 = st.columns(2)

with col3:

    district = st.selectbox(
        "📍 District",
        option_values(available_records, "district", COMMON_DISTRICTS),
        key="market_district",
    )

with col4:

    market = st.selectbox(
        "🏪 Market / Mandi",
        option_values(available_records, "market", COMMON_MANDIS),
        key="market_name",
    )

st.divider()

search_col, clear_col = st.columns([3, 1])

with search_col:

    search_clicked = st.button(
        "🔍 Search Live Prices",
        width="stretch",
        type="primary"
    )

with clear_col:

    clear_clicked = st.button(
        "Clear",
        width="stretch"
    )

selected_labels = [
    value for value in [commodity, state, district, market]
    if value != "All"
]
filter_summary = " · ".join(selected_labels) if selected_labels else "Showing all available markets"
st.markdown(f'<div class="active-filter">Current view: <b>{filter_summary}</b></div>', unsafe_allow_html=True)

# =========================================================
# CLEAR
# =========================================================

if clear_clicked:

    st.session_state["market_records"] = None
    st.session_state["market_loaded"] = False
    st.session_state["market_query"] = {}

    st.rerun()


# =========================================================
# SEARCH
# =========================================================

if search_clicked:

    query = {
        "commodity": None if commodity == "All" else commodity,
        "state": None if state == "All" else state,
        "district": None if district == "All" else district,
        "market": None if market == "All" else market
    }

    with st.spinner(
        "📡 Fetching official mandi market data..."
    ):

        result = fetch_market_data(
            commodity=query["commodity"],
            state=query["state"],
            district=query["district"],
            market=query["market"]
        )

    if result["success"]:

        st.session_state["market_records"] = result["records"]
        st.session_state["market_loaded"] = True
        st.session_state["market_query"] = query

    else:

        st.session_state["market_records"] = None
        st.session_state["market_loaded"] = False

        st.error(result["message"])


# =========================================================
# LOAD RESULTS
# =========================================================

records = st.session_state["market_records"]

if records:

    df = pd.DataFrame(records)

    # -----------------------------------------------------
    # NORMALIZE COLUMN NAMES
    # -----------------------------------------------------

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    # -----------------------------------------------------
    # PRICE FIELDS
    # -----------------------------------------------------

    for column in [
        "min_price",
        "max_price",
        "modal_price"
    ]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    if "arrival_date" in df.columns:

        df["arrival_date"] = pd.to_datetime(
            df["arrival_date"],
            errors="coerce",
            dayfirst=True
        )

    # =====================================================
    # STATUS
    # =====================================================

    st.markdown(
        """
        <span class="status-live">
            ● OFFICIAL MARKET DATA
        </span>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # TOP METRICS
    # =====================================================

    st.markdown(
        '<div class="section-title">📊 Market Overview</div>',
        unsafe_allow_html=True
    )

    modal = (
        df["modal_price"].dropna()
        if "modal_price" in df.columns
        else pd.Series(dtype=float)
    )

    minimum = (
        df["min_price"].dropna()
        if "min_price" in df.columns
        else pd.Series(dtype=float)
    )

    maximum = (
        df["max_price"].dropna()
        if "max_price" in df.columns
        else pd.Series(dtype=float)
    )

    avg_modal = modal.mean() if not modal.empty else None
    lowest = minimum.min() if not minimum.empty else None
    highest = maximum.max() if not maximum.empty else None

    market_count = (
        df["market"].nunique()
        if "market" in df.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        value = (
            f"₹{avg_modal:,.0f}"
            if avg_modal is not None
            else "—"
        )

        st.markdown(
            f"""
            <div class="price-card">

                <div class="price-icon">💰</div>

                <div class="price-label">
                    Average Modal Price
                </div>

                <div class="price-value">
                    {value}
                </div>

                <div class="price-unit">
                    per quintal
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        value = (
            f"₹{lowest:,.0f}"
            if lowest is not None
            else "—"
        )

        st.markdown(
            f"""
            <div class="price-card">

                <div class="price-icon">📉</div>

                <div class="price-label">
                    Lowest Market Price
                </div>

                <div class="price-value">
                    {value}
                </div>

                <div class="price-unit">
                    minimum price
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        value = (
            f"₹{highest:,.0f}"
            if highest is not None
            else "—"
        )

        st.markdown(
            f"""
            <div class="price-card">

                <div class="price-icon">📈</div>

                <div class="price-label">
                    Highest Market Price
                </div>

                <div class="price-value">
                    {value}
                </div>

                <div class="price-unit">
                    maximum price
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="price-card">

                <div class="price-icon">🏪</div>

                <div class="price-label">
                    Markets Found
                </div>

                <div class="price-value">
                    {market_count}
                </div>

                <div class="price-unit">
                    market locations
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # BEST MARKET
    # =====================================================

    if (
        "market" in df.columns
        and "modal_price" in df.columns
    ):

        best_df = df.dropna(
            subset=["modal_price"]
        )

        if not best_df.empty:

            best_row = best_df.loc[
                best_df["modal_price"].idxmax()
            ]

            best_market_name = best_row["market"]
            best_price = best_row["modal_price"]

            st.markdown(
                f"""
                <div class="best-market">

                    <div class="best-market-title">
                        🏆 Highest Modal Price Found
                    </div>

                    <div class="best-market-name">
                        {best_market_name}
                    </div>

                    <div style="
                        color:#5d6b60;
                        margin-top:5px;
                    ">
                        Modal price:
                        <b>₹{best_price:,.0f}</b>
                        per quintal
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # MARKET COMPARISON
    # =====================================================

    if (
        "market" in df.columns
        and "modal_price" in df.columns
    ):

        comparison = df[
            ["market", "modal_price"]
        ].dropna()

        if not comparison.empty:

            comparison = (
                comparison
                .groupby("market")["modal_price"]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(15)
            )

            st.markdown(
                '<div class="section-title">'
                '📊 Market-wise Price Comparison'
                '</div>',
                unsafe_allow_html=True
            )

            st.bar_chart(
                comparison,
                height=400
            )

    # =====================================================
    # DETAILED TABLE
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        '📋 Detailed Market Results'
        '</div>',
        unsafe_allow_html=True
    )

    preferred = [
        "state",
        "district",
        "market",
        "commodity",
        "variety",
        "grade",
        "arrival_date",
        "min_price",
        "max_price",
        "modal_price"
    ]

    available = [
        column
        for column in preferred
        if column in df.columns
    ]

    table = df[available].copy()

    rename = {
        "state": "State",
        "district": "District",
        "market": "Market",
        "commodity": "Commodity",
        "variety": "Variety",
        "grade": "Grade",
        "arrival_date": "Arrival Date",
        "min_price": "Min Price",
        "max_price": "Max Price",
        "modal_price": "Modal Price"
    }

    table.rename(
        columns=rename,
        inplace=True
    )

    if "Arrival Date" in table.columns:

        table["Arrival Date"] = (
            table["Arrival Date"]
            .dt.strftime("%d-%m-%Y")
            .fillna("—")
        )

    for column in [
        "Min Price",
        "Max Price",
        "Modal Price"
    ]:

        if column in table.columns:

            table[column] = table[column].apply(
                lambda value:
                f"₹{value:,.0f}"
                if pd.notna(value)
                else "—"
            )

    st.dataframe(
        table,
        width="stretch",
        hide_index=True
    )

    # =====================================================
    # DATA INFORMATION
    # =====================================================

    st.markdown(
        """
        <div class="info-box">

            <b>💡 How to read the prices</b>

            <br><br>

            <b>Min Price</b> – lowest reported wholesale price.

            <br>

            <b>Max Price</b> – highest reported wholesale price.

            <br>

            <b>Modal Price</b> – the modal/most representative
            reported market price.

            <br><br>

            Use market comparison as decision support;
            actual selling price may vary based on quality,
            variety, grade, quantity and local conditions.

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # SOURCE
    # =====================================================

    st.markdown(
        """
        <div class="source-box">

            <b>🇮🇳 Official Data Source</b>

            <br><br>

            Government of India –
            Open Government Data (OGD) Platform

            <br>

            Department of Agriculture & Farmers Welfare

            <br>

            Directorate of Marketing & Inspection (DMI)

            <br><br>

            <b>Dataset:</b>
            Current Daily Price of Various Commodities
            from Various Markets (Mandi)

            <br><br>

            <span style="color:#68756d;">
            Market data is published daily and may not represent
            second-by-second real-time prices.
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # REFRESH
    # =====================================================

    st.write("")

    if st.button(
        "🔄 Refresh Official Market Data",
        width="stretch"
    ):

        query = st.session_state["market_query"]

        with st.spinner(
            "Updating official market prices..."
        ):

            result = fetch_market_data(
                commodity=query.get("commodity"),
                state=query.get("state"),
                district=query.get("district"),
                market=query.get("market")
            )

        if result["success"]:

            st.session_state["market_records"] = (
                result["records"]
            )

            st.rerun()

        else:

            st.error(result["message"])


# =========================================================
# NO RESULTS
# =========================================================

elif st.session_state["market_loaded"]:

    st.markdown(
        """
        <div class="empty-state">

            <div class="empty-icon">
                📊
            </div>

            <h2 style="color:#2E7D32;">
                No Market Data Found
            </h2>

            <p style="color:#68756D;">
                Try a broader commodity, state or district.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# INITIAL STATE
# =========================================================

else:

    st.markdown(
        """
        <div class="empty-state">

            <div class="empty-icon">
                🌾
            </div>

            <h2 style="color:#2E7D32;">
                Explore Agricultural Market Prices
            </h2>

            <p style="color:#68756D;">
                Search for a commodity and location to view
                official Government mandi price data.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )