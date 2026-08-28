import streamlit as st
import requests

st.set_page_config(
    page_title="Painel Pro de Futebol",
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

@st.cache_data(ttl=15)
def fetch_espn_matches(slug):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            return res.json().get("events", [])
        return []
    except Exception:
        return []

@st.cache_data(ttl=15)
def fetch_match_summary(slug, event_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/summary?event={event_id}"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            return res.json()
        return {}
    except Exception:
        return {}

def extract_stats(summary_data):
    stats_dict = {"home": {}, "away": {}}
    boxscore = summary_data.get("boxscore", {})
    teams = boxscore.get("teams", [])
    
    for team_data in teams:
        side = "home" if team_data.get("homeAway") == "home" else "away"
        statistics = team_data.get("statistics", [])
        for stat in statistics:
            name = stat.get("name", "")
            val = stat.get("displayValue", "0")
            stats_dict[side][name] = val
            
    return stats_dict

def calculate_pressure(home_stats, away_stats):
    def parse_num(val):
        try:
            return float(str(val).replace("%", "").strip())
        except ValueError:
            return 0.0

    h_target = parse_num(home_stats.get("shotsOnTarget", 0))
    h_shots = parse_num(home_stats.get("totalShots", 0))
    h_corners = parse_num(home_stats.get("wonCorners", 0))
    h_poss = parse_num(home_stats.get("possessionPct", 50))

    a_target = parse_num(away_stats.get("shotsOnTarget", 0))
    a_shots = parse_num(away_stats.get("totalShots", 0))
    a_corners = parse_num(away_stats.get("wonCorners", 0))
    a_poss = parse_num(away_stats.get("possessionPct", 50))

    h_score = (h_target * 3.0) + (h_shots * 1.0) + (h_corners * 1.5) + (h_poss * 0.2)
    a_score = (a_target * 3.0) + (a_shots * 1.0) + (a_corners * 1.5) + (a_poss * 0.2)

    total = h_score + a_score
    if total == 0:
        return 50, 50
    
    h_pct = int(round((h_score / total) * 100))
    a_pct = 100 - h_pct
    return h_pct, a_pct

def get_custom_bar(percentage, side):
    if percentage >= 70:
        color = "#ef4444"  # Vermelho (Pressão Forte / Alta)
        label = "🔥 Pressão Alta"
    elif percentage >= 50:
        color = "#f97316"  # Laranja (Forte / Ativo)
        label = "⚡ Força Moderada"
    elif percentage >= 30:
        color = "#3b82f6"  # Azul (Neutro)
        label = "⚖️ Neutro"
    else:
        color = "#64748b"  # Cinza (Baixo)
        label = "🛡️ Defensivo"
        
    align = "right" if side == "home" else "left"
    
    return f"""
    <div style="text-align: {align}; margin-top: 6px;">
        <span style="font-size: 11px; color: #cbd5e1; font-weight: bold;">{label} ({percentage}%)</span>
        <div style="background-color: #334155; border-radius: 4px; width: 100%; height: 10px; overflow: hidden; margin-top: 3px;">
            <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    """

st.title("⚽ Painel de Futebol & Termômetro de Força")

search_query = st.text_input("🔍 Buscar time (ex: Al Nassr, Real Madrid, Flamengo...)", "").strip().lower()

matches_to_display = []

if search_query:
    st.subheader(f"🔎 Resultados da busca por: '{search_query}'")
    with st.spinner("Procurando nas ligas..."):
        for league_name, slug in LEAGUES.items():
            events = fetch_espn_matches(slug)
            for ev in events:
                name = ev.get("name", "").lower()
                if search_query in name:
                    matches_to_display.append((league_name, slug, ev))
else:
    st.sidebar.title("⚙️ Configurações")
    selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
    league_slug = LEAGUES[selected_league_name]
    st.markdown(f"Liga selecionada: **{selected_league_name}**")
    
    events = fetch_espn_matches(league_slug)
    for ev in events:
        matches_to_display.append((selected_league_name, league_slug, ev))

if not matches_to_display:
    st.info("Nenhuma partida encontrada.")
else:
    for league_name, slug, event in matches_to_display:
        event_id = event.get("id")
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        home_team, away_team = "Casa", "Fora"
        home_score, away_score = "0", "0"
        
        for comp in competitors:
            if comp.get("homeAway") == "home":
                home_team = comp.get("team", {}).get("displayName", "Casa")
                home_score = comp.get("score", "0")
            else:
                away_team = comp.get("team", {}).get("displayName", "Fora")
                away_score = comp.get("score", "0")
        
        status_type = competition.get("status", {}).get("type", {})
        state = status_type.get("state", "pre")
        detail = status_type.get("detail", "")
        
        # Buscar estatísticas prévias para calcular o termômetro individual em tempo real
        summary = fetch_match_summary(slug, event_id)
        stats = extract_stats(summary)
        h_press, a_press = calculate_pressure(stats["home"], stats["away"])

        if search_query:
            st.caption(f"🏆 Campeonato: **{league_name}**")

        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"<h3 style='text-align: right; color: #fff; margin-bottom: 0;'>{home_team}</h3>", unsafe_allow_html=True)
            st.markdown(get_custom_bar(h_press, "home"), unsafe_allow_html=True)
        with col2:
            if state == "in":
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#ff4b4b; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>AO VIVO ({detail})</span><h2 style='color:#fff; margin:4px 0;'>{home_score} x {away_score}</h2></div>", unsafe_allow_html=True)
            elif state == "post":
                st.markdown(f"<div style='text-align: center;'><span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span><h2 style='color:#fff; margin:4px 0;'>{home_score} x {away_score}</h2></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center;'><span style='background-color:#3b82f6; color:white; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;'>🕒 {detail}</span><h3 style='color:#94a3b8; margin:4px 0;'>vs</h3></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h3 style='text-align: left; color: #fff; margin-bottom: 0;'>{away_team}</h3>", unsafe_allow_html=True)
            st.markdown(get_custom_bar(a_press, "away"), unsafe_allow_html=True)

        # Botão Expansível apenas para as Estatísticas Detalhadas
        with st.expander(f"📊 Ver Estatísticas Detalhadas ({home_team} vs {away_team})"):
            h_stats, a_stats = stats["home"], stats["away"]
            
            m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
            
            poss_h = h_stats.get("possessionPct", "0%")
            poss_a = a_stats.get("possessionPct", "0%")
            shots_target_h = h_stats.get("shotsOnTarget", "0")
            shots_target_a = a_stats.get("shotsOnTarget", "0")
            shots_total_h = h_stats.get("totalShots", "0")
            shots_total_a = a_stats.get("totalShots", "0")
            corners_h = h_stats.get("wonCorners", "0")
            corners_a = a_stats.get("wonCorners", "0")
            
            with m_col1:
                st.markdown(f"<p style='text-align: right;'><b>{poss_h}</b><br>{shots_target_h}<br>{shots_total_h}<br>{corners_h}</p>", unsafe_allow_html=True)
            with m_col2:
                st.markdown("<p style='text-align: center; color: #94a3b8;'>Posse de Bola<br>Chutes no Gol<br>Chutes Totais<br>Escanteios</p>", unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"<p style='text-align: left;'><b>{poss_a}</b><br>{shots_target_a}<br>{shots_total_a}<br>{corners_a}</p>", unsafe_allow_html=True)

        st.divider()
