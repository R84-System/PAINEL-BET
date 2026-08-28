"""
Painel Inteligente de Futebol para Transmissões ao Vivo
Versão com Inserção de Chave via Painel Lateral
"""

import streamlit as st
from datetime import datetime, timezone, timedelta
import requests

# =====================================================================
# BLOCO 1: CONFIGURAÇÕES E MAPA GLOBAL DE LIGAS (PRIMEIRAS DIVISÕES)
# =====================================================================

LEAGUES = {
    "🇮🇹 Serie A (Itália)": 135,
    "🇧🇷 Brasileirão Série A": 71,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)": 39,
    "🇪🇸 La Liga (Espanha)": 140,
    "🇩🇪 Bundesliga (Alemanha)": 78,
    "🇫🇷 Ligue 1 (França)": 61,
    "🇵🇹 Primeira Liga (Portugal)": 94,
    "🇳🇱 Eredivisie (Holanda)": 88,
    "🇦🇷 Liga Profesional (Argentina)": 128,
    "🇺🇸 MLS (Estados Unidos)": 253,
    "🇸🇦 Saudi Pro League (Arábia Saudita)": 307,
    "🌎 Copa Libertadores": 13,
    "🇪🇺 Champions League": 2,
}

UI_THEME = {
    "bg_color": "#090d16",
    "card_bg": "#121726",
    "border_color": "#1e2538",
    "accent_live": "#ff3b3b",
    "accent_timer": "#00ffcc",
}

# =====================================================================
# BLOCO 2: CLIENTE DE API COM SUPORTE A CHAVE DINÂMICA
# =====================================================================

class FootballAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key
        }

    def _get_active_season(self, league_id: int) -> int:
        now = datetime.now()
        year = now.year
        if league_id in [71, 128, 253]:
            return year
        if now.month < 7:
            return year - 1
        return year

    def get_fixtures_by_date(self, league_id: int, date_str: str) -> tuple:
        if not self.api_key:
            return [], "Chave da API não informada."
        
        season = self._get_active_season(league_id)
        try:
            url = f"{self.base_url}/fixtures?league={league_id}&season={season}&date={date_str}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data and data["errors"]:
                    return [], str(data["errors"])
                return data.get("response", []), None
            elif response.status_code == 403:
                return [], "Erro 403: Chave de API inválida."
            else:
                return [], f"Erro HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return [], f"Erro de conexão: {str(e)}"

    def get_fixture_statistics(self, fixture_id: int) -> list:
        if not self.api_key:
            return []
        try:
            url = f"{self.base_url}/fixtures/statistics?fixture={fixture_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", [])
            return []
        except requests.exceptions.RequestException:
            return []

# =====================================================================
# BLOCO 3: MOTOR ANALÍTICO E CRONÔMETRO DIGITAL
# =====================================================================

class MatchAnalyticsEngine:
    @staticmethod
    def calculate_thermometer(stats_data: list) -> dict:
        if not stats_data or len(stats_data) < 2:
            return {"home_pct": 50, "away_pct": 50, "status": "Equilibrado ⚖️", "trend": "Estudo em campo"}
        
        try:
            home_stats = {s["type"]: s["value"] for s in stats_data[0].get("statistics", [])}
            away_stats = {s["type"]: s["value"] for s in stats_data[1].get("statistics", [])}
            
            def parse_metric(val):
                if not val: return 0
                if isinstance(val, str) and "%" in val:
                    return int(val.replace("%", ""))
                try:
                    return int(val)
                except ValueError:
                    return 0

            home_score = parse_metric(home_stats.get("Shots on Goal", 0)) * 3 + parse_metric(home_stats.get("Total Shots", 0))
            away_score = parse_metric(away_stats.get("Shots on Goal", 0)) * 3 + parse_metric(away_stats.get("Total Shots", 0))
            
            total = home_score + away_score
            if total == 0:
                return {"home_pct": 50, "away_pct": 50, "status": "Equilibrado ⚖️", "trend": "Sem finalizações"}
            
            home_pct = int((home_score / total) * 100)
            away_pct = 100 - home_pct
            
            if home_pct > 65:
                status = "Pressão Forte 🔴"
                trend = f"{stats_data[0]['team']['name']} sufocando"
            elif away_pct > 65:
                status = "Pressão Forte 🔵"
                trend = f"{stats_data[1]['team']['name']} sufocando"
            else:
                status = "Lado a Lado ⚖️"
                trend = "Jogo Aberto"
                
            return {"home_pct": home_pct, "away_pct": away_pct, "status": status, "trend": trend}
        except Exception:
            return {"home_pct": 50, "away_pct": 50, "status": "Equilibrado ⚖️", "trend": "Indisponível"}

    @staticmethod
    def get_match_timer_info(match_date_str: str) -> tuple:
        try:
            match_time = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
            local_time_str = match_time.astimezone().strftime("%H:%M")
            
            now = datetime.now(timezone.utc)
            diff = match_time - now
            total_seconds = int(diff.total_seconds())
            
            if total_seconds <= 0:
                return "EM BREVE", local_time_str
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            timer_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return timer_str, local_time_str
        except Exception:
            return "--:--:--", "00:00"

