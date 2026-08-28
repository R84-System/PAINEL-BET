import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Painel de Futebol - APIFootball.com",
    page_icon="⚽",
    layout="wide"
)

API_KEY = "c6c045752fef0a0759a2447ec070dbdd064f9a61d55c52fd1d59a052612f1da0"
BASE_URL = "https://apifootball.com/api/"

LEAGUES = {
    "🇧🇷 Brasileirão Série A": "271",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "152",
    "🇪🇸 La Liga": "302",
    "🇮🇹 Serie A (Itália)": "207",
    "🇩🇪 Bundesliga": "175",
    "🇫🇷 Ligue 1": "168",
    "🇵🇹 Primeira Liga": "332",
    "🇸🇦 Saudi Pro League": "468",
    "🇦🇷 Liga Profesional (Argentina)": "37",
    "🇳🇱 Eredivisie": "116",
    "🇺🇸 MLS": "338",
    "🇪🇺 Champions League": "4",
    "🌎 Copa Libertadores": "15"
}

st.sidebar.title("⚙️ Configurações")
selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
league_id = LEAGUES[selected_league_name]

st.title("⚽ Painel de Futebol - APIFootball.com")
st.markdown(f"Liga selecionada: **{selected_league_name}**")

@st.cache_data(ttl=30)
def fetch_events(lid):
    today = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "action": "get_events",
        "from": today,
        "to": today,
        "league_id": lid,
        "APIkey": API_KEY
    }
    try:
        # Timeout aumentado para 25 segundos para evitar quedas por lentidão do servidor
        res = requests.get(BASE_URL, params=params, timeout=25)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data, None
            elif isinstance(data, dict):
                return [], data.get("error", "Erro desconhecido na API")
        return [], f"Erro HTTP {res.status_code}"
    except requests.exceptions.Timeout:
        return [], "O servidor demorou muito para responder (Timeout). Tente atualizar a página."
    except Exception as e:
        return [], str(e)

matches, api_error = fetch_events(league_id)

if api_error:
    st.error(f"⚠️ {api_error}")

if not matches and not api_error:
    st.info("Nenhuma partida programada para hoje nesta liga.")
elif matches:
    st.success(f"{len(matches)} partida(s) encontrada(s) para hoje!")
    
    for m in matches:
        home = m.get("match_hometeam_name", "Casa")
        away = m.get("match_awayteam_name", "Fora")
        h_goals = m.get("match_hometeam_score", "0")
        a_goals = m.get("match_awayteam_score", "0")
        status = m.get("match_status", "")
        time_match = m.get("match_time", "")
        
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"<h3 style='text-align: right; color: #fff;'>{home}</h3>", unsafe_allow_html=True)
        with col2:
            if status in ["1H", "2H", "HT", "ET", "P"]:
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#ff4b4b; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>AO VIVO ({status})</span><h2 style='color:#fff; margin:4px 0;'>{h_goals} x {a_goals}</h2></div>", unsafe_allow_html=True)
            elif status in ["FT", "Finished"]:
                st.markdown(f"<div style='text-align: center;'><span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span><h2 style='color:#fff; margin:4px 0;'>{h_goals} x {a_goals}</h2></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#3b82f6; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>🕒 {time_match}</span><h3 style='color:#94a3b8; margin:4px 0;'>vs</h3></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h3 style='text-align: left; color: #fff;'>{away}</h3>", unsafe_allow_html=True)
        st.divider()
