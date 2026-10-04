"""
Veraxio tema modulu - Dark mode + mavi vurgu
"""
import streamlit as st


def tema_uygula():
    """
    Veraxio marka CSS'i uygular.
    Streamlit native dark tema uzerine marka katmani.
    """
    css = """
    <style>
    /* ============================================================ */
    /* VERAXIO MARKA - CSS */
    /* ============================================================ */

    /* METRIK KARTLARI */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #171717 0%, #1f1f1f 100%);
        padding: 18px 16px;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(59, 130, 246, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #a3a3a3 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #fafafa !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f;
        border-right: 1px solid #1f1f1f;
    }
    [data-testid="stSidebar"] h1 {
        color: #fafafa !important;
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: #171717;
        border-radius: 8px;
        font-weight: 600;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }

    /* BUTONLAR - primary */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    /* BASLIKLAR */
    h1, h2 {
        padding-bottom: 6px;
        border-bottom: 1px solid #1f1f1f;
    }
    h1 {
        color: #fafafa !important;
        font-weight: 700;
    }
    h2, h3 {
        color: #e5e5e5 !important;
    }

    /* SUCCESS / ERROR / INFO */
    [data-testid="stAlert"] {
        border-radius: 10px;
        border-left-width: 4px;
    }

    /* CHART container */
    [data-testid="stPlotlyChart"] {
        background-color: #0f0f0f;
        border-radius: 10px;
        padding: 8px;
        border: 1px solid #1f1f1f;
    }

    /* INPUT */
    [data-baseweb="select"] > div {
        background-color: #171717 !important;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #171717 !important;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #262626; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #404040; }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] button {
        color: #a3a3a3;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #fafafa;
        border-bottom-color: #3b82f6 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)