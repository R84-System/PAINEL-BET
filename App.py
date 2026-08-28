import streamlit as st
import requests

st.set_page_config(
    page_title="Painel Pro de Futebol",
    page_icon="⚽",
    layout="wide"
)

# CSS com a bolinha verde piscando mais devagar (2 segundos)
st.markdown("""
<style>
@keyframes blink {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(0.95); }
    100% { opacity: 1; transform: scale(1); }
}
.blinking-dot {
    height: 10px;
    width: 10px;
    background-color: #22c55e;
    border-radius: 50%;
    display: inline-block;
    animation: blink 2s infinite ease-in-out;
    margin-right: 6px;
    box-shadow: 0 0 8px #22c55e;
}
</style>
""", unsafe_allow_html=True)

LEAGUES = {
    "🔴 Todos os Jogos ao Vivo (Global)": "all_live",
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

@st.cache_data(ttl=10)
def fetch_espn_matches(slug):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            return res.json().get("events", [])
        return []
    except Exception:
        return []

@st.cache_data(ttl=10)
def fetch_match_summary(slug, event_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/summary?event={event_id}"
    try:
        res = requests.get(url, timeout=6)
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
        for stat in team_data.get("statistics", []):
            stats_dict[side][stat.get("name", "")] = stat.get("displayValue", "0")
    return stats_dict

def extract_red_cards(summary_data, home_team_id, away_team_id):
    home_players = []
    away_players = []
    details = summary_data.get("details", [])
    for item in details:
        text = str(item.get("type", {}).get("text", "")).lower()
        if "red card" in text or "cartão vermelho" in text:
            athlete = item.get("athlete", {})
            p_name = athlete.get("displayName", "Jogador")
            t_id = item.get("team", {}).get("id")
            if t_id == home_team_id:
                if p_name not in home_players:
                    home_players.append(p_name)
            else:
                if p_name not in away_players:
                    away_players.append(p_name)
    return home_players, away_players

def calculate_pressure(home_stats, away_stats):
    def parse_num(val):
        try:
            return float(str(val).replace("%", "").strip())
        except ValueError:
            return 0.0

    h_score = (parse_num(home_stats.get("shotsOnTarget", 0)) * 3.0) + \
              (parse_num(home_stats.get("totalShots", 0)) * 1.0) + \
              (parse_num(home_stats.get("wonCorners", 0)) * 1.5) + \
              (parse_num(home_stats.get("possessionPct", 50)) * 0.2)
              
    a_score = (parse_num(away_stats.get("shotsOnTarget", 0)) * 3.0) + \
              (parse_num(away_stats.get("totalShots", 0)) * 1.0) + \
              (parse_num(away_stats.get("wonCorners", 0)) * 1.5) + \
              (parse_num(away_stats.get("possessionPct", 50)) * 0.2)

    total = h_score + a_score
    if total == 0:
        return 50, 50
    
    h_pct = int(round((h_score / total) * 100))
    return h_pct, 100 - h_pct

def get_custom_bar(percentage, side):
    # Cores atualizadas: Alta = Verde, Neutro = Branco, Baixa/Defensiva = Vermelho
    if percentage >= 65:
        color, label = "#22c55e", "🔥 Pressão Alta"
    elif percentage >= 35:
        color, label = "#ffffff", "⚖️ Neutro"
    else:
        color, label = "#ef4444", "🛡️ Defensiva / Baixa"
        
    align = "right" if side == "home" else "left"
    
    return f"""
    <div style="text-align: {align}; margin-top: 6px;">
        <span style="font-size: 11px; color: {color}; font-weight: bold;">{label} ({percentage}%)</span>
        <div style="background-color: #334155; border-radius: 4px; width: 100%; height: 10px; overflow: hidden; margin-top: 3px;">
            <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    """

st.title("⚽ Painel Pro de Futebol ao Vivo")

st.sidebar.title("⚙️ Configurações")
selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
league_slug = LEAGUES[selected_league_name]

search_query = st.text_input("🔍 Buscar time (ex: Al Nassr, Real Madrid, Flamengo...)", "").strip().lower()

@st.fragment(run_every=10)
def render_live_panel(slug, league_name, query):
    matches_to_display = []
    
    if query:
        st.subheader(f"🔎 Resultados da busca por: '{query}'")
        for l_name, l_slug in LEAGUES.items():
            if l_slug == "all_live":
                continue
            for ev in fetch_espn_matches(l_slug):
                if query in ev.get("name", "").lower():
                    matches_to_display.append((l_name, l_slug, ev))
    elif slug == "all_live":
        st.markdown("### 🔴 Todos os Jogos Ao Vivo no Mundo")
        for l_name, l_slug in LEAGUES.items():
            if l_slug == "all_live":
                continue
            for ev in fetch_espn_matches(l_slug):
                comp = ev.get("competitions", [{}])[0]
                if comp.get("status", {}).get("type", {}).get("state") == "in":
                    matches_to_display.append((l_name, l_slug, ev))
    else:
        st.markdown(f"Liga selecionada: **{league_name}**")
        for ev in fetch_espn_matches(slug):
            matches_to_display.append((league_name, slug, ev))

    if not matches_to_display:
        st.info("Nenhuma partida encontrada no momento.")
        return

    for l_name, l_slug, event in matches_to_display:
        event_id = event.get("id")
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        home_team, away_team = "Casa", "Fora"
        home_score, away_score = "0", "0"
        home_team_id, away_team_id = "", ""
        
        for comp in competitors:
            if comp.get("homeAway") == "home":
                home_team = comp.get("team", {}).get("displayName", "Casa")
                home_team_id = comp.get("team", {}).get("id", "")
                home_score = comp.get("score", "0")
            else:
                away_team = comp.get("team", {}).get("displayName", "Fora")
                away_team_id = comp.get("team", {}).get("id", "")
                away_score = comp.get("score", "0")
        
        status_type = competition.get("status", {}).get("type", {})
        state = status_type.get("state", "pre")
        detail = status_type.get("detail", "")
        status_obj = competition.get("status", {})
        display_clock = status_obj.get("displayClock", "")
        period = status_obj.get("period", 1)
        
        summary = fetch_match_summary(l_slug, event_id)
        stats = extract_stats(summary)
        h_red_players, a_red_players = extract_red_cards(summary, home_team_id, away_team_id)
        
        h_press, a_press = calculate_pressure(stats["home"], stats["away"])

        if query or slug == "all_live":
            st.caption(f"🏆 Campeonato: **{l_name}**")

        h_red_badge = f"<div style='text-align: right; margin-bottom: 2px;'><span style='background-color: #ef4444; color: white; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>🟥 EXPULSO ({len(h_red_players)})</span></div>" if h_red_players else ""
        a_red_badge = f"<div style='text-align: left; margin-bottom: 2px;'><span style='background-color: #ef4444; color: white; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>🟥 EXPULSO ({len(a_red_players)})</span></div>" if a_red_players else ""

        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(h_red_badge, unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: right; color: #fff; margin-top: 0; margin-bottom: 0;'>{home_team}</h3>", unsafe_allow_html=True)
            st.markdown(get_custom_bar(h_press, "home"), unsafe_allow_html=True)
        
        with col2:
            if state == "in":
                if period == 1:
                    period_name = "1º Tempo"
                elif period == 2:
                    period_name = "2º Tempo"
                elif period in [3, 4]:
                    period_name = "Prorrogação"
                elif period >= 5 or "pen" in detail.lower() or "pênalt" in detail.lower():
                    period_name = "Pênaltis"
                else:
                    period_name = f"Tempo {period}"
                
                clock_display = f" ({display_clock})" if display_clock else f" ({detail})"
                st.markdown(f"""
                <div style='text-align: center;'>
                    <span style='background-color:#1e293b; color:white; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:bold; border: 1px solid #334155;'>
                        <span class="blinking-dot"></span>AO VIVO • {period_name}{clock_display}
                    </span>
                    <h2 style='color:#fff; margin:6px 0;'>{home_score} x {away_score}</h2>
                </div>
                """, unsafe_allow_html=True)
            elif state == "post":
                st.markdown(f"""
                <div style='text-align: center;'>
                    <span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span>
                    <h2 style='color:#fff; margin:6px 0;'>{home_score} x {away_score}</h2>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <span style='background-color:#3b82f6; color:white; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:bold;'>🕒 {detail}</span>
                    <h3 style='color:#94a3b8; margin:6px 0;'>vs</h3>
                </div>
                """, unsafe_allow_html=True)
                
        with col3:
            st.markdown(a_red_badge, unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: left; color: #fff; margin-top: 0; margin-bottom: 0;'>{away_team}</h3>", unsafe_allow_html=True)
            st.markdown(get_custom_bar(a_press, "away"), unsafe_allow_html=True)

        with st.expander(f"📊 Ver Estatísticas Detalhadas ({home_team} vs {away_team})"):
            h_stats, a_stats = stats["home"], stats["away"]
            
            poss_h = h_stats.get("possessionPct", "0")
            if not poss_h.endswith("%"):
                poss_h = f"{poss_h}%" if poss_h != "0" else "0%"
            poss_a = a_stats.get("possessionPct", "0")
            if not poss_a.endswith("%"):
                poss_a = f"{poss_a}%" if poss_a != "0" else "0%"

            fouls_h = h_stats.get("foulsCommitted", h_stats.get("fouls", "0"))
            fouls_a = a_stats.get("foulsCommitted", a_stats.get("fouls", "0"))
            
            yellow_h = h_stats.get("yellowCards", "0")
            yellow_a = a_stats.get("yellowCards", "0")
            red_h_count = h_stats.get("redCards", str(len(h_red_players)))
            red_a_count = h_stats.get("redCards", str(len(a_red_players)))

            cards_h_str = f"🟨 {yellow_h} | 🟥 {red_h_count}"
            cards_a_str = f"🟨 {yellow_a} | 🟥 {red_a_count}"

            if h_red_players:
                cards_h_str += f"<br><span style='font-size:10px; color:#ef4444;'>Expulso(s): {', '.join(h_red_players)}</span>"
            if a_red_players:
                cards_a_str += f"<br><span style='font-size:10px; color:#ef4444;'>Expulso(s): {', '.join(a_red_players)}</span>"

            m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
            with m_col1:
                st.markdown(f"""
                <p style='text-align: right;'>
                    <b>{poss_h}</b><br>
                    {h_stats.get('shotsOnTarget', '0')}<br>
                    {h_stats.get('totalShots', '0')}<br>
                    {h_stats.get('wonCorners', '0')}<br>
                    {fouls_h}<br>
                    {cards_h_str}
                </p>
                """, unsafe_allow_html=True)
            with m_col2:
                st.markdown("""
                <p style='text-align: center; color: #94a3b8;'>
                    Posse de Bola<br>
                    Chutes no Gol<br>
                    Chutes Totais<br>
                    Escanteios<br>
                    Faltas Cometidas<br>
                    Cartões (Amarelos | Vermelhos)
                </p>
                """, unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"""
                <p style='text-align: left;'>
                    <b>{poss_a}</b><br>
                    {a_stats.get('shotsOnTarget', '0')}<br>
                    {a_stats.get('totalShots', '0')}<br>
                    {a_stats.get('wonCorners', '0')}<br>
                    {fouls_a}<br>
                    {cards_a_str}
                </p>
                """, unsafe_allow_html=True)

        st.divider()

render_live_panel(league_slug, selected_league_name, search_query)
