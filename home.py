import streamlit as st
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AirAware Smart",
    page_icon="🌬️",
    layout="centered",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 620px; }

/* ── Hero ── */
.logo-circle {
    width: 68px; height: 68px; border-radius: 50%;
    background: #f5f5f0; border: 1px solid #e0ddd5;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px; margin: 0 auto 1.2rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem; font-weight: 400;
    color: #1a1a18; line-height: 1.15; margin-bottom: 0.4rem;
    text-align: center;
}
.hero-title em { font-style: italic; color: #aaa; }
.hero-sub {
    font-size: 15px; color: #999; font-weight: 300;
    max-width: 380px; margin: 0 auto 1.6rem; line-height: 1.65;
    text-align: center;
}

/* ── AQI card ── */
.aqi-card {
    background: #fff; border: 1px solid #ebebeb;
    border-radius: 20px; padding: 1.8rem 2rem; margin-top: 1.2rem;
}
.aqi-top {
    display: flex; justify-content: space-between;
    align-items: flex-start; margin-bottom: 1.4rem;
}
.aqi-micro-label {
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.09em;
    color: #bbb; margin-bottom: 4px; font-weight: 500;
}
.aqi-number {
    font-family: 'DM Serif Display', serif;
    font-size: 5rem; line-height: 1; font-weight: 400;
}
.aqi-badge {
    display: inline-block; margin-top: 8px;
    padding: 5px 14px; border-radius: 20px;
    font-size: 13px; font-weight: 500;
}
.aqi-right { text-align: right; }
.station-name { font-size: 14px; font-weight: 500; color: #1a1a18; margin-bottom: 3px; }
.station-time { font-size: 12px; color: #bbb; }

/* ── Scale bar ── */
.scale-wrap { margin: 0 0 1.4rem; }
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

/* ── Poll grid ── */
.poll-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1.4rem; }
.poll-cell { background: #f8f8f5; border-radius: 10px; padding: 10px 6px; text-align: center; }
.poll-val { font-size: 18px; font-weight: 500; color: #1a1a18; }
.poll-lbl { font-size: 10px; color: #bbb; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }

/* ── Health box ── */
.health-box { border-radius: 10px; padding: 12px 14px; font-size: 13px; line-height: 1.55; }

/* ── Feature cards ── */
.feat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-top: 2rem; }
.feat-card {
    background: #fff; border: 1px solid #ebebeb;
    border-radius: 14px; padding: 1rem;
}
.feat-icon { font-size: 20px; margin-bottom: 8px; }
.feat-title { font-size: 13px; font-weight: 500; color: #1a1a18; margin-bottom: 3px; }
.feat-desc { font-size: 11px; color: #bbb; line-height: 1.45; }

/* ── Divider ── */
.soft-divider { border: none; border-top: 1px solid #f0f0ec; margin: 2rem 0; }

/* ── Warn box ── */
.warn-box {
    background: #fffbe6; border: 1px solid #ffe58f;
    color: #8a6d00; border-radius: 10px;
    padding: 12px 14px; font-size: 13px; margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
API_TOKEN = "32c53cfc61cde08743a85391301436793640a986"

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

def fetch_aqi(city):
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


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:0.5rem 0 1rem;">
  <div class="logo-circle">🌬</div>
  <div class="hero-title">AirAware <em>Smart</em></div>
  <p class="hero-sub">Know the air you breathe — live AQI, pollutant breakdown, and health guidance for any city.</p>
</div>
""", unsafe_allow_html=True)

# ── City input + Check button ──────────────────────────────────────────────────
c1, c2 = st.columns([3, 1], gap="small")
with c1:
    city = st.text_input("", value="hyderabad", placeholder="Enter city…", label_visibility="collapsed")
with c2:
    check = st.button("Check air", use_container_width=True, type="primary")

# ── Open Dashboard button (uses st.switch_page for Streamlit multipage) ────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("➜  Open Full Dashboard", use_container_width=True):
    st.switch_page("pages/dashboard.py")

# ── Fetch & Render AQI card ────────────────────────────────────────────────────
data, error = (None, None)
if city:
    data, error = fetch_aqi(city)

if error:
    st.markdown(f'<div class="warn-box">⚠️ {error} — try a different city name.</div>',
                unsafe_allow_html=True)

elif data:
    aqi     = data["aqi"]
    station = data["city"]["name"]
    updated = data["time"]["s"]
    iaqi    = data.get("iaqi", {})

    label, color, bg = get_level(aqi)
    health_msg       = get_health(aqi)
    thumb            = min((aqi / 500) * 100, 97)

    poll_cells = ""
    for k in POLL_KEYS:
        val = round(iaqi[k]["v"]) if k in iaqi else "—"
        poll_cells += f"""
        <div class="poll-cell">
          <div class="poll-val">{val}</div>
          <div class="poll-lbl">{POLL_LABELS[k]}</div>
        </div>"""

    st.markdown(f"""
    <div class="aqi-card">
      <div class="aqi-top">
        <div>
          <div class="aqi-micro-label">Air Quality Index</div>
          <div class="aqi-number" style="color:{color};">{aqi}</div>
          <div class="aqi-badge" style="background:{bg};color:{color};">{label}</div>
        </div>
        <div class="aqi-right">
          <div class="station-name">{station}</div>
          <div class="station-time">Updated {updated}</div>
        </div>
      </div>

      <div class="scale-wrap">
        <div class="scale-labels">
          <span>Good</span><span>Moderate</span><span>Unhealthy</span><span>Hazardous</span>
        </div>
        <div class="scale-track"></div>
        <div class="scale-thumb-wrap">
          <div class="scale-thumb" style="left:{thumb:.1f}%;"></div>
        </div>
      </div>

      <div style="margin-top:1.2rem;">
        <div class="aqi-micro-label" style="margin-bottom:10px;">Pollutants</div>
        <div class="poll-grid">{poll_cells}</div>
      </div>

      <div class="health-box" style="background:{bg};color:{color};">
        💡 {health_msg}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Divider ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

# ── Feature cards ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="feat-grid">
  <div class="feat-card">
    <div class="feat-icon">📈</div>
    <div class="feat-title">7-day forecast</div>
    <div class="feat-desc">Prophet model trained on historical AQI data</div>
  </div>
  <div class="feat-card">
    <div class="feat-icon">🫁</div>
    <div class="feat-title">Health alerts</div>
    <div class="feat-desc">Personalised guidance based on tomorrow's predicted AQI</div>
  </div>
  <div class="feat-card">
    <div class="feat-icon">📡</div>
    <div class="feat-title">Live vs predicted</div>
    <div class="feat-desc">Side-by-side comparison of real-time and forecast values</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<p style="text-align:center;font-size:11px;color:#ccc;margin-top:2.5rem;">
  AirAware Smart — Mini Project &nbsp;·&nbsp; WAQI API &nbsp;·&nbsp; Prophet &nbsp;·&nbsp; Streamlit
</p>
""", unsafe_allow_html=True)
