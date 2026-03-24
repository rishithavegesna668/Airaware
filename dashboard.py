import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import requests
import os
import sys

# Allow imports from parent folder (preprocessing, train_model, etc.)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from preprocessing import load_data, preprocess
from train_model import prepare_prophet_df, train, save_model
from predict import load_model, predict_aqi
from aqi_alerts import get_category, get_alert

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AirAware — Dashboard",
    page_icon="🌬️",
    layout="wide",
)

# ── Shared CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1100px; }

/* ── Top nav ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 1.2rem; border-bottom: 1px solid #f0f0ec; margin-bottom: 2rem;
}
.topbar-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem; font-weight: 400; color: #1a1a18;
}
.topbar-brand em { font-style: italic; color: #aaa; }

/* ── Section labels ── */
.sec-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em;
    color: #bbb; font-weight: 500; margin-bottom: 0.4rem;
}
.sec-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem; font-weight: 400; color: #1a1a18; margin-bottom: 0.2rem;
}
.sec-sub { font-size: 13px; color: #aaa; margin-bottom: 1.4rem; line-height: 1.5; }

/* ── White card ── */
.card {
    background: #fff; border: 1px solid #ebebeb;
    border-radius: 18px; padding: 1.5rem 1.8rem; margin-bottom: 1.4rem;
}

/* ── Stat cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 1.4rem; }
.stat-card {
    background: #fff; border: 1px solid #ebebeb;
    border-radius: 16px; padding: 1.2rem 1.4rem;
}
.stat-micro { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #bbb; margin-bottom: 6px; }
.stat-val {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem; font-weight: 400; line-height: 1;
}
.stat-badge {
    display: inline-block; margin-top: 8px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 500;
}
.stat-note { font-size: 12px; color: #aaa; margin-top: 6px; }

/* ── Scale bar ── */
.scale-labels {
    display: flex; justify-content: space-between;
    font-size: 10px; color: #ccc; margin-bottom: 5px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.scale-track {
    height: 8px; border-radius: 4px;
    background: linear-gradient(to right,#4caf50,#ffeb3b,#ff9800,#f44336,#9c27b0,#7b1fa2);
}
.scale-thumb-wrap { position: relative; height: 16px; }
.scale-thumb {
    position: absolute; top: -4px;
    width: 16px; height: 16px; border-radius: 50%;
    background: #fff; border: 2.5px solid #1a1a18;
    transform: translateX(-50%);
}

/* ── Poll grid (6 cols) ── */
.poll-grid-6 { display: grid; grid-template-columns: repeat(6,1fr); gap: 10px; }
.poll-cell { background: #f8f8f5; border-radius: 10px; padding: 10px 6px; text-align: center; }
.poll-val { font-size: 17px; font-weight: 500; color: #1a1a18; }
.poll-lbl { font-size: 10px; color: #bbb; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }

/* ── Health / alert box ── */
.health-box { border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.55; margin-top: 1rem; }

/* ── Compare grid ── */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 1.4rem; }
.compare-card {
    background: #fff; border: 1px solid #ebebeb;
    border-radius: 16px; padding: 1.2rem 1.4rem;
}
.compare-micro { font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: #bbb; margin-bottom: 8px; }
.compare-aqi {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem; font-weight: 400; line-height: 1;
}
.compare-cat { font-size: 12px; color: #888; margin-top: 4px; }
.compare-msg { font-size: 12px; color: #aaa; margin-top: 6px; line-height: 1.45; }

/* ── Data table ── */
.aqi-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.aqi-table th {
    text-align: left; font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.08em; color: #bbb; font-weight: 500;
    padding: 0 0 8px; border-bottom: 1px solid #f0f0ec;
}
.aqi-table td { padding: 9px 0; border-bottom: 1px solid #f8f8f5; color: #1a1a18; }
.aqi-table tr:last-child td { border-bottom: none; }
.aqi-table .aqi-pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 500;
}

/* ── Divider ── */
.soft-divider { border: none; border-top: 1px solid #f0f0ec; margin: 2rem 0; }

/* ── Warn ── */
.warn-box {
    background: #fffbe6; border: 1px solid #ffe58f;
    color: #8a6d00; border-radius: 10px;
    padding: 12px 14px; font-size: 13px; margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
API_TOKEN = "32c53cfc61cde08743a85391301436793640a986"
MODEL_PATH = "model.pkl"

LEVELS = [
    (50,           "Good",               "#4a7c59", "#e8f5e9"),
    (100,          "Moderate",           "#8a6d00", "#fffde7"),
    (150,          "Unhealthy for Some", "#b04e00", "#fff3e0"),
    (200,          "Unhealthy",          "#991f1f", "#fdecea"),
    (300,          "Very Unhealthy",     "#6a1b9a", "#f3e5f5"),
    (float("inf"), "Hazardous",          "#4a0000", "#fde8e8"),
]
HEALTH_MSGS = [
    (50,           "Air quality is satisfactory. Great day for outdoor activities."),
    (100,          "Acceptable quality. Sensitive people should limit prolonged outdoor exertion."),
    (150,          "Sensitive groups may experience effects. Reduce prolonged outdoor exertion."),
    (200,          "Everyone may begin to experience effects. Avoid prolonged outdoor exertion."),
    (300,          "Health alert — everyone may experience serious effects. Stay indoors."),
    (float("inf"), "Emergency conditions. Everyone should avoid all outdoor exertion."),
]
POLL_KEYS   = ["pm25", "pm10", "o3", "no2", "so2", "co"]
POLL_LABELS = {"pm25":"PM 2.5","pm10":"PM 10","o3":"Ozone","no2":"NO₂","so2":"SO₂","co":"CO"}


def get_level(aqi):
    for cap, label, color, bg in LEVELS:
        if aqi <= cap:
            return label, color, bg
    return LEVELS[-1][1], LEVELS[-1][2], LEVELS[-1][3]

def get_health(aqi):
    for cap, msg in HEALTH_MSGS:
        if aqi <= cap:
            return msg
    return HEALTH_MSGS[-1][1]

def thumb_pct(aqi):
    return min((aqi / 500) * 100, 97)

def fetch_aqi_full(city):
    try:
        r = requests.get(
            f"https://api.waqi.info/feed/{city.strip().lower()}/?token={API_TOKEN}",
            timeout=6,
        )
        d = r.json()
        if d["status"] == "ok":
            return d["data"], None
        return None, "City not found."
    except Exception as e:
        return None, str(e)


# ── Top nav ────────────────────────────────────────────────────────────────────
nav_l, nav_r = st.columns([3, 1])
with nav_l:
    st.markdown("""
    <div style="padding-bottom:1.2rem; border-bottom:1px solid #f0f0ec; margin-bottom:1.8rem;">
      <span style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#1a1a18;">
        AirAware <em style="font-style:italic;color:#aaa;">Smart</em>
      </span>
      <span style="font-size:12px; color:#bbb; margin-left:12px;">Full Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
with nav_r:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("home.py")

# ── City input ─────────────────────────────────────────────────────────────────
ci1, ci2 = st.columns([3, 1], gap="small")
with ci1:
    CITY = st.text_input("", value="hyderabad", placeholder="Enter city name…", label_visibility="collapsed")
with ci2:
    st.button("Fetch live AQI", use_container_width=True, type="primary")

if not CITY:
    st.info("Enter a city name above to begin.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — LIVE AQI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-label">Section 01</div>
<div class="sec-title">Live AQI Right Now</div>
<p class="sec-sub">Fetched in real-time from the WAQI global sensor network.</p>
""", unsafe_allow_html=True)

live_data, live_error = fetch_aqi_full(CITY)

if live_error:
    st.markdown(f'<div class="warn-box">⚠️ {live_error}</div>', unsafe_allow_html=True)
    live_aqi = None
else:
    live_aqi    = live_data["aqi"]
    station     = live_data["city"]["name"]
    updated     = live_data["time"]["s"]
    iaqi        = live_data.get("iaqi", {})
    live_cat    = get_category(live_aqi)
    live_alert  = get_alert(live_aqi)
    lvl_label, lvl_color, lvl_bg = get_level(live_aqi)
    health_msg  = get_health(live_aqi)
    thumb       = thumb_pct(live_aqi)

    # Stat cards row
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-micro">Air Quality Index</div>
        <div class="stat-val" style="color:{lvl_color};">{live_aqi}</div>
        <div class="stat-badge" style="background:{lvl_bg};color:{lvl_color};">{lvl_label}</div>
      </div>
      <div class="stat-card">
        <div class="stat-micro">Monitoring Station</div>
        <div style="font-size:1.1rem;font-weight:500;color:#1a1a18;margin-top:8px;">{station}</div>
        <div class="stat-note">Last updated {updated}</div>
      </div>
      <div class="stat-card">
        <div class="stat-micro">Health Category</div>
        <div style="font-size:1.1rem;font-weight:500;color:#1a1a18;margin-top:8px;">{live_cat}</div>
        <div class="stat-note">{live_alert}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Scale bar
    st.markdown(f"""
    <div class="card" style="padding:1.2rem 1.6rem;">
      <div class="sec-label" style="margin-bottom:0.6rem;">AQI Scale</div>
      <div class="scale-labels">
        <span>0 · Good</span><span>100 · Moderate</span>
        <span>200 · Unhealthy</span><span>300 · Very unhealthy</span><span>500 · Hazardous</span>
      </div>
      <div class="scale-track"></div>
      <div class="scale-thumb-wrap">
        <div class="scale-thumb" style="left:{thumb:.1f}%;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Pollutant grid
    poll_cells = ""
    for k in POLL_KEYS:
        val = round(iaqi[k]["v"]) if k in iaqi else "—"
        poll_cells += f"""
        <div class="poll-cell">
          <div class="poll-val">{val}</div>
          <div class="poll-lbl">{POLL_LABELS[k]}</div>
        </div>"""

    st.markdown(f"""
    <div class="card">
      <div class="sec-label" style="margin-bottom:0.8rem;">Pollutant Breakdown</div>
      <div class="poll-grid-6">{poll_cells}</div>
      <div class="health-box" style="background:{lvl_bg};color:{lvl_color};margin-top:1rem;">
        💡 {health_msg}
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — HISTORICAL DATA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-label">Section 02</div>
<div class="sec-title">Historical AQI Data</div>
<p class="sec-sub">Dataset used to train the prediction model — last 15 records shown.</p>
""", unsafe_allow_html=True)

df = load_data()
df = preprocess(df)

# Build styled HTML table
table_rows = ""
for _, row in df[["Date", "AQI"]].tail(15).iterrows():
    aqi_v   = int(row["AQI"])
    lbl, clr, bg_ = get_level(aqi_v)
    table_rows += f"""
    <tr>
      <td>{str(row['Date'])[:10]}</td>
      <td>{aqi_v}</td>
      <td><span class="aqi-pill" style="background:{bg_};color:{clr};">{lbl}</span></td>
    </tr>"""

st.markdown(f"""
<div class="card">
  <table class="aqi-table">
    <thead>
      <tr><th>Date</th><th>AQI</th><th>Category</th></tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — MODEL TRAINING (silent)
# ══════════════════════════════════════════════════════════════════════════════
if not os.path.exists(MODEL_PATH):
    with st.spinner("Training prediction model on historical data…"):
        prophet_df = prepare_prophet_df(df)
        model      = train(prophet_df)
        save_model(model, MODEL_PATH)
    st.success("Model trained and saved.")
else:
    model = load_model(MODEL_PATH)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — 7-DAY FORECAST
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-label">Section 03</div>
<div class="sec-title">7-Day AQI Forecast</div>
<p class="sec-sub">Predicted using a Facebook Prophet model trained on your historical dataset.</p>
""", unsafe_allow_html=True)

predictions = predict_aqi(model, days=7)

# ── Chart ──
fig, ax = plt.subplots(figsize=(11, 4))
fig.patch.set_facecolor("#ffffff")
ax.set_facecolor("#fafaf8")

ax.plot(df["Date"], df["AQI"],
        color="#a0b4c8", linewidth=1.2, label="Historical AQI", zorder=2)

ax.plot(predictions["Date"], predictions["Predicted_AQI"],
        color="#c05a3a", linewidth=2, linestyle="--",
        marker="o", markersize=5, markerfacecolor="#fff",
        markeredgewidth=1.5, label="Predicted AQI", zorder=3)

ax.fill_between(
    predictions["Date"],
    predictions["Lower_Bound"],
    predictions["Upper_Bound"],
    alpha=0.12, color="#c05a3a", label="Confidence range", zorder=1,
)

if live_aqi:
    ax.axhline(y=live_aqi, color="#4a7c59", linewidth=1.2,
               linestyle=":", label=f"Live today ({live_aqi})", zorder=4)

ax.set_xlabel("Date", fontsize=11, color="#aaa")
ax.set_ylabel("AQI", fontsize=11, color="#aaa")
ax.tick_params(colors="#aaa", labelsize=10)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#f0f0ec")
ax.spines["bottom"].set_color("#f0f0ec")
ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
ax.grid(axis="y", color="#f0f0ec", linewidth=0.8, zorder=0)
legend = ax.legend(fontsize=10, frameon=True, facecolor="#fff",
                   edgecolor="#ebebeb", labelcolor="#555")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()

st.pyplot(fig)

# ── Forecast table ──
table_rows2 = ""
for _, row in predictions.iterrows():
    aqi_v   = int(row["Predicted_AQI"])
    lbl, clr, bg_ = get_level(aqi_v)
    table_rows2 += f"""
    <tr>
      <td>{str(row['Date'])[:10]}</td>
      <td>{aqi_v}</td>
      <td>{int(row['Lower_Bound'])} – {int(row['Upper_Bound'])}</td>
      <td><span class="aqi-pill" style="background:{bg_};color:{clr};">{lbl}</span></td>
    </tr>"""

st.markdown(f"""
<div class="card" style="margin-top:1rem;">
  <div class="sec-label" style="margin-bottom:0.8rem;">Predicted values</div>
  <table class="aqi-table">
    <thead>
      <tr><th>Date</th><th>Predicted AQI</th><th>Range</th><th>Category</th></tr>
    </thead>
    <tbody>{table_rows2}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — TOMORROW'S ALERT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="sec-label">Section 04</div>
<div class="sec-title">Tomorrow's Health Alert</div>
<p class="sec-sub">Based on the model's prediction for the next 24 hours.</p>
""", unsafe_allow_html=True)

tomorrow_aqi = int(predictions["Predicted_AQI"].iloc[0])
t_label, t_color, t_bg = get_level(tomorrow_aqi)
t_health = get_health(tomorrow_aqi)
t_cat    = get_category(tomorrow_aqi)
t_alert  = get_alert(tomorrow_aqi)

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-micro">Predicted AQI Tomorrow</div>
    <div class="stat-val" style="color:{t_color};">{tomorrow_aqi}</div>
    <div class="stat-badge" style="background:{t_bg};color:{t_color};">{t_label}</div>
  </div>
  <div class="stat-card">
    <div class="stat-micro">Category</div>
    <div style="font-size:1.1rem;font-weight:500;color:#1a1a18;margin-top:8px;">{t_cat}</div>
  </div>
  <div class="stat-card">
    <div class="stat-micro">Confidence Range</div>
    <div style="font-size:1.1rem;font-weight:500;color:#1a1a18;margin-top:8px;">
      {int(predictions['Lower_Bound'].iloc[0])} – {int(predictions['Upper_Bound'].iloc[0])}
    </div>
  </div>
</div>
<div class="health-box" style="background:{t_bg};color:{t_color};">
  🚨 &nbsp;<strong>Alert:</strong> {t_alert}<br>
  <span style="opacity:0.85;">{t_health}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — LIVE vs PREDICTED COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
if live_aqi:
    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-label">Section 05</div>
    <div class="sec-title">Live vs Predicted</div>
    <p class="sec-sub">How today's real-time reading compares with tomorrow's forecast.</p>
    """, unsafe_allow_html=True)

    ll, lc, lb = get_level(live_aqi)

    st.markdown(f"""
    <div class="compare-grid">
      <div class="compare-card">
        <div class="compare-micro">📡 Right now — live API</div>
        <div class="compare-aqi" style="color:{lc};">{live_aqi}</div>
        <div class="compare-cat">
          <span style="background:{lb};color:{lc};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;">{ll}</span>
        </div>
        <div class="compare-msg">{get_health(live_aqi)}</div>
      </div>
      <div class="compare-card">
        <div class="compare-micro">🔮 Tomorrow — model prediction</div>
        <div class="compare-aqi" style="color:{t_color};">{tomorrow_aqi}</div>
        <div class="compare-cat">
          <span style="background:{t_bg};color:{t_color};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;">{t_label}</span>
        </div>
        <div class="compare-msg">{t_health}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Trend note
    diff = tomorrow_aqi - live_aqi
    trend_msg = (
        f"Air quality is expected to <strong>improve by {abs(diff)} points</strong> tomorrow."
        if diff < 0 else
        f"Air quality is expected to <strong>worsen by {diff} points</strong> tomorrow."
        if diff > 0 else
        "Air quality is expected to <strong>stay the same</strong> tomorrow."
    )
    trend_color = "#4a7c59" if diff < 0 else "#991f1f" if diff > 0 else "#555"
    trend_bg    = "#e8f5e9" if diff < 0 else "#fdecea" if diff > 0 else "#f5f5f0"
    st.markdown(f"""
    <div class="health-box" style="background:{trend_bg};color:{trend_color};">
      📊 &nbsp;{trend_msg}
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)
st.markdown("""
<p style="text-align:center;font-size:11px;color:#ccc;margin-top:1rem;">
  AirAware Smart — Mini Project &nbsp;·&nbsp; WAQI API &nbsp;·&nbsp; Facebook Prophet &nbsp;·&nbsp; Streamlit
</p>
""", unsafe_allow_html=True)