import streamlit as st
import requests

st.set_page_config(
    page_title="Painel de Futebol - ESPN",
    page_icon="⚽",
    layout="wide"
)

LEAGUES = {
    "🇧🇷 Brasileirão Série A": "bra.1",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "eng.1",
    "🇪🇸 La Liga": "esp.1",
    "🇮🇹 Serie A (Itália)": "ita.1",
    "🇩🇪 Bundesliga": "ger.1",
    "🇫🇷 Ligue 1": "fra.1",
    "🇵🇹 Primeira Liga": "por.1",
    "🇸🇦 Saudi Pro League": "ksa.1",
    "🇦🇷 Liga Profesional (Argentina)": "arg.1",
    "🇳🇱 Eredivisie": "ned.1",
    "🇺🇸 MLS": "usa.1",
    "🇪🇺 Champions League": "uefa.champions",
    "🌎 Copa Libertadores": "conmebol.libertadores"
}

st.sidebar.title("⚙️ Configurações")
selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
league_slug = LEAGUES[selected_league_name]

st.title("⚽ Painel de Futebol - ESPN API")
st.markdown(f"Liga selecionada: **{selected_league_name}**")

@st.cache_data(ttl=15)
def fetch_espn_matches(slug):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("events", [])
        return []
    except Exception:
        return []

events = fetch_espn_matches(league_slug)

if not events:
    st.info("Nenhuma partida encontrada para hoje nesta liga.")
else:
    st.success(f"{len(events)} partida(s) encontrada(s)!")
    
    for event in events:
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        home_team, away_team, home_score, away_score = "Casa", "Fora", "0", "0"
        for comp in competitors:
            if comp.get("homeAway") == "home":
                home_team = comp.get("team", {}).get("displayName", "Casa")
                home_score = comp.get("score", "0")
            else:
                away_team = comp.get("team", {}).get("displayName", "Fora")
                away_score = comp.get("score", "0")
        
        status_type = competition.get("status", {}).get("type", {})
        state = status_type.get("state", "pre") # pre, in, post
        detail = status_type.get("detail", "")
        
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"<h3 style='text-align: right; color: #fff;'>{home_team}</h3>", unsafe_allow_html=True)
        with col2:
            if state == "in":
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#ff4b4b; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>AO VIVO ({detail})</span><h2 style='color:#fff; margin:4px 0;'>{home_score} x {away_score}</h2></div>", unsafe_allow_html=True)
            elif state == "post":
                st.markdown(f"<div style='text-align: center;'><span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span><h2 style='color:#fff; margin:4px 0;'>{home_score} x {away_score}</h2></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#3b82f6; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>🕒 {detail}</span><h3 style='color:#94a3b8; margin:4px 0;'>vs</h3></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h3 style='text-align: left; color: #fff;'>{away_team}</h3>", unsafe_allow_html=True)
        st.divider()