# =====================================================================
# BLOCO 4: DESIGN DE INTERFACE E ESTILOS VISUAIS
# =====================================================================

def configure_page_styles():
    st.set_page_config(
        page_title="Painel de Partidas - Live",
        page_icon="⚽",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {UI_THEME['bg_color']}; }}
        .match-card {{
            background-color: {UI_THEME['card_bg']};
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            border: 1px solid {UI_THEME['border_color']};
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }}
        .live-badge {{
            background-color: {UI_THEME['accent_live']};
            color: white; padding: 3px 8px; border-radius: 4px;
            font-size: 10px; font-weight: 800; letter-spacing: 0.5px;
        }}
        .timer-digital {{
            font-family: monospace;
            font-size: 20px;
            font-weight: bold;
            color: {UI_THEME['accent_timer']};
            letter-spacing: 1px;
            margin: 0;
        }}
        .time-label {{
            font-size: 11px;
            color: #8b9bb4;
            margin-top: -2px;
        }}
        .thermometer-box {{
            margin-top: 10px; background-color: #0b0f19;
            padding: 8px 12px; border-radius: 8px; border: 1px solid #1a2236;
        }}
        .progress-bar-bg {{
            background-color: #1e2538; border-radius: 4px;
            overflow: hidden; height: 8px; display: flex; width: 100%;
            margin-top: 5px; margin-bottom: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_admin():
    with st.sidebar:
        st.markdown("### ⚙️ Painel ADM & Configuração")
        st.divider()
        
        # Tenta pegar dos secrets do Streamlit, senão permite digitar aqui
        default_key = ""
        try:
            default_key = st.secrets.get("API_FOOTBALL_KEY", "")
        except Exception:
            pass

        api_key_input = st.text_input("Chave da API-Football", value=default_key, type="password")
        st.session_state.api_key = api_key_input

        st.divider()
        selected_name = st.selectbox("Campeonato Mundial", options=list(LEAGUES.keys()))
        st.session_state.selected_league = LEAGUES[selected_name]
        
        st.divider()
        if st.button("🔄 Limpar Cache / Recarregar"):
            st.cache_data.clear()
            st.rerun()

# =====================================================================
# BLOCO 5: CONTROLADOR PRINCIPAL DA APLICAÇÃO
# =====================================================================

configure_page_styles()

if "selected_league" not in st.session_state:
    st.session_state.selected_league = list(LEAGUES.values())[0]

render_sidebar_admin()

api_key = st.session_state.get("api_key", "")
api_client = FootballAPIClient(api_key)
analytics = MatchAnalyticsEngine()

st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 20px;'>⚽ Painel de Transmissão</h2>", unsafe_allow_html=True)

if not api_key:
    st.warning("⚠️ Insira a sua chave da API-Football no painel lateral à esquerda para carregar os jogos.")
    st.stop()

@st.fragment(run_every="1s")
def render_live_dashboard():
    league_id = st.session_state.selected_league
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    matches, error_msg = api_client.get_fixtures_by_date(league_id, today_str)
    
    if error_msg:
        st.error(f"⚠️ Erro ao consultar API: {error_msg}")
        return

    if not matches:
        yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_str = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
        m_yes, _ = api_client.get_fixtures_by_date(league_id, yesterday_str)
        m_tom, _ = api_client.get_fixtures_by_date(league_id, tomorrow_str)
        matches = m_yes + m_tom

    if not matches:
        st.info("Nenhuma partida agendada para hoje nesta liga.")
        return

    for match in matches:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})
        
        fixture_id = fixture.get("id")
        status_short = fixture.get("status", {}).get("short", "NS")
        elapsed = fixture.get("status", {}).get("elapsed", 0)
        extra = fixture.get("status", {}).get("extra")
        match_date = fixture.get("date", "")
        
        home_team = teams.get("home", {}).get("name", "Casa")
        away_team = teams.get("away", {}).get("name", "Fora")
        home_logo = teams.get("home", {}).get("logo", "")
        away_logo = teams.get("away", {}).get("logo", "")
        
        home_goals = goals.get("home") if goals.get("home"] is not None else 0
        away_goals = goals.get("away") if goals.get("away") is not None else 0
        
        with st.container():
            st.markdown("<div class='match-card'>", unsafe_allow_html=True)
            
            col_home, col_center, col_away = st.columns([3, 3, 3])
            
            with col_home:
                c_logo, c_name = st.columns([1, 2])
                with c_logo:
                    if home_logo:
                        st.image(home_logo, width=32)
                with c_name:
                    st.markdown(f"<div style='color: white; font-weight: 700; font-size: 13px; line-height: 1.2;'>{home_team}</div>", unsafe_allow_html=True)
            
            with col_center:
                if status_short in ["1H", "2H", "ET"]:
                    time_str = f"{elapsed}'" + (f"+{extra}'" if extra else "")
                    st.markdown(f"<div style='text-align: center;'><span class='live-badge'>AO VIVO {time_str}</span><div style='color: white; font-weight: bold; font-size: 18px; margin-top: 2px;'>{home_goals} x {away_goals}</div></div>", unsafe_allow_html=True)
                elif status_short == "NS":
                    timer_str, local_time = analytics.get_match_timer_info(match_date)
                    st.markdown(f"<div style='text-align: center;'><p class='timer-digital'>{timer_str}</p><p class='time-label'>{local_time}</p></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center;'><span style='color: #8b9bb4; font-size: 11px; font-weight: bold;'>ENCERRADO</span><div style='color: white; font-weight: bold; font-size: 16px;'>{home_goals} x {away_goals}</div></div>", unsafe_allow_html=True)
            
            with col_away:
                c_name, c_logo = st.columns([2, 1])
                with c_name:
                    st.markdown(f"<div style='text-align: right; color: white; font-weight: 700; font-size: 13px; line-height: 1.2;'>{away_team}</div>", unsafe_allow_html=True)
                with c_logo:
                    if away_logo:
                        st.image(away_logo, width=32)
            
            if status_short in ["1H", "2H", "ET"]:
                stats_data = api_client.get_fixture_statistics(fixture_id)
                thermometer = analytics.calculate_thermometer(stats_data)
                
                st.markdown(f"""
                <div class='thermometer-box'>
                    <div style='display: flex; justify-content: space-between; font-size: 11px; font-weight: bold;'>
                        <span style='color: #3b82f6;'>{home_team} ({thermometer['home_pct']}%)</span>
                        <span style='color: #ff7676;'>{thermometer['status']}</span>
                        <span style='color: #ef4444;'>({thermometer['away_pct']}%) {away_team}</span>
                    </div>
                    <div class='progress-bar-bg'>
                        <div style='width: {thermometer['home_pct']}%; background-color: #3b82f6; height: 100%;'></div>
                        <div style='width: {thermometer['away_pct']}%; background-color: #ef4444; height: 100%;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

render_live_dashboard()
