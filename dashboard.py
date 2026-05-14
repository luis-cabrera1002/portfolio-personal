import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import (UNIVERSE, TICKER_NAMES, ALL_TICKERS,
                    GOOGLE_API_KEY, ANTHROPIC_API_KEY,
                    APP_TITLE, APP_SUBTITLE, APP_ICON)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": f"# {APP_TITLE}\nTu centro personal de inteligencia financiera con IA.",
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — DARK PROFESSIONAL THEME
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
.stApp { background: linear-gradient(135deg, #050810 0%, #0a0e1a 50%, #0d1220 100%) !important; }
.stApp > header { background: transparent !important; }
* { box-sizing: border-box; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 60%, #090d18 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.12) !important;
}
[data-testid="stSidebar"]::before {
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at top left, rgba(0,212,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

/* ── Metric cards — glassmorphism ── */
[data-testid="metric-container"] {
    background: rgba(17,24,39,0.75) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-top: 2px solid rgba(0,212,255,0.45) !important;
    border-radius: 14px !important;
    padding: 18px 16px !important;
    backdrop-filter: blur(12px) !important;
    transition: border-color 0.25s, transform 0.2s !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35) !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,212,255,0.4) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.82em !important; text-transform: uppercase; letter-spacing: 0.04em; }
[data-testid="stMetricDelta"] svg { display:none; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(17,24,39,0.9) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1px solid rgba(30,41,59,0.8) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 8px 14px !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #94a3b8 !important; background: rgba(255,255,255,0.04) !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15)) !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00d4ff, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s !important;
    box-shadow: 0 4px 15px rgba(0,212,255,0.2) !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 6px 20px rgba(0,212,255,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    box-shadow: 0 4px 20px rgba(0,212,255,0.3) !important;
}

/* ── DataFrames ── */
.stDataFrame {
    border: 1px solid rgba(30,41,59,0.9) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="stDataFrameResizable"] { background: rgba(11,17,32,0.9) !important; }

/* ── Text ── */
.stMarkdown p { color: #cbd5e1 !important; }
h1, h2, h3, h4 { color: #e2e8f0 !important; }
.stCaption { color: #475569 !important; font-size: 0.78em !important; }

/* ── Inputs & Selects ── */
[data-testid="stSelectbox"] > div > div,
.stTextInput > div > div > input,
.stMultiSelect [data-baseweb="select"] > div {
    background: rgba(17,24,39,0.9) !important;
    border: 1px solid rgba(30,41,59,0.9) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(17,24,39,0.6) !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(30,41,59,0.6) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    background: rgba(11,17,32,0.5) !important;
}

/* ── Info / Warning / Success / Error boxes ── */
[data-testid="stAlert"] { border-radius: 10px !important; }
.stInfo    { background: rgba(0,212,255,0.07)  !important; border-color: rgba(0,212,255,0.3)  !important; }
.stWarning { background: rgba(245,158,11,0.07) !important; border-color: rgba(245,158,11,0.3) !important; }
.stSuccess { background: rgba(0,255,136,0.07)  !important; border-color: rgba(0,255,136,0.3)  !important; }
.stError   { background: rgba(255,68,68,0.07)  !important; border-color: rgba(255,68,68,0.3)  !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── Mobile ── */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { min-width: 100% !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.68rem !important; padding: 5px 7px !important; }
    [data-testid="metric-container"] { padding: 10px !important; }
}

/* ── Misc ── */
.stApp { scroll-behavior: smooth; }
[data-testid="stSidebar"] { padding-top: 0.75rem; }
.element-container { transition: opacity 0.15s ease; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_DARK = dict(template="plotly_dark", paper_bgcolor="#111827", plot_bgcolor="#0a0e1a")

def _pct(v):
    try: return f"{float(v):.2%}"
    except: return "N/A"

def _f2(v):
    try: return f"{float(v):.2f}"
    except: return "N/A"

def _color(v, neutral_zero=True):
    try:
        f = float(v)
        if f > 0: return "#00ff88"
        if f < 0: return "#ff4444"
        return "#94a3b8"
    except: return "#94a3b8"

def _badge(text, bg):
    return f'<span style="background:{bg};color:white;padding:2px 8px;border-radius:4px;font-size:0.78em;font-weight:600">{text}</span>'

def _sentiment_badge(s):
    m = {"positivo": "#00ff88", "negativo": "#ff4444", "neutro": "#f59e0b"}
    return _badge(s.upper(), m.get(str(s).lower(), "#94a3b8"))

def _impact_badge(i):
    m = {"alto": "#ff4444", "medio": "#f59e0b", "bajo": "#00ff88"}
    return _badge(i.upper(), m.get(str(i).lower(), "#94a3b8"))

def _action_badge(a):
    m = {"COMPRAR": "#00ff88", "MANTENER": "#f59e0b", "VENDER": "#ff4444"}
    return _badge(a, m.get(str(a).upper(), "#94a3b8"))

def _traffic_emoji(t):
    return {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}.get(str(t).lower(), "⚪")


def create_var_gauge(var_value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(var_value, 2),
        title={"text": "VaR Diario 95% (%)", "font": {"color": "#e2e8f0", "size": 15}},
        number={"suffix": "%", "font": {"color": "#e2e8f0", "size": 42}},
        delta={"reference": 2.0,
               "increasing": {"color": "#ff4444"},
               "decreasing": {"color": "#00ff88"}},
        gauge={
            "axis": {"range": [0, 8], "tickcolor": "#94a3b8",
                     "tickfont": {"color": "#94a3b8", "size": 11}},
            "bar":  {"color": "#00d4ff", "thickness": 0.28},
            "bgcolor": "#111827",
            "borderwidth": 1,
            "bordercolor": "#1e293b",
            "steps": [
                {"range": [0, 1], "color": "#052e16"},
                {"range": [1, 3], "color": "#431407"},
                {"range": [3, 8], "color": "#450a0a"},
            ],
            "threshold": {
                "line": {"color": "#ff4444", "width": 3},
                "thickness": 0.85,
                "value": 3,
            },
        },
    ))
    fig.update_layout(**_DARK, height=300, margin=dict(l=30, r=30, t=55, b=20))
    return fig


def metric_card(titulo, valor, delta=None, tooltip=None, icon="📊",
                color_acento="#00d4ff", positivo_es_bueno=True):
    delta_html = ""
    if delta is not None:
        try:
            d = float(str(delta).replace("%", "").replace("+", ""))
            if positivo_es_bueno:
                dc = "#00ff88" if d >= 0 else "#ff4444"
                da = "▲" if d >= 0 else "▼"
            else:
                dc = "#ff4444" if d >= 0 else "#00ff88"
                da = "▲" if d >= 0 else "▼"
            delta_html = (f'<div style="color:{dc};font-size:0.82em;margin-top:4px;font-weight:600">'
                          f'{da} {delta}</div>')
        except Exception:
            delta_html = (f'<div style="color:#94a3b8;font-size:0.82em;margin-top:4px">'
                          f'{delta}</div>')
    tip = f' title="{tooltip}"' if tooltip else ""
    return (
        f'<div{tip} style="background:rgba(17,24,39,0.85);border:1px solid {color_acento}2a;'
        f'border-top:3px solid {color_acento};border-radius:13px;padding:18px 14px;text-align:center;'
        f'box-shadow:0 4px 20px rgba(0,0,0,0.3);cursor:default;transition:transform 0.2s">'
        f'<div style="font-size:1.55em;margin-bottom:5px">{icon}</div>'
        f'<div style="color:#64748b;font-size:0.73em;text-transform:uppercase;'
        f'letter-spacing:0.07em;margin-bottom:7px">{titulo}</div>'
        f'<div style="color:#e2e8f0;font-size:1.35em;font-weight:700">{valor}</div>'
        f'{delta_html}'
        f'</div>'
    )


def info_card(titulo, contenido, icon="ℹ️", tipo="info"):
    colors = {
        "info":    ("#00d4ff", "rgba(0,212,255,0.07)"),
        "warning": ("#f59e0b", "rgba(245,158,11,0.07)"),
        "success": ("#00ff88", "rgba(0,255,136,0.07)"),
        "danger":  ("#ff4444", "rgba(255,68,68,0.07)"),
    }
    accent, bg = colors.get(tipo, colors["info"])
    return (
        f'<div style="background:{bg};border-left:4px solid {accent};border-radius:0 10px 10px 0;'
        f'padding:13px 16px;margin:10px 0">'
        f'<div style="color:{accent};font-weight:600;font-size:0.88em;margin-bottom:5px">'
        f'{icon} {titulo}</div>'
        f'<div style="color:#94a3b8;font-size:0.84em;line-height:1.55">{contenido}</div>'
        f'</div>'
    )


def news_card(headline, sentiment, impact, summary, ticker, time_ago=""):
    sc = {"positivo": "#00ff88", "negativo": "#ff4444", "neutro": "#f59e0b"}.get(
        str(sentiment).lower(), "#94a3b8")
    ic = {"alto": "#ff4444", "medio": "#f59e0b", "bajo": "#00ff88"}.get(
        str(impact).lower(), "#94a3b8")
    return (
        f'<div style="background:rgba(17,24,39,0.88);border:1px solid {sc}2a;'
        f'border-left:4px solid {sc};border-radius:11px;padding:14px 16px;margin-bottom:10px;'
        f'box-shadow:0 3px 15px rgba(0,0,0,0.25)">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
        f'<span style="background:rgba(0,212,255,0.13);color:#00d4ff;font-size:0.73em;'
        f'font-weight:700;padding:2px 9px;border-radius:5px">{ticker}</span>'
        f'<span style="color:#475569;font-size:0.73em">{time_ago}</span>'
        f'</div>'
        f'<div style="color:#e2e8f0;font-weight:600;font-size:0.9em;line-height:1.45;'
        f'margin-bottom:7px">{headline}</div>'
        f'<div style="color:#64748b;font-size:0.81em;margin-bottom:10px;line-height:1.4">'
        f'{summary[:130]}</div>'
        f'<div style="display:flex;gap:7px">'
        f'<span style="background:{sc}1a;color:{sc};border:1px solid {sc}40;padding:2px 8px;'
        f'border-radius:4px;font-size:0.73em;font-weight:600">{str(sentiment).upper()}</span>'
        f'<span style="background:{ic}1a;color:{ic};border:1px solid {ic}40;padding:2px 8px;'
        f'border-radius:4px;font-size:0.73em;font-weight:600">IMPACTO {str(impact).upper()}</span>'
        f'</div>'
        f'</div>'
    )


def recommendation_card(ticker, nombre, accion, justificacion,
                        retorno=None, sharpe=None, esg_light=None):
    ac = {"COMPRAR": "#00ff88", "MANTENER": "#f59e0b", "VENDER": "#ff4444"}.get(
        str(accion).upper(), "#94a3b8")
    extras = []
    if retorno:
        extras.append(f'<span style="color:#94a3b8;font-size:0.79em">Ret: '
                      f'<b style="color:#e2e8f0">{retorno}</b></span>')
    if sharpe:
        extras.append(f'<span style="color:#94a3b8;font-size:0.79em">Sharpe: '
                      f'<b style="color:#e2e8f0">{sharpe}</b></span>')
    if esg_light:
        esg_icon = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}.get(
            str(esg_light).lower(), "⚪")
        extras.append(f'<span style="font-size:0.79em">{esg_icon} ESG</span>')
    extras_html = '<div style="display:flex;gap:14px;flex-wrap:wrap">' + "".join(extras) + "</div>" if extras else ""
    return (
        f'<div style="background:rgba(17,24,39,0.82);border:1px solid {ac}2a;'
        f'border-radius:13px;padding:14px 16px;margin-bottom:10px;'
        f'box-shadow:0 3px 16px rgba(0,0,0,0.28)">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
        f'<div><span style="color:#e2e8f0;font-weight:700;font-size:1.0em">{ticker}</span>'
        f'<span style="color:#475569;font-size:0.81em;margin-left:9px">{nombre}</span></div>'
        f'<span style="background:{ac}1a;color:{ac};border:1px solid {ac}55;padding:3px 11px;'
        f'border-radius:7px;font-weight:700;font-size:0.84em">{str(accion).upper()}</span>'
        f'</div>'
        f'<div style="color:#94a3b8;font-size:0.84em;line-height:1.5;margin-bottom:10px">'
        f'{justificacion[:150]}</div>'
        f'{extras_html}'
        f'</div>'
    )

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k in ("analysis_results", "last_run", "is_running"):
    if k not in st.session_state:
        st.session_state[k] = None if k != "is_running" else False

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <span style="font-size:2em;">🧠</span>
        <div style="font-size:1.1em;font-weight:700;background:linear-gradient(135deg,#00d4ff,#7c3aed);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Portfolio Intelligence
        </div>
        <div style="color:#94a3b8;font-size:0.8em;margin-top:2px;">AI Investment Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"## 🎯 {APP_TITLE}")
    st.caption("Centro de Inteligencia Financiera Personal")
    run_full  = st.button("⚡ Análisis Completo", use_container_width=True, type="primary")
    run_quick = st.button("🔄 Update Rápido",    use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Universo de Activos")

    sel_stocks = st.multiselect(
        "Acciones",
        options=UNIVERSE["stocks"],
        default=["AAPL", "NVDA", "MSFT", "AMZN"],
    )
    sel_comm = st.multiselect(
        "Commodities",
        options=UNIVERSE["commodities"],
        format_func=lambda t: TICKER_NAMES.get(t, t),
        default=["GC=F", "CL=F"],
    )
    sel_etfs = st.multiselect(
        "ETFs",
        options=UNIVERSE["etfs"],
        default=["SPY", "QQQ"],
    )
    selected_tickers = sel_stocks + sel_comm + sel_etfs

    period = st.select_slider(
        "Período histórico",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        value="1y",
    )

    st.markdown("---")
    st.markdown("### 🤖 Estado de Agentes")
    results = st.session_state.analysis_results or {}
    agents_status = {
        "market_analyst":      "market" in results,
        "esg_checker":         "esg" in results,
        "news_sentinel":       "news" in results,
        "risk_manager":        "risk" in results,
        "predictor_engine":    "predictions" in results,
        "macro_monitor":       "macro" in results,
        "commodity_tracker":   "commodities" in results,
        "portfolio_strategist":"strategy" in results,
    }
    for name, ready in agents_status.items():
        dot = "🟢" if ready else "⚫"
        st.markdown(f'<div style="color:#94a3b8;font-size:0.82em">{dot} {name}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⏰ Scheduler")
    try:
        from agents.scheduler import get_scheduler_status, start_scheduler, run_morning_analysis as _run_now
        sched_status = get_scheduler_status()
        if sched_status["running"]:
            st.success(f"🟢 Activo — Próximo: {sched_status['next_run']}")
        else:
            st.info("⚫ Scheduler inactivo")
        sc1, sc2 = st.columns(2)
        if sc1.button("▶ Iniciar", key="sched_start", use_container_width=True):
            start_scheduler()
            st.rerun()
        if sc2.button("▶▶ Ahora", key="sched_now", use_container_width=True):
            with st.spinner("Ejecutando análisis..."):
                _run_now()
            st.success("✅ Completado")
    except Exception as _se:
        st.caption(f"Scheduler: {_se}")

    st.markdown("---")
    _active_alerts = (st.session_state.analysis_results or {}).get("alerts", [])
    _alert_count = len(_active_alerts)
    _badge_bg = "#ff4444" if _alert_count > 0 else "#00ff88"
    st.markdown(
        f'### 🔔 Alertas &nbsp;<span style="background:{_badge_bg};color:white;'
        f'padding:1px 8px;border-radius:10px;font-size:0.75em;font-weight:700">{_alert_count}</span>',
        unsafe_allow_html=True,
    )
    if _active_alerts:
        with st.expander("Ver alertas activas"):
            for _a in _active_alerts[:5]:
                _lvl = _a.get("level", "")
                _icon = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}.get(_lvl, "⚪")
                st.markdown(f"{_icon} {_a.get('message', '')}")

    st.markdown("---")
    if results.get("report_path"):
        try:
            with open(results["report_path"], "rb") as f:
                st.download_button("📄 Descargar Reporte PDF", f,
                                   file_name="portfolio_report.pdf",
                                   mime="application/pdf",
                                   use_container_width=True)
        except Exception:
            pass

    # API status
    st.markdown("---")
    if GOOGLE_API_KEY:
        st.success("🟢 Google AI: Activo")
    elif ANTHROPIC_API_KEY:
        st.warning("🟡 Anthropic: Activo")
    else:
        st.error("🔴 Sin clave de IA — análisis básico")

# ─────────────────────────────────────────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if not selected_tickers:
    st.warning("Selecciona al menos un activo en el sidebar.")
    st.stop()

if run_full:
    from orchestrator import PortfolioOrchestrator
    with st.spinner("🔍 Ejecutando análisis completo… (1-2 min)"):
        try:
            orch = PortfolioOrchestrator(selected_tickers)
            st.session_state.analysis_results = orch.run_full_analysis(selected_tickers)
            from datetime import datetime
            st.session_state.last_run = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.rerun()
        except Exception as e:
            st.error(f"Error en análisis completo: {e}")

if run_quick:
    from orchestrator import PortfolioOrchestrator
    with st.spinner("⚡ Actualizando datos rápidos…"):
        try:
            orch = PortfolioOrchestrator(selected_tickers)
            quick = orch.run_quick_analysis(selected_tickers)
            # Merge into existing results
            existing = st.session_state.analysis_results or {}
            existing.update(quick)
            st.session_state.analysis_results = existing
            from datetime import datetime
            st.session_state.last_run = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.rerun()
        except Exception as e:
            st.error(f"Error en update rápido: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 20px 0 10px 0;">
  <h1 style="background: linear-gradient(135deg, #00d4ff, #7c3aed);
             -webkit-background-clip: text;
             -webkit-text-fill-color: transparent;
             font-size: clamp(1.5rem, 5vw, 2.5rem);
             font-weight: 800; margin: 0;">
    {APP_ICON} {APP_TITLE}
  </h1>
  <p style="color: #94a3b8; font-size: clamp(0.8rem, 2vw, 1rem); margin-top: 8px;">
    {APP_SUBTITLE}
  </p>
  <div style="display:flex; justify-content:center; gap:12px; margin-top:12px; flex-wrap:wrap;">
    <span style="background:#00ff8822; color:#00ff88; padding:4px 12px;
                border-radius:20px; font-size:0.75rem; border:1px solid #00ff8844;">
      &#9679; LIVE
    </span>
    <span style="background:#00d4ff22; color:#00d4ff; padding:4px 12px;
                border-radius:20px; font-size:0.75rem; border:1px solid #00d4ff44;">
      {len(ALL_TICKERS)} Activos Monitoreados
    </span>
    <span style="background:#7c3aed22; color:#7c3aed; padding:4px 12px;
                border-radius:20px; font-size:0.75rem; border:1px solid #7c3aed44;">
      Gemini 2.5 Flash IA
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# Status bar
sc1, sc2, sc3 = st.columns(3)
sc1.caption(f"⏱ Última actualización: {st.session_state.last_run or 'Nunca'}")
sc2.caption(f"📊 Tickers monitoreados: {len(selected_tickers)}")
ai_status = ("🟢 Google AI" if GOOGLE_API_KEY else ("🟡 Anthropic" if ANTHROPIC_API_KEY else "🔴 Sin IA"))
sc3.caption(f"🤖 Estado IA: {ai_status}")

# ─────────────────────────────────────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.analysis_results:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;max-width:700px;margin:0 auto">
        <div style="font-size:3.5em;margin-bottom:16px">📊</div>
        <h2 style="background:linear-gradient(135deg,#00d4ff,#7c3aed);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   font-size:1.8em;margin-bottom:12px">
            Bienvenido a Portfolio Intelligence
        </h2>
        <p style="color:#94a3b8;font-size:1.05em;margin-bottom:32px">
            Plataforma de análisis de inversiones con IA multi-agente
        </p>
        <div style="background:rgba(17,24,39,0.8);border:1px solid rgba(0,212,255,0.2);
                    border-radius:16px;padding:28px;text-align:left;max-width:500px;margin:0 auto">
            <p style="color:#00d4ff;font-weight:600;margin-bottom:12px">🚀 Cómo empezar</p>
            <ol style="color:#e2e8f0;line-height:2;margin:0;padding-left:20px">
                <li>Selecciona activos en el sidebar izquierdo</li>
                <li>Elige el período de análisis</li>
                <li>Pulsa <strong style="color:#00d4ff">⚡ Análisis Completo</strong></li>
                <li>Explora los resultados en cada pestaña</li>
            </ol>
        </div>
        <p style="color:#64748b;font-size:0.82em;margin-top:24px">
            💡 Para activar análisis con IA, agrega tu GOOGLE_API_KEY en .env
            (gratuito en <strong>aistudio.google.com</strong>)
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# DATA EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
R = st.session_state.analysis_results
market_data     = R.get("market", {})
esg_data        = R.get("esg", {})
news_data       = R.get("news", [])
risk_data       = R.get("risk", {})
predictions_data= R.get("predictions", {})
macro_data      = R.get("macro", {})
commodities_data= R.get("commodities", {})
strategy_data   = R.get("strategy", {})
alerts_data     = R.get("alerts", [])
prices_df: pd.DataFrame = market_data.get("prices_df", pd.DataFrame())
metrics_map     = market_data.get("metrics", {})
current_prices  = market_data.get("current_prices", {})

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📈 Mercado",
    "🎯 Portfolio Óptimo",
    "⚠️ Riesgo",
    "🌱 ESG",
    "📰 Noticias",
    "🔮 Predicciones ML",
    "🌍 Macro",
    "🥇 Commodities",
    "📊 Backtesting",
    "🔔 Alertas",
    "⚙️ Configuración",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MERCADO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    try:
        perf_vals = [(t, current_prices.get(t, {}).get("change_pct", 0) or 0)
                     for t in selected_tickers if current_prices.get(t, {}).get("price")]
        perf_vals.sort(key=lambda x: x[1])
        worst     = perf_vals[0]  if perf_vals else None
        best      = perf_vals[-1] if perf_vals else None
        avg_sharpe = np.mean([m.get("sharpe_ratio", 0) for m in metrics_map.values()
                               if m.get("sharpe_ratio")]) if metrics_map else 0
        avg_ret    = np.mean([m.get("total_return", 0) for m in metrics_map.values()
                               if m.get("total_return") is not None]) if metrics_map else 0

        # ── 4 metric cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card(
                "Mejor hoy", f"{best[0]}" if best else "N/A",
                delta=f"{best[1]:+.2f}%" if best else None,
                tooltip="Ticker con mayor variación positiva en el día",
                icon="📈", color_acento="#00ff88"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card(
                "Peor hoy", f"{worst[0]}" if worst else "N/A",
                delta=f"{worst[1]:+.2f}%" if worst else None,
                tooltip="Ticker con mayor variación negativa en el día",
                icon="📉", color_acento="#ff4444", positivo_es_bueno=False), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card(
                "Retorno Total Prom.", _pct(avg_ret),
                tooltip="Retorno total promedio del período seleccionado para todos los activos",
                icon="📊", color_acento="#00d4ff"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card(
                "Sharpe Promedio", _f2(avg_sharpe),
                tooltip="Sharpe ratio promedio: retorno ajustado por riesgo (>1 = bueno, >2 = excelente)",
                icon="⚡", color_acento="#7c3aed"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Chart info card + chart
        st.markdown(info_card(
            "Precios Normalizados (Base 100)",
            "Todos los activos se reescalan a 100 en la fecha inicial para comparar desempeño relativo. "
            "Un valor de 120 significa +20% de ganancia desde el inicio del período.",
            icon="📈", tipo="info"), unsafe_allow_html=True)

        if not prices_df.empty:
            valid_cols = [t for t in selected_tickers if t in prices_df.columns]
            if valid_cols:
                norm = prices_df[valid_cols] / prices_df[valid_cols].iloc[0] * 100
                fig  = go.Figure()
                palette = ["#00d4ff","#7c3aed","#00ff88","#ff4444","#f59e0b",
                           "#ec4899","#06b6d4","#8b5cf6","#10b981","#ef4444",
                           "#f97316","#6366f1","#14b8a6","#a855f7","#84cc16"]
                for i, col in enumerate(valid_cols):
                    fig.add_trace(go.Scatter(
                        x=norm.index, y=norm[col],
                        name=f"{col} ({TICKER_NAMES.get(col, col)})",
                        line=dict(color=palette[i % len(palette)], width=2),
                        hovertemplate=f"<b>{col}</b><br>%{{x}}<br>Índice: %{{y:.1f}}<extra></extra>",
                    ))
                fig.update_layout(
                    **_DARK,
                    title=dict(text=f"Desempeño Relativo — {period}",
                               font=dict(color="#e2e8f0", size=14)),
                    xaxis=dict(color="#94a3b8", gridcolor="#1e293b",
                               rangeslider=dict(visible=True, bgcolor="#111827")),
                    yaxis=dict(color="#94a3b8", gridcolor="#1e293b", title="Índice base 100"),
                    legend=dict(bgcolor="#111827", bordercolor="#1e293b", font=dict(color="#94a3b8")),
                    hovermode="x unified", height=430,
                    margin=dict(l=10, r=10, t=45, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Price table with column explainer
        rows = []
        for t in selected_tickers:
            cp  = current_prices.get(t, {})
            met = metrics_map.get(t, {})
            price = cp.get("price")
            chg   = cp.get("change_pct", 0) or 0
            rows.append({
                "Ticker":      t,
                "Nombre":      TICKER_NAMES.get(t, t),
                "Precio":      f"${price:.2f}" if price else "N/A",
                "Hoy %":       f"{chg:+.2f}%",
                "Ret. Total":  _pct(met.get("total_return")),
                "Ret. Anual":  _pct(met.get("annualized_return")),
                "Volatilidad": _pct(met.get("volatility")),
                "Sharpe":      _f2(met.get("sharpe_ratio")),
                "Beta":        _f2(met.get("beta")) if met.get("beta") is not None else "—",
            })
        if rows:
            df_table = pd.DataFrame(rows)
            st.dataframe(
                df_table.style.applymap(
                    lambda v: (f"color: {'#00ff88' if str(v).startswith('+') else '#ff4444' if str(v).startswith('-') else '#e2e8f0'}"),
                    subset=["Hoy %", "Ret. Total", "Ret. Anual"],
                ),
                use_container_width=True, hide_index=True,
            )
            with st.expander("📖 ¿Qué significa cada columna?"):
                st.markdown("""
| Columna | Significado |
|---------|-------------|
| **Hoy %** | Variación del precio respecto al cierre anterior |
| **Ret. Total** | Ganancia/pérdida acumulada en el período seleccionado |
| **Ret. Anual** | Retorno total anualizado (CAGR) |
| **Volatilidad** | Desviación estándar anualizada de los retornos diarios |
| **Sharpe** | Retorno ajustado por riesgo (rf=0%). >1 bueno, >2 excelente |
| **Beta** | Sensibilidad al mercado. >1 = más volátil que el mercado |
""")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🤖 Análisis IA del Mercado")
        if st.button("🤖 Generar análisis IA", key="ai_market_btn"):
            from agents.ai_client import get_ai_response
            lines = []
            for t in selected_tickers[:10]:
                met = metrics_map.get(t, {})
                cp  = current_prices.get(t, {})
                price  = cp.get("price", "N/A")
                ret    = met.get("total_return")
                sharpe = met.get("sharpe_ratio")
                line   = f"{t}: ${price}"
                if ret    is not None: line += f", retorno {ret:.2%}"
                if sharpe is not None: line += f", sharpe {sharpe:.2f}"
                lines.append(line)
            prompt = (
                f"Analiza el estado actual de este portafolio de {len(selected_tickers)} activos en 3 párrafos concisos:\n"
                + "\n".join(lines)
                + "\n\nIncluye: 1) Resumen del desempeño, 2) Activos destacados positiva y negativamente, "
                + "3) Recomendación general. Responde en español."
            )
            with st.spinner("Generando análisis con IA..."):
                ai_analysis = get_ai_response(prompt, max_tokens=600)
            st.markdown(
                f'<div style="background:rgba(17,24,39,0.8);border-left:4px solid #00d4ff;'
                f'border-radius:10px;padding:16px 18px;margin-top:12px">'
                f'<p style="color:#00d4ff;font-weight:600;margin:0 0 10px;font-size:0.9em">'
                f'🤖 Análisis IA</p>'
                f'<p style="color:#cbd5e1;font-size:0.88em;line-height:1.6;white-space:pre-wrap;margin:0">'
                f'{ai_analysis}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.caption(f"⏱ Datos actualizados: {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Mercado: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PORTFOLIO ÓPTIMO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    try:
        alloc     = strategy_data.get("allocation", {})
        weights   = alloc.get("weights", {})
        recs_data = strategy_data.get("recommendations", {}) or {}
        rec_dict  = recs_data.get("recommendations", {}) if isinstance(recs_data, dict) else {}

        # ── Explainer
        st.markdown(info_card(
            "Optimización de Markowitz (Frontera Eficiente)",
            "El modelo maximiza el Sharpe Ratio: retorno esperado dividido por la volatilidad del portfolio. "
            "Los pesos se calculan con Covariance Shrinkage (Ledoit-Wolf) para mayor estabilidad. "
            "Un portfolio eficiente ofrece el máximo retorno para un nivel dado de riesgo.",
            icon="🎯", tipo="info"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 4 metric cards
        n_hold = len([w for w in weights.values() if w > 0.005])
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card("Retorno Esperado", _pct(alloc.get("expected_return")),
                tooltip="Retorno anual esperado del portfolio óptimo",
                icon="📈", color_acento="#00ff88"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Volatilidad", _pct(alloc.get("volatility")),
                tooltip="Volatilidad anualizada esperada del portfolio",
                icon="📉", color_acento="#f59e0b", positivo_es_bueno=False), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("Sharpe Ratio", _f2(alloc.get("sharpe_ratio")),
                tooltip="Retorno ajustado por riesgo (>1 bueno, >2 excelente)",
                icon="⚡", color_acento="#00d4ff"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("Holdings Activos", str(n_hold),
                tooltip="Número de activos con peso significativo (>0.5%)",
                icon="🎯", color_acento="#7c3aed"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_l, col_r = st.columns([1, 1])

        with col_l:
            if weights:
                active  = {k: v for k, v in weights.items() if v > 0.005}
                palette_pie = ["#00d4ff","#7c3aed","#00ff88","#f59e0b","#ff4444",
                               "#ec4899","#06b6d4","#8b5cf6","#10b981","#ef4444"]
                fig_pie = go.Figure(go.Pie(
                    labels=list(active.keys()),
                    values=list(active.values()),
                    hole=0.48,
                    marker=dict(colors=palette_pie, line=dict(color="#0a0e1a", width=2)),
                    textinfo="label+percent",
                    textfont=dict(color="#e2e8f0", size=11),
                    hovertemplate="<b>%{label}</b><br>Peso: %{percent:.1%}<extra></extra>",
                ))
                fig_pie.update_layout(
                    **_DARK,
                    title=dict(text="Asignación Óptima (Max Sharpe)",
                               font=dict(color="#e2e8f0", size=13)),
                    legend=dict(bgcolor="#111827", font=dict(color="#94a3b8", size=11)),
                    height=380, margin=dict(l=10, r=10, t=45, b=10),
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No hay pesos disponibles. Ejecuta el análisis completo.")

        with col_r:
            if rec_dict:
                overall = recs_data.get("overall_outlook", "")
                if overall:
                    st.markdown(info_card("Perspectiva General", overall,
                                         icon="🔮", tipo="info"), unsafe_allow_html=True)
                for tkr, info_r in list(rec_dict.items())[:8]:
                    if not isinstance(info_r, dict): continue
                    action = info_r.get("action", "N/A")
                    just   = info_r.get("justification", "")
                    tw     = info_r.get("target_weight", 0)
                    met_r  = metrics_map.get(tkr, {})
                    st.markdown(recommendation_card(
                        tkr, TICKER_NAMES.get(tkr, tkr),
                        action, just,
                        retorno=_pct(met_r.get("total_return")),
                        sharpe=_f2(met_r.get("sharpe_ratio")),
                    ), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    "Sin recomendaciones de IA",
                    "Ejecuta el <b>Análisis Completo</b> para obtener recomendaciones personalizadas "
                    "generadas por IA para cada activo del portfolio.",
                    icon="🤖", tipo="warning"), unsafe_allow_html=True)
                if weights:
                    wdf = pd.DataFrame([
                        {"Ticker": k, "Nombre": TICKER_NAMES.get(k, k),
                         "Peso (%)": f"{v*100:.1f}%"}
                        for k, v in sorted(weights.items(), key=lambda x: -x[1]) if v > 0.005
                    ])
                    st.dataframe(wdf, use_container_width=True, hide_index=True)

        # ── Risks & Opportunities
        if isinstance(recs_data, dict) and (recs_data.get("key_risks") or recs_data.get("key_opportunities")):
            st.markdown("<br>", unsafe_allow_html=True)
            cr, co = st.columns(2)
            with cr:
                risks_txt = "".join(f"• {r}<br>" for r in recs_data.get("key_risks", []))
                st.markdown(info_card("Riesgos Clave", risks_txt or "—",
                                      icon="⚠️", tipo="danger"), unsafe_allow_html=True)
            with co:
                opps_txt = "".join(f"• {o}<br>" for o in recs_data.get("key_opportunities", []))
                st.markdown(info_card("Oportunidades", opps_txt or "—",
                                      icon="💡", tipo="success"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🔄 Rebalanceo del Portfolio")
        rb_c1, rb_c2 = st.columns([2, 1])
        with rb_c1:
            max_w = st.slider("Peso máximo por activo (%)", 5, 50, 25, 5, key="rb_max") / 100
            min_w = st.slider("Peso mínimo por activo (%)", 0, 10, 2, 1, key="rb_min") / 100
        with rb_c2:
            rb_method = st.radio("Método de optimización", ["max_sharpe", "min_volatility"], key="rb_method")
        if st.button("🔄 Recalcular Portfolio Óptimo", key="rebalance_btn"):
            from agents.portfolio_strategist import optimize_portfolio_full as optimize_portfolio
            with st.spinner("Optimizando con restricciones..."):
                try:
                    new_alloc = optimize_portfolio(selected_tickers, method=rb_method)
                    raw_w     = new_alloc.get("weights", {})
                    constrained = {k: min(max(v, min_w), max_w)
                                   for k, v in raw_w.items() if v > 0.0005}
                    total_cw = sum(constrained.values())
                    if total_cw > 0:
                        constrained = {k: round(v / total_cw, 4) for k, v in constrained.items()}
                    new_alloc["weights"] = constrained
                    st.success(
                        f"✅ Rebalanceo completado — "
                        f"Sharpe: {_f2(new_alloc.get('sharpe_ratio'))} | "
                        f"Ret. Esperado: {_pct(new_alloc.get('expected_return'))} | "
                        f"Volatilidad: {_pct(new_alloc.get('volatility'))}"
                    )
                    if st.session_state.analysis_results:
                        st.session_state.analysis_results.setdefault("strategy", {})["allocation"] = new_alloc
                        st.rerun()
                except Exception as rb_err:
                    st.error(f"Error en rebalanceo: {rb_err}")

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Portfolio: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RIESGO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    try:
        pm     = risk_data.get("portfolio_metrics", {})
        alerts = risk_data.get("alerts", [])
        corr   = risk_data.get("correlation_matrix", {})
        per_t  = risk_data.get("per_ticker_var", {})

        if not pm:
            st.info("Ejecuta el **Análisis Completo** para ver métricas de riesgo.")
        else:
            # ── VaR explainer
            st.markdown(info_card(
                "Value at Risk (VaR) — ¿Qué significa?",
                "El <b>VaR 95%</b> indica la pérdida máxima esperada en un día con un 95% de confianza. "
                "Por ejemplo, VaR=2% significa que en el 95% de los días tu portfolio no perderá más del 2%. "
                "<b>Verde</b> (&lt;1%): riesgo bajo · <b>Naranja</b> (1-3%): moderado · <b>Rojo</b> (&gt;3%): alto",
                icon="⚠️", tipo="warning"), unsafe_allow_html=True)

            var95_pct = abs(float(pm.get("var_95", 0))) * 100

            # ── Gauge (fixed colors)
            gc1, gc2 = st.columns([2, 1])
            with gc1:
                st.plotly_chart(create_var_gauge(var95_pct), use_container_width=True)
            with gc2:
                risk_level = "🟢 Bajo" if var95_pct < 1 else ("🟡 Moderado" if var95_pct < 3 else "🔴 Alto")
                st.markdown(info_card(
                    "Nivel de Riesgo",
                    f'<div style="font-size:1.6em;font-weight:700;text-align:center;margin:8px 0">'
                    f'{risk_level}</div>'
                    f'<div style="text-align:center">VaR 95% = <b>{var95_pct:.2f}%</b> diario</div>',
                    icon="🎯", tipo=("success" if var95_pct < 1 else ("warning" if var95_pct < 3 else "danger"))
                ), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── 4 metric cards
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(metric_card("VaR 99% (1d)", _pct(pm.get("var_99")),
                    tooltip="Pérdida máxima con 99% de confianza — umbral más conservador",
                    icon="📉", color_acento="#ff4444", positivo_es_bueno=False), unsafe_allow_html=True)
            with c2:
                st.markdown(metric_card("CVaR 95%", _pct(pm.get("cvar_95")),
                    tooltip="Pérdida promedio esperada en los peores 5% de días (Conditional VaR)",
                    icon="⚡", color_acento="#f59e0b", positivo_es_bueno=False), unsafe_allow_html=True)
            with c3:
                st.markdown(metric_card("Volatilidad Anual", _pct(pm.get("annual_volatility")),
                    tooltip="Desviación estándar de retornos anualizada. <15% baja, 15-30% media, >30% alta",
                    icon="📊", color_acento="#00d4ff", positivo_es_bueno=False), unsafe_allow_html=True)
            with c4:
                hhi = pm.get("hhi_concentration", 0)
                hhi_tipo = "success" if (hhi or 0) < 0.15 else ("warning" if (hhi or 0) < 0.25 else "danger")
                st.markdown(metric_card("Concentración HHI", _f2(hhi),
                    tooltip="Índice Herfindahl-Hirschman. <0.15 diversificado, >0.25 concentrado",
                    icon="🎯", color_acento="#7c3aed", positivo_es_bueno=False), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Risk alerts
            if alerts:
                for alert in alerts:
                    lvl = alert.get("level", "bajo")
                    msg = alert.get("message", "")
                    tipo_map = {"alto": "danger", "medio": "warning", "bajo": "success"}
                    icon_map = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}
                    st.markdown(info_card(
                        f"Alerta de Riesgo [{lvl.upper()}]", msg,
                        icon=icon_map.get(lvl, "⚪"),
                        tipo=tipo_map.get(lvl, "info")), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Correlation explainer + heatmap
            st.markdown(info_card(
                "Matriz de Correlación",
                "Muestra cómo se mueven los activos entre sí. "
                "<b>Azul fuerte (+1)</b>: se mueven juntos (diversificación baja). "
                "<b>Rojo fuerte (-1)</b>: se mueven opuestos (cobertura natural). "
                "Un buen portfolio mezcla activos con baja correlación entre sí.",
                icon="🔗", tipo="info"), unsafe_allow_html=True)

            if corr:
                corr_df = pd.DataFrame(corr)
                valid_t = [t for t in selected_tickers
                           if t in corr_df.columns and t in corr_df.index]
                if valid_t:
                    sub   = corr_df.loc[valid_t, valid_t].astype(float)
                    fig_h = px.imshow(
                        sub, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        title="Correlación de Retornos Diarios",
                        text_auto=".2f",
                        **_DARK,
                    )
                    fig_h.update_layout(
                        coloraxis_colorbar=dict(
                            tickfont=dict(color="#94a3b8"),
                            title=dict(font=dict(color="#94a3b8"))),
                        title_font_color="#e2e8f0",
                        title_font_size=13,
                        margin=dict(l=10, r=10, t=45, b=10),
                    )
                    st.plotly_chart(fig_h, use_container_width=True)

            # ── Per-ticker VaR table
            if per_t:
                st.markdown("#### 📊 VaR por Activo")
                vr = [{"Ticker": t, "Nombre": d.get("name", t),
                        "VaR 95% (1d)": _pct(d.get("var_95")),
                        "Volatilidad Anual": _pct(d.get("volatility"))}
                      for t, d in per_t.items() if t in selected_tickers]
                if vr:
                    st.dataframe(pd.DataFrame(vr), use_container_width=True, hide_index=True)

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Riesgo: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ESG
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    try:
        if not esg_data:
            st.info("Ejecuta el **Análisis Completo** para ver datos ESG.")
        else:
            # ── ESG explainer
            st.markdown(info_card(
                "¿Qué mide el score ESG?",
                "<b>E</b>nvironmental (0-100): impacto ambiental, emisiones, gestión de recursos. "
                "<b>S</b>ocial (0-100): relación con empleados, comunidades, cadena de suministro. "
                "<b>G</b>overnance (0-100): transparencia, estructura de directiva, ética corporativa. "
                "Score total >50 = cumple umbrales mínimos. <b>🟢 Verde</b> &gt;70 · <b>🟡 Amarillo</b> 50-70 · <b>🔴 Rojo</b> &lt;50.",
                icon="🌱", tipo="success"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Color-coded score cards
            active_esg = {t: v for t, v in esg_data.items() if t in selected_tickers}
            if active_esg:
                cards_per_row = 4
                items = list(active_esg.items())
                for row_start in range(0, len(items), cards_per_row):
                    cols = st.columns(min(cards_per_row, len(items) - row_start))
                    for ci, (t, info) in enumerate(items[row_start:row_start + cards_per_row]):
                        total = info.get("total_score", 0) or 0
                        tl    = info.get("traffic_light", "rojo")
                        color_map = {"verde": "#00ff88", "amarillo": "#f59e0b", "rojo": "#ff4444"}
                        tc    = color_map.get(tl, "#94a3b8")
                        e_s   = info.get("environmental_score", "—")
                        s_s   = info.get("social_score", "—")
                        g_s   = info.get("governance_score", "—")
                        comp  = "✅" if info.get("compliant") else "❌"
                        with cols[ci]:
                            st.markdown(
                                f'<div style="background:rgba(17,24,39,0.85);border:1px solid {tc}2a;'
                                f'border-top:3px solid {tc};border-radius:13px;padding:16px 14px;'
                                f'text-align:center;box-shadow:0 4px 18px rgba(0,0,0,0.3)">'
                                f'<div style="color:{tc};font-weight:700;font-size:1.0em">{_traffic_emoji(tl)} {t}</div>'
                                f'<div style="color:#64748b;font-size:0.78em;margin:2px 0 8px">{TICKER_NAMES.get(t, t)}</div>'
                                f'<div style="font-size:2em;font-weight:800;color:{tc}">{total}</div>'
                                f'<div style="color:#475569;font-size:0.72em;margin-bottom:10px">Score Total</div>'
                                f'<div style="display:flex;justify-content:space-around;font-size:0.78em">'
                                f'<div><div style="color:#00ff88">🌍</div><div style="color:#e2e8f0;font-weight:600">{e_s}</div></div>'
                                f'<div><div style="color:#00d4ff">👥</div><div style="color:#e2e8f0;font-weight:600">{s_s}</div></div>'
                                f'<div><div style="color:#7c3aed">🏛️</div><div style="color:#e2e8f0;font-weight:600">{g_s}</div></div>'
                                f'</div>'
                                f'<div style="margin-top:10px;font-size:0.78em;color:#64748b">{comp} Cumple estándares</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Bar chart
            valid_esg = {
                t: v for t, v in esg_data.items()
                if t in selected_tickers
                and all(isinstance(v.get(k), (int, float))
                        for k in ["environmental_score", "social_score", "governance_score"])
            }
            if valid_esg:
                esg_rows = []
                for t, info in valid_esg.items():
                    for dim, col in [("environmental_score", "E 🌍"),
                                     ("social_score", "S 👥"),
                                     ("governance_score", "G 🏛️")]:
                        esg_rows.append({"Ticker": t, "Dimensión": col, "Score": info[dim]})
                fig_esg = px.bar(
                    pd.DataFrame(esg_rows), x="Score", y="Ticker",
                    color="Dimensión", barmode="group", orientation="h",
                    title="Scores ESG por Dimensión (0–100)",
                    color_discrete_map={"E 🌍": "#00ff88", "S 👥": "#00d4ff", "G 🏛️": "#7c3aed"},
                    **_DARK,
                )
                fig_esg.add_vline(x=50, line_dash="dot", line_color="#ff4444",
                                  annotation_text="Umbral mínimo (50)",
                                  annotation_font_color="#ff4444")
                fig_esg.update_layout(
                    title_font_color="#e2e8f0", title_font_size=13,
                    xaxis=dict(range=[0, 100], color="#94a3b8", gridcolor="#1e293b"),
                    yaxis=dict(color="#94a3b8"),
                    legend=dict(bgcolor="#111827"),
                    height=max(300, len(valid_esg) * 65),
                    margin=dict(l=10, r=10, t=45, b=10),
                )
                st.plotly_chart(fig_esg, use_container_width=True)

            # ── Issues
            issues = [(t, iss) for t, info in esg_data.items()
                      if t in selected_tickers for iss in info.get("issues", [])]
            if issues:
                for t, iss in issues:
                    st.markdown(info_card(f"Incumplimiento ESG — {t}", iss,
                                         icon="⚠️", tipo="danger"), unsafe_allow_html=True)
            else:
                st.markdown(info_card(
                    "Cumplimiento ESG",
                    "✅ Todos los activos seleccionados cumplen los umbrales ESG mínimos.",
                    icon="🌱", tipo="success"), unsafe_allow_html=True)

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab ESG: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — NOTICIAS & SENTIMIENTO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    try:
        if not news_data:
            st.info("Ejecuta el **Análisis Completo** para ver noticias.")
        else:
            # ── Explainer
            pos_count  = sum(1 for n in news_data if n.get("sentiment") == "positivo")
            neg_count  = sum(1 for n in news_data if n.get("sentiment") == "negativo")
            high_count = sum(1 for n in news_data if n.get("impact") == "alto")
            st.markdown(info_card(
                f"Resumen de Sentimiento — {len(news_data)} noticias analizadas",
                f"<b style='color:#00ff88'>{pos_count} positivas</b> · "
                f"<b style='color:#ff4444'>{neg_count} negativas</b> · "
                f"<b style='color:#f59e0b'>{len(news_data)-pos_count-neg_count} neutras</b> · "
                f"<b style='color:#ff4444'>{high_count} de alto impacto</b>. "
                "El sentimiento se determina con IA analizando el titular y contexto de cada noticia.",
                icon="📰", tipo="info"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Filters
            fc1, fc2 = st.columns([1, 2])
            with fc1:
                filt_ticker = st.selectbox(
                    "Filtrar por ticker",
                    options=["Todos"] + sorted({n.get("ticker", "") for n in news_data}),
                )
            with fc2:
                filt_sent = st.multiselect(
                    "Sentimiento",
                    options=["positivo", "neutro", "negativo"],
                    default=["positivo", "neutro", "negativo"],
                )

            filtered = [n for n in news_data
                        if (filt_ticker == "Todos" or n.get("ticker") == filt_ticker)
                        and n.get("sentiment", "neutro") in filt_sent]

            st.markdown("<br>", unsafe_allow_html=True)

            if filtered:
                # Grid 2 columns with news_card
                for i in range(0, len(filtered[:24]), 2):
                    col_l, col_r = st.columns(2)
                    for col, idx in [(col_l, i), (col_r, i + 1)]:
                        if idx >= len(filtered):
                            break
                        n = filtered[idx]
                        with col:
                            st.markdown(news_card(
                                headline=n.get("headline", ""),
                                sentiment=n.get("sentiment", "neutro"),
                                impact=n.get("impact", "medio"),
                                summary=n.get("summary", ""),
                                ticker=n.get("ticker", ""),
                                time_ago=f'{n.get("source","")} · {n.get("published_at","")}',
                            ), unsafe_allow_html=True)
            else:
                st.info("No hay noticias con los filtros seleccionados.")

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Noticias: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PREDICCIONES ML
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    try:
        if not predictions_data:
            st.info("Ejecuta el **Análisis Completo** para ver predicciones.")
        else:
            # ── ML explainer
            st.markdown(info_card(
                "Modelo de Predicción — Random Forest + Análisis Técnico",
                "Se entrena un modelo <b>Random Forest</b> con features de momentum, volatilidad, RSI, "
                "MACD y medias móviles. La dirección (📈/📉) indica la tendencia esperada a 5 días. "
                "La <b>confianza</b> refleja la probabilidad del modelo — valores &gt;65% son más fiables. "
                "Los rangos Optimista/Base/Pesimista son percentiles 75/50/25 del histórico reciente.",
                icon="🔮", tipo="info"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Visual prediction cards
            pred_items = [(t, p) for t, p in predictions_data.items()
                          if t in selected_tickers and not p.get("error")]
            cards_per_row = 3
            for row_start in range(0, len(pred_items), cards_per_row):
                cols = st.columns(min(cards_per_row, len(pred_items) - row_start))
                for ci, (t, p) in enumerate(pred_items[row_start:row_start + cards_per_row]):
                    d        = p.get("direction", "neutral")
                    conf     = p.get("confidence", 0.5)
                    d_color  = {"up": "#00ff88", "down": "#ff4444", "neutral": "#94a3b8"}.get(d, "#94a3b8")
                    d_arrow  = {"up": "📈", "down": "📉", "neutral": "➡️"}.get(d, "➡️")
                    d_label  = {"up": "ALCISTA", "down": "BAJISTA", "neutral": "NEUTRAL"}.get(d, d.upper())
                    conf_pct = int(conf * 100)
                    curr_p   = p.get("current_price", "—")
                    opt_p    = p.get("optimistic", "—")
                    base_p   = p.get("base", "—")
                    pess_p   = p.get("pessimistic", "—")
                    bar_w    = int(conf_pct)
                    with cols[ci]:
                        st.markdown(
                            f'<div style="background:rgba(17,24,39,0.88);border:1px solid {d_color}2a;'
                            f'border-top:3px solid {d_color};border-radius:13px;padding:16px 14px;'
                            f'box-shadow:0 4px 18px rgba(0,0,0,0.28)">'
                            f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                            f'<div>'
                            f'<div style="color:#e2e8f0;font-weight:700;font-size:1.05em">{t}</div>'
                            f'<div style="color:#475569;font-size:0.78em">{TICKER_NAMES.get(t, t)}</div>'
                            f'</div>'
                            f'<span style="font-size:1.8em">{d_arrow}</span>'
                            f'</div>'
                            f'<div style="margin:10px 0 6px">'
                            f'<div style="color:{d_color};font-weight:700;font-size:0.9em;margin-bottom:5px">'
                            f'{d_label}</div>'
                            f'<div style="background:#1e293b;border-radius:4px;height:6px;overflow:hidden">'
                            f'<div style="background:{d_color};width:{bar_w}%;height:100%;border-radius:4px;'
                            f'transition:width 0.5s ease"></div>'
                            f'</div>'
                            f'<div style="color:#475569;font-size:0.73em;margin-top:3px">Confianza: '
                            f'<b style="color:{d_color}">{conf_pct}%</b></div>'
                            f'</div>'
                            f'<div style="border-top:1px solid #1e293b;margin-top:8px;padding-top:8px;'
                            f'display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:0.76em">'
                            f'<div style="color:#64748b">Actual</div>'
                            f'<div style="color:#e2e8f0;font-weight:600">${curr_p}</div>'
                            f'<div style="color:#00ff88">Optimista</div>'
                            f'<div style="color:#00ff88;font-weight:600">${opt_p}</div>'
                            f'<div style="color:#94a3b8">Base</div>'
                            f'<div style="color:#94a3b8;font-weight:600">${base_p}</div>'
                            f'<div style="color:#ff4444">Pesimista</div>'
                            f'<div style="color:#ff4444;font-weight:600">${pess_p}</div>'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Confidence bar chart
            conf_data = [(t, p.get("confidence", 0.5), p.get("direction", "neutral"))
                         for t, p in predictions_data.items()
                         if t in selected_tickers and not p.get("error")]
            if conf_data:
                df_conf = pd.DataFrame(conf_data, columns=["Ticker", "Confianza", "Dirección"])
                df_conf["Color"] = df_conf["Dirección"].map(
                    {"up": "#00ff88", "down": "#ff4444", "neutral": "#94a3b8"})
                fig_conf = go.Figure()
                for _, row in df_conf.iterrows():
                    fig_conf.add_trace(go.Bar(
                        x=[row["Ticker"]], y=[row["Confianza"]],
                        marker_color=row["Color"], name=row["Ticker"],
                        hovertemplate=(f"<b>{row['Ticker']}</b><br>Confianza: {row['Confianza']:.1%}<br>"
                                       f"Dirección: {row['Dirección']}<extra></extra>"),
                    ))
                fig_conf.update_layout(
                    **_DARK,
                    title=dict(text="Confianza del Modelo por Activo",
                               font=dict(color="#e2e8f0", size=13)),
                    yaxis=dict(range=[0, 1], tickformat=".0%",
                               color="#94a3b8", gridcolor="#1e293b"),
                    xaxis=dict(color="#94a3b8"),
                    showlegend=False, height=300,
                    margin=dict(l=10, r=10, t=45, b=10),
                )
                fig_conf.add_hline(y=0.5, line_dash="dot", line_color="#475569",
                                   annotation_text="50% (neutral)",
                                   annotation_font_color="#475569")
                st.plotly_chart(fig_conf, use_container_width=True)

            st.markdown(info_card(
                "Aviso importante",
                "⚠️ Predicciones estadísticas basadas en datos históricos. "
                "No constituyen asesoría financiera. Rendimiento pasado no garantiza resultados futuros.",
                icon="⚠️", tipo="warning"), unsafe_allow_html=True)

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Predicciones: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — MACRO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    try:
        if not macro_data:
            st.info("Ejecuta el **Análisis Completo** para ver datos macro.")
        else:
            indicators = macro_data.get("indicators", {})
            analysis   = macro_data.get("analysis", "")

            # 4 métricas grandes
            key_order = ["fed_funds_rate","cpi_yoy","unemployment_rate","gdp_growth_qoq"]
            cols = st.columns(4)
            for i, key in enumerate(key_order):
                info = indicators.get(key, {})
                if isinstance(info, dict):
                    cols[i].metric(info.get("label", key),
                                   f"{info.get('value','N/A')}{info.get('unit','')}")

            # Indicadores secundarios
            secondary = {k:v for k,v in indicators.items() if k not in key_order}
            if secondary:
                s_cols = st.columns(len(secondary))
                for i,(k,v) in enumerate(secondary.items()):
                    if isinstance(v,dict):
                        s_cols[i].metric(v.get("label",k), f"{v.get('value','N/A')}{v.get('unit','')}")

            st.markdown("---")

            if analysis:
                st.markdown("#### 🤖 Análisis de Impacto — IA")
                # Separar en párrafos y usar callouts por tema
                paras = [p.strip() for p in analysis.split("\n\n") if p.strip()]
                icons = ["💻", "🥇", "📊"]
                titles = ["Impacto en Acciones Tech", "Impacto en Commodities", "Recomendación de Posicionamiento"]
                for i, para in enumerate(paras[:3]):
                    icon  = icons[i] if i < len(icons) else "📌"
                    title = titles[i] if i < len(titles) else ""
                    st.markdown(
                        f'<div style="background:rgba(17,24,39,0.8);border-left:3px solid #00d4ff;'
                        f'border-radius:8px;padding:14px;margin-bottom:12px">'
                        f'<p style="color:#00d4ff;font-weight:600;margin:0 0 6px">{icon} {title}</p>'
                        f'<p style="color:#e2e8f0;margin:0;font-size:0.90em">{para}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                if len(paras) > 3:
                    with st.expander("Ver análisis completo"):
                        for para in paras[3:]:
                            st.write(para)

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Macro: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — COMMODITIES
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    try:
        signals     = commodities_data.get("signals", {})
        comm_prices = commodities_data.get("prices_df", pd.DataFrame())

        if not signals and comm_prices.empty:
            st.info("Ejecuta el **Análisis Completo** para ver commodities.")
        else:
            # 4 cards de commodities
            if signals:
                c_cols = st.columns(min(len(signals), 4))
                for i, (ticker, info) in enumerate(signals.items()):
                    price    = info.get("current_price", 0)
                    m_chg    = info.get("monthly_change", 0) or 0
                    trend    = info.get("trend", "lateral")
                    signal   = info.get("signal", "MANTENER")
                    rsi_val  = info.get("rsi")
                    corr_spy = info.get("corr_spy")
                    chg_color  = "#00ff88" if m_chg > 0 else "#ff4444"
                    trend_icon = {"alcista":"📈","bajista":"📉","lateral":"➡️"}.get(trend,"➡️")
                    sig_color  = {"COMPRAR":"#00ff88","VENDER":"#ff4444","MANTENER":"#f59e0b"}.get(signal,"#94a3b8")
                    with c_cols[i % 4]:
                        st.markdown(
                            f'<div style="background:rgba(17,24,39,0.8);border:1px solid rgba(0,212,255,0.2);'
                            f'border-radius:14px;padding:20px;text-align:center;height:220px">'
                            f'<div style="color:#00d4ff;font-weight:700;font-size:1em;margin-bottom:4px">'
                            f'{TICKER_NAMES.get(ticker,ticker)}</div>'
                            f'<div style="color:#e2e8f0;font-size:1.7em;font-weight:800">${price:.2f}</div>'
                            f'<div style="color:{chg_color};font-size:0.95em;margin:4px 0">'
                            f'{m_chg:+.2%} (1M)</div>'
                            f'<div style="color:#94a3b8;font-size:0.85em;margin:4px 0">'
                            f'{trend_icon} {trend.capitalize()}</div>'
                            f'{"<div style=color:#94a3b8;font-size:0.8em>RSI: "+str(round(rsi_val,1))+"</div>" if rsi_val else ""}'
                            f'<div style="background:{sig_color}22;border:1px solid {sig_color}66;'
                            f'border-radius:6px;padding:4px 10px;margin-top:8px;display:inline-block;'
                            f'color:{sig_color};font-weight:700;font-size:0.88em">{signal}</div>'
                            f'{"<div style=color:#64748b;font-size:0.78em;margin-top:4px>Corr SPY: "+str(corr_spy)+"</div>" if corr_spy else ""}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            st.markdown("---")

            # Gráfica histórica
            if not comm_prices.empty:
                norm_c = comm_prices / comm_prices.iloc[0] * 100
                fig_c = go.Figure()
                palette_c = {"GC=F":"#f59e0b","CL=F":"#6366f1","SI=F":"#94a3b8","NG=F":"#00d4ff"}
                for col in norm_c.columns:
                    fig_c.add_trace(go.Scatter(
                        x=norm_c.index, y=norm_c[col],
                        name=TICKER_NAMES.get(col,col),
                        line=dict(color=palette_c.get(col,"#e2e8f0"), width=2.5),
                    ))
                fig_c.update_layout(
                    **_DARK,
                    title=dict(text="Commodities — Precios Normalizados (base 100)",
                               font=dict(color="#e2e8f0")),
                    xaxis=dict(color="#94a3b8", gridcolor="#1e293b"),
                    yaxis=dict(color="#94a3b8", gridcolor="#1e293b"),
                    legend=dict(bgcolor="#111827"),
                    hovermode="x unified", height=360,
                )
                st.plotly_chart(fig_c, use_container_width=True)

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Commodities: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — BACKTESTING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    try:
        st.markdown("#### 📊 Backtesting del Portfolio")

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            bt_start = st.date_input(
                "Fecha inicio",
                value=pd.Timestamp.now() - pd.DateOffset(years=1),
                key="bt_start",
            )
        with bc2:
            bt_end = st.date_input("Fecha fin", value=pd.Timestamp.now(), key="bt_end")
        with bc3:
            bt_bench = st.selectbox("Benchmark", ["SPY", "QQQ", "GLD", "TLT"], key="bt_bench")

        if st.button("🚀 Ejecutar Backtest", key="run_backtest_btn"):
            from orchestrator import PortfolioOrchestrator
            bt_weights = strategy_data.get("allocation", {}).get("weights", {})
            bt_orch = PortfolioOrchestrator(selected_tickers)
            with st.spinner("Ejecutando backtest... (puede tomar unos segundos)"):
                bt_results = bt_orch.run_backtest(
                    tickers=selected_tickers,
                    weights=bt_weights,
                    start_date=str(bt_start),
                    end_date=str(bt_end),
                    benchmark=bt_bench,
                )
            st.session_state["bt_results"] = bt_results

        bt_results = st.session_state.get("bt_results")
        if bt_results:
            if "error" in bt_results:
                st.error(bt_results["error"])
            else:
                port_m  = bt_results.get("portfolio", {})
                bench_m = bt_results.get("benchmark", {})

                mc1, mc2, mc3, mc4 = st.columns(4)
                alpha_val = bt_results.get("alpha")
                mc1.metric(
                    "Retorno Total",
                    _pct(port_m.get("total_return")),
                    delta=f"α {_pct(alpha_val)}" if alpha_val is not None else None,
                )
                mc2.metric("Retorno Anual", _pct(port_m.get("annualized_return")))
                mc3.metric("Sharpe Ratio",  _f2(port_m.get("sharpe_ratio")))
                mc4.metric("Max Drawdown",  _pct(port_m.get("max_drawdown")))

                cum_data = bt_results.get("cumulative_returns", {})
                if cum_data.get("dates"):
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Scatter(
                        x=cum_data["dates"],
                        y=[(v - 1) * 100 for v in cum_data.get("portfolio", [])],
                        name="Portfolio",
                        line=dict(color="#00d4ff", width=2.5),
                        hovertemplate="Portfolio<br>%{x}<br>%{y:.2f}%<extra></extra>",
                    ))
                    if cum_data.get("benchmark"):
                        fig_bt.add_trace(go.Scatter(
                            x=cum_data["dates"],
                            y=[(v - 1) * 100 for v in cum_data["benchmark"]],
                            name=bt_bench,
                            line=dict(color="#f59e0b", width=2, dash="dash"),
                            hovertemplate=f"{bt_bench}<br>%{{x}}<br>%{{y:.2f}}%<extra></extra>",
                        ))
                    fig_bt.update_layout(
                        **_DARK,
                        title=dict(text="Retorno Acumulado (%)", font=dict(color="#e2e8f0")),
                        xaxis=dict(color="#94a3b8", gridcolor="#1e293b"),
                        yaxis=dict(color="#94a3b8", gridcolor="#1e293b", ticksuffix="%"),
                        legend=dict(bgcolor="#111827"),
                        hovermode="x unified", height=400,
                    )
                    st.plotly_chart(fig_bt, use_container_width=True)

                if bench_m:
                    st.markdown("##### Comparación vs Benchmark")
                    comp = pd.DataFrame([
                        {"Métrica": "Retorno Total",   "Portfolio": _pct(port_m.get("total_return")),         bt_bench: _pct(bench_m.get("total_return"))},
                        {"Métrica": "Retorno Anual",   "Portfolio": _pct(port_m.get("annualized_return")),    bt_bench: _pct(bench_m.get("annualized_return"))},
                        {"Métrica": "Volatilidad",     "Portfolio": _pct(port_m.get("annualized_volatility")),bt_bench: _pct(bench_m.get("annualized_volatility"))},
                        {"Métrica": "Sharpe Ratio",    "Portfolio": _f2(port_m.get("sharpe_ratio")),          bt_bench: _f2(bench_m.get("sharpe_ratio"))},
                        {"Métrica": "Alpha",           "Portfolio": _pct(bt_results.get("alpha")),            bt_bench: "—"},
                    ])
                    st.dataframe(comp, use_container_width=True, hide_index=True)

        elif not st.session_state.get("bt_results"):
            st.info("Configura el período y pulsa **🚀 Ejecutar Backtest** para comparar tu portfolio vs benchmark.")
    except Exception as e:
        st.error(f"Error en tab Backtesting: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 10 — ALERTAS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[9]:
    try:
        from agents.alert_manager import get_alerts_history, ALERT_THRESHOLDS, send_email_alert

        st.markdown("#### 🔔 Panel de Alertas")

        # Active alerts
        if alerts_data:
            st.markdown("##### ⚡ Alertas del Último Análisis")
            level_fn = {"alto": st.error, "medio": st.warning, "bajo": st.success}
            for _a in alerts_data:
                _lvl  = _a.get("level", "bajo")
                _icon = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}.get(_lvl, "⚪")
                level_fn.get(_lvl, st.info)(f"{_icon} **[{_lvl.upper()}]** {_a.get('message', '')}")
        else:
            st.success("✅ No hay alertas activas en el análisis actual.")

        st.markdown("---")

        # Threshold display
        st.markdown("##### ⚙️ Umbrales de Alerta Configurados")
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("VaR 95% máximo",      f"{ALERT_THRESHOLDS['var_95_max']:.0%}")
        tc1.metric("Volatilidad máxima",  f"{ALERT_THRESHOLDS['volatility_max']:.0%}")
        tc2.metric("Sharpe mínimo",        str(ALERT_THRESHOLDS["sharpe_min"]))
        tc2.metric("Concentración HHI máx.", str(ALERT_THRESHOLDS["concentration_max"]))
        tc3.metric("Noticias neg. máx.",   str(ALERT_THRESHOLDS["negative_news_max"]))

        st.markdown("---")

        # Email alert
        st.markdown("##### 📧 Enviar Alertas por Email")
        alert_email = st.text_input("Email receptor", placeholder="tu@email.com", key="alert_email_input")
        if st.button("📨 Enviar alertas por email", key="send_alert_email_btn"):
            if not alert_email:
                st.warning("Introduce un email receptor")
            elif not alerts_data:
                st.info("No hay alertas activas para enviar")
            else:
                ok = send_email_alert(alerts_data, alert_email)
                if ok:
                    st.success("✅ Email enviado correctamente")
                else:
                    st.error("❌ Error enviando email — configura las credenciales SMTP en el código")

        st.markdown("---")

        # Alerts history
        st.markdown("##### 📋 Historial de Alertas")
        hist = get_alerts_history(limit=20)
        if hist:
            hist_df = pd.DataFrame([
                {
                    "Fecha":   h.get("timestamp", "")[:16],
                    "Nivel":   h.get("level", ""),
                    "Tipo":    h.get("type", ""),
                    "Mensaje": h.get("message", ""),
                }
                for h in hist
            ])
            st.dataframe(hist_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay historial de alertas. Ejecuta el **Análisis Completo** para generar alertas.")

        st.caption(f"⏱ {st.session_state.last_run}")
    except Exception as e:
        st.error(f"Error en tab Alertas: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 11 — CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
with tabs[10]:
    try:
        from config import NEWS_API_KEY as _NEWS_KEY, FRED_API_KEY as _FRED_KEY, ALPHA_VANTAGE_KEY as _AV_KEY

        # ── SECCIÓN 1: Personalización ────────────────────────────────────────
        st.markdown("##### 🎨 Personalización de la App")
        cfg_c1, cfg_c2 = st.columns(2)
        with cfg_c1:
            new_title    = st.text_input("Nombre de la app",  value=APP_TITLE,    key="cfg_title_in")
            new_subtitle = st.text_input("Subtítulo",         value=APP_SUBTITLE, key="cfg_sub_in")
        with cfg_c2:
            icon_opts = ["🧠", "🚀", "💼", "📊", "💰", "🎯"]
            cur_idx   = icon_opts.index(APP_ICON) if APP_ICON in icon_opts else 0
            new_icon  = st.selectbox("Icono", icon_opts, index=cur_idx, key="cfg_icon_in")

        if st.button("💾 Guardar preferencias", key="cfg_save_pref"):
            try:
                env_path = ".env"
                with open(env_path) as _f:
                    _lines = _f.readlines()
                _updated = set()
                _new_lines = []
                for _l in _lines:
                    if _l.startswith("APP_TITLE="):
                        _new_lines.append(f"APP_TITLE={new_title}\n"); _updated.add("APP_TITLE")
                    elif _l.startswith("APP_SUBTITLE="):
                        _new_lines.append(f"APP_SUBTITLE={new_subtitle}\n"); _updated.add("APP_SUBTITLE")
                    elif _l.startswith("APP_ICON="):
                        _new_lines.append(f"APP_ICON={new_icon}\n"); _updated.add("APP_ICON")
                    else:
                        _new_lines.append(_l)
                for _k, _v in [("APP_TITLE", new_title), ("APP_SUBTITLE", new_subtitle), ("APP_ICON", new_icon)]:
                    if _k not in _updated:
                        _new_lines.append(f"{_k}={_v}\n")
                with open(env_path, "w") as _f:
                    _f.writelines(_new_lines)
                st.success("✅ Guardado. Reinicia el dashboard para ver los cambios.")
            except Exception as _ce:
                st.error(f"Error: {_ce}")

        # ── SECCIÓN 2: API Keys ───────────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 🔑 Estado de API Keys")
        _api_info = [
            ("Google Gemini",  GOOGLE_API_KEY, "https://aistudio.google.com",                          "Gratis · 1 000+ req/día"),
            ("News API",       _NEWS_KEY,       "https://newsapi.org",                                  "Gratis · 100 req/día"),
            ("FRED API",       _FRED_KEY,       "https://fred.stlouisfed.org/docs/api/api_key.html",    "Gratis · ilimitado"),
            ("Alpha Vantage",  _AV_KEY,         "https://www.alphavantage.co/support/#api-key",         "Gratis · 25 req/día"),
        ]
        for _name, _key, _url, _note in _api_info:
            if _key:
                st.success(f"✅ **{_name}**: Configurada  `{_key[:10]}…`")
            else:
                st.warning(f"⚠️ **{_name}**: No configurada — [Obtener gratis]({_url})  •  {_note}")

        with st.expander("🔧 Agregar o actualizar API keys"):
            _in_google = st.text_input("Google API Key",    type="password", key="cfg_k_google")
            _in_news   = st.text_input("News API Key",      type="password", key="cfg_k_news")
            _in_fred   = st.text_input("FRED API Key",      type="password", key="cfg_k_fred")
            _in_av     = st.text_input("Alpha Vantage Key", type="password", key="cfg_k_av")
            if st.button("💾 Guardar keys", key="cfg_save_keys"):
                try:
                    _kmap = {"GOOGLE_API_KEY": _in_google, "NEWS_API_KEY": _in_news,
                             "FRED_API_KEY": _in_fred, "ALPHA_VANTAGE_KEY": _in_av}
                    with open(".env") as _f:
                        _lines = _f.readlines()
                    _up2 = set()
                    _nl2 = []
                    for _l in _lines:
                        _matched = False
                        for _kk, _vv in _kmap.items():
                            if _l.startswith(f"{_kk}=") and _vv:
                                _nl2.append(f"{_kk}={_vv}\n"); _up2.add(_kk); _matched = True; break
                        if not _matched:
                            _nl2.append(_l)
                    for _kk, _vv in _kmap.items():
                        if _kk not in _up2 and _vv:
                            _nl2.append(f"{_kk}={_vv}\n")
                    with open(".env", "w") as _f:
                        _f.writelines(_nl2)
                    st.success("✅ Keys guardadas. Reinicia para aplicar.")
                except Exception as _ke:
                    st.error(f"Error: {_ke}")

        # ── SECCIÓN 3: Universo de Activos ────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 📊 Universo de Activos")
        _uc1, _uc2, _uc3 = st.columns(3)
        with _uc1:
            st.markdown("**📈 Acciones**")
            for _t in UNIVERSE["stocks"]:
                st.markdown(f'<span style="color:#00d4ff;font-size:0.85em">• {_t}</span>', unsafe_allow_html=True)
        with _uc2:
            st.markdown("**🥇 Commodities**")
            for _t in UNIVERSE["commodities"]:
                st.markdown(f'<span style="color:#f59e0b;font-size:0.85em">• {_t} ({TICKER_NAMES.get(_t,_t)})</span>', unsafe_allow_html=True)
        with _uc3:
            st.markdown("**📦 ETFs**")
            for _t in UNIVERSE["etfs"]:
                st.markdown(f'<span style="color:#7c3aed;font-size:0.85em">• {_t} ({TICKER_NAMES.get(_t,_t)})</span>', unsafe_allow_html=True)

        _new_ticker = st.text_input("Agregar ticker (ej: TSMC, BABA, GS):", key="cfg_new_ticker").upper().strip()
        _vcol1, _vcol2 = st.columns(2)
        if _vcol1.button("🔍 Verificar ticker", key="cfg_verify_btn"):
            if _new_ticker:
                with st.spinner(f"Verificando {_new_ticker}..."):
                    try:
                        import yfinance as yf
                        _info = yf.Ticker(_new_ticker).fast_info
                        _price = _info.last_price
                        if _price:
                            st.success(f"✅ **{_new_ticker}** válido — Precio actual: ${_price:.2f}")
                            st.session_state["verified_ticker"] = _new_ticker
                        else:
                            st.error(f"❌ {_new_ticker} no encontrado o sin precio")
                    except Exception as _ve:
                        st.error(f"❌ Error: {_ve}")
            else:
                st.warning("Introduce un ticker primero")

        # ── SECCIÓN 4: Scheduler ──────────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### ⏰ Análisis Automático")
        from agents.scheduler import get_scheduler_status, start_scheduler
        _sch = get_scheduler_status()
        _sc1, _sc2 = st.columns(2)
        with _sc1:
            _run_time = st.time_input("Hora del análisis diario", value=None, key="cfg_sched_time")
        with _sc2:
            _sched_on = st.toggle("Activar scheduler", value=_sch["running"], key="cfg_sched_toggle")

        if _sched_on and not _sch["running"]:
            _rt_str = _run_time.strftime("%H:%M") if _run_time else "08:00"
            start_scheduler(_rt_str)
            st.success(f"✅ Scheduler activado — análisis diario a las {_rt_str}")
        elif not _sched_on and _sch["running"]:
            st.info("Reinicia el dashboard para detener el scheduler.")

        if _sch["log"]:
            st.markdown("**Últimas 5 ejecuciones:**")
            for _entry in _sch["log"][-5:]:
                _icon = "✅" if _entry.get("status") == "success" else "❌"
                st.caption(f'{_icon} {_entry.get("timestamp","")[:16]} — {_entry.get("status","")}')

        # ── SECCIÓN 5: Datos & Cache ──────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 💾 Datos & Cache")
        import os, glob, zipfile
        from io import BytesIO

        _cache_files = glob.glob("data/cache/*")
        _cache_size  = sum(os.path.getsize(f) for f in _cache_files if os.path.isfile(f))
        _prices_mtime = None
        _prices_path  = "data/cache/prices.csv"
        if os.path.exists(_prices_path):
            import datetime
            _prices_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(_prices_path)).strftime("%d/%m/%Y %H:%M")

        _dc1, _dc2, _dc3 = st.columns(3)
        _dc1.metric("Tamaño del cache", f"{_cache_size/1024:.1f} KB")
        _dc2.metric("Archivos en cache", str(len(_cache_files)))
        _dc3.metric("Precios actualizados", _prices_mtime or "N/A")

        _btn_c1, _btn_c2 = st.columns(2)
        if _btn_c1.button("🗑️ Limpiar cache JSON", key="cfg_clear_cache"):
            _cleared = 0
            for _cf in glob.glob("data/cache/*.json"):
                if "alerts" not in _cf:
                    os.remove(_cf); _cleared += 1
            st.success(f"✅ {_cleared} archivos JSON borrados (alerts conservado)")
            st.rerun()

        # Export ZIP
        _zip_buf = BytesIO()
        with zipfile.ZipFile(_zip_buf, "w", zipfile.ZIP_DEFLATED) as _zf:
            for _cf in glob.glob("data/cache/*"):
                if os.path.isfile(_cf):
                    _zf.write(_cf, os.path.basename(_cf))
            for _rf in glob.glob("reports/*.pdf"):
                if os.path.isfile(_rf):
                    _zf.write(_rf, f"reports/{os.path.basename(_rf)}")
        _zip_buf.seek(0)
        _btn_c2.download_button(
            "📦 Exportar datos (ZIP)",
            data=_zip_buf,
            file_name="portfolio_export.zip",
            mime="application/zip",
            key="cfg_export_zip",
        )

    except Exception as e:
        st.error(f"Error en tab Configuración: {e}")
