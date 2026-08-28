import streamlit as st
from datetime import datetime, timezone
import requests

st.set_page_config(
    page_title="Painel Inteligente de Partidas",
    page_icon="⚽",
    layout="wide"
)

API_KEY = "c6c045752fef0a0759a2447ec070dbdd064f9a61d55c52fd1d59a052612f1da0"
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

LEAGUES = {
    "🇧🇷 Brasileirão Série A": 71,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": 39,
    "🇪🇸 La Liga": 140,
    "🇮🇹 Serie A (Itália)": 135,
    "🇩🇪 Bundesliga": 78,
    "🇫🇷 Ligue 1": 61,
    "🇵🇹 Primeira Liga": 94,
    "🇪🇺 Champions League": 2,
}

st.sidebar.title("⚙️ Configurações")
selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
league_id = LEAGUES[selected_league_name]

st.title("⚽ Painel Inteligente de Partidas")
st.markdown(f"Liga selecionada: **{selected_league_name}**")

def get_season(lid):
    now = datetime.now()
    year = now.year
    if lid in [71, 128, 253]:
        return year
    return year if now.month >= 7 else year - 1

@st.cache_data(ttl=30)
def fetch_fixtures(lid):
    season = get_season(lid)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/fixtures?league={lid}&season={season}&date={today}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                return data
        
        # Fallback para jogos ao vivo gerais se não achar na data exata
        url_live = f"{BASE_URL}/fixtures?live=all"
        res_live = requests.get(url_live, headers=HEADERS, timeout=10)
        if res_live.status_code == 200:
            all_live = res_live.json().get("response", [])
            league_live = [m for m in all_live if m.get("league", {}).get("id") == lid]
            if league_live:
                return league_live
        return []
    except:
        return []

matches = fetch_fixtures(league_id)

if not matches:
    st.info("Nenhuma partida encontrada para hoje ou ao vivo nesta liga.")
else:
    for m in matches:
        fixture = m.get("fixture", {})
        teams = m.get("teams", {})
        goals = m.get("goals", {})
        
        home = teams.get("home", {}).get("name", "Casa")
        away = teams.get("away", {}).get("name", "Fora")
        h_goals = goals.get("home") if goals.get("home") is not None else 0
        a_goals = goals.get("away") if goals.get("away") is not None else 0
        status = fixture.get("status", {}).get("short", "NS")
        elapsed = fixture.get("status", {}).get("elapsed", "")
        
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"<h3 style='text-align: right; color: #fff;'>{home}</h3>", unsafe_allow_html=True)
        with col2:
            if status in ["1H", "2H", "ET", "P"]:
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#ff4b4b; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>AO VIVO ({elapsed}')</span><h2 style='color:#fff; margin:4px 0;'>{h_goals} x {a_goals}</h2></div>", unsafe_allow_html=True)
            elif status == "FT":
                st.markdown(f"<div style='text-align: center;'><span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span><h2 style='color:#fff; margin:4px 0;'>{h_goals} x {a_goals}</h2></div>", unsafe_allow_html=True)
            else:
                date_iso = fixture.get("date", "")
                time_str = "Em breve"
                if date_iso:
                    try:
                        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
                        time_str = dt.strftime("%H:%M (UTC)")
                    except:
                        pass
                st.markdown(f"<div style='text-align: center;'><span style='color:#3b82f6; font-weight:bold;'>{time_str}</span><h3 style='color:#94a3b8; margin:4px 0;'>vs</h3></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h3 style='text-align: left; color: #fff;'>{away}</h3>", unsafe_allow_html=True)
        st.divider()
