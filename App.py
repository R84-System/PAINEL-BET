"""
Painel Inteligente de Futebol para Transmissões ao Vivo
Arquitetura Modular - Padrão Sênior
"""

import streamlit as st
from datetime import datetime, timezone
import requests

# =====================================================================
# BLOCO 1: CONFIGURAÇÕES E CONSTANTES GLOBAIS
# =====================================================================

LEAGUES = {
    "Brasileirão Série A": 71,
    "Premier League": 39,
    "Champions League": 2,
    "La Liga": 140,
    "Libertadores": 13,
}

UI_THEME = {
    "bg_color": "#0e1117",
    "card_bg": "#16192b",
    "text_primary": "#ffffff",
    "accent_live": "#ff4b4b",
    "accent_home": "#3b82f6",
    "accent_away": "#ef4444",
}

# =====================================================================
# BLOCO 2: CLIENTE DE API (INTEGRAÇÃO EXTERNA)
# =====================================================================

class FootballAPIClient:
    def __init__(self):
        self.api_key = st.secrets.get("API_FOOTBALL_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

    def get_fixtures_by_date(self, league_id: int, date_str: str) -> list:
        if not self.api_key:
            return []
        try:
            url = f"{self.base_url}/fixtures?league={league_id}&season=2026&date={date_str}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", [])
            return []
        except requests.exceptions.RequestException:
            return []

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
# BLOCO 3: MOTOR ANALÍTICO E PROCESSAMENTO DE DADOS
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
    def format_countdown(match_date_str: str) -> str:
        try:
            match_time = datetime.fromisoformat(match_date_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            diff = match_time - now
            total_seconds = int(diff.total_seconds())
            
            if total_seconds <= 0:
                return "Iniciando..."
            
            minutes = total_seconds // 60
            if minutes < 60:
                return f"Inicia em {minutes} min"
            
            hours = minutes // 60
            rem_mins = minutes % 60
            return f"Inicia em {hours}h {rem_mins}m"
        except Exception:
            return "Pré-jogo"

# =====================================================================
# BLOCO 4: COMPONENTES DE INTERFACE (UI & ESTILOS)
# =====================================================================

def configure_page_styles():
    st.set_page_config(
        page_title="Central Inteligente de Futebol",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {UI_THEME['bg_color']}; }}
        .match-card {{
            background-color: {UI_THEME['card_bg']};
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 14px;
            border: 1px solid #252a41;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .live-badge {{
            background-color: {UI_THEME['accent_live']};
            color: white; padding: 4px 10px; border-radius: 4px;
            font-size: 11px; font-weight: 700;
        }}
        .pre-badge {{
            background-color: #3b82f6;
            color: white; padding: 4px 10px; border-radius: 4px;
            font-size: 11px; font-weight: 700;
        }}
        .thermometer-box {{
            margin-top: 12px; background-color: #121522;
            padding: 10px 14px; border-radius: 8px; border: 1px solid #22273d;
        }}
        .progress-bar-bg {{
            background-color: #2a2f45; border-radius: 4px;
            overflow: hidden; height: 10px; display: flex; width: 100%;
            margin-top: 6px; margin-bottom: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_admin():
    with st.sidebar:
        st.markdown("### ⚙️ Painel ADM (Controle)")
        st.divider()
        
        password = st.text_input("Senha de Acesso", type="password")
        if password == "admin123":
            st.session_state.admin_mode = True
            st.success("Acesso Autorizado")
        
        if st.session_state.get("admin_mode", False):
            selected_name = st.selectbox("Campeonato", options=list(LEAGUES.keys()))
            st.session_state.selected_league = LEAGUES[selected_name]
        else:
            st.info("Insira a senha 'admin123' para gerenciar.")

# =====================================================================
# BLOCO 5: CONTROLADOR PRINCIPAL DA APLICAÇÃO
# =====================================================================

configure_page_styles()

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "selected_league" not in st.session_state:
    st.session_state.selected_league = list(LEAGUES.values())[0]

api_client = FootballAPIClient()
analytics = MatchAnalyticsEngine()

render_sidebar_admin()

st.title("⚽ Painel Inteligente de Partidas")

@st.fragment(run_every="30s")
def render_live_dashboard():
    league_id = st.session_state.selected_league
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    matches = api_client.get_fixtures_by_date(league_id, today_str)
    
    if not matches:
        st.info("Nenhuma partida encontrada para hoje nesta liga.")
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
        home_goals = goals.get("home") if goals.get("home") is not None else 0
        away_goals = goals.get("away") if goals.get("away") is not None else 0
        
        with st.container():
            st.markdown("<div class='match-card'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 2, 3])
            with col1:
                st.markdown(f"<h3 style='text-align: right; margin: 0; color: #fff;'>{home_team}</h3>", unsafe_allow_html=True)
            with col2:
                if status_short in ["1H", "2H", "ET"]:
                    time_str = f"{elapsed}'" + (f"+{extra}'" if extra else "")
                    st.markdown(f"<div style='text-align: center;'><span class='live-badge'>AO VIVO {time_str}</span><h2 style='margin: 4px 0 0 0; color: #fff;'>{home_goals} x {away_goals}</h2></div>", unsafe_allow_html=True)
                elif status_short == "NS":
                    countdown = analytics.format_countdown(match_date)
                    st.markdown(f"<div style='text-align: center;'><span class='pre-badge'>{countdown}</span><h3 style='margin: 4px 0 0 0; color: #94a3b8;'>vs</h3></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center;'><span style='color: #94a3b8; font-weight: bold;'>ENCERRADO</span><h2 style='margin: 4px 0 0 0; color: #fff;'>{home_goals} x {away_goals}</h2></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<h3 style='text-align: left; margin: 0; color: #fff;'>{away_team}</h3>", unsafe_allow_html=True)
            
            if status_short in ["1H", "2H", "ET"]:
                stats_data = api_client.get_fixture_statistics(fixture_id)
                thermometer = analytics.calculate_thermometer(stats_data)
                
                st.markdown(f"""
                <div class='thermometer-box'>
                    <div style='display: flex; justify-content: space-between; font-size: 12px; font-weight: bold;'>
                        <span style='color: #3b82f6;'>{home_team} ({thermometer['home_pct']}%)</span>
                        <span style='color: #f87171;'>{thermometer['status']}</span>
                        <span style='color: #ef4444;'>({thermometer['away_pct']}%) {away_team}</span>
                    </div>
                    <div class='progress-bar-bg'>
                        <div style='width: {thermometer['home_pct']}%; background-color: #3b82f6; height: 100%;'></div>
                        <div style='width: {thermometer['away_pct']}%; background-color: #ef4444; height: 100%;'></div>
                    </div>
                    <div style='text-align: center; font-size: 12px; color: #38bdf8; font-weight: 600;'>
                        Tendência: {thermometer['trend']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("📊 Estatísticas Detalhadas da Partida"):
                stats_data = api_client.get_fixture_statistics(fixture_id)
                if stats_data and len(stats_data) >= 2:
                    h_stats = {s["type"]: s["value"] for s in stats_data[0].get("statistics", [])}
                    a_stats = {s["type"]: s["value"] for s in stats_data[1].get("statistics", [])}
                    
                    metrics = [
                        ("Ball Possession", "Posse de Bola"),
                        ("Shots on Goal", "Chutes ao Gol"),
                        ("Total Shots", "Total de Finalizações"),
                        ("Corner Kicks", "Escanteios"),
                        ("Yellow Cards", "Cartões Amarelos"),
                        ("Fouls", "Faltas")
                    ]
                    
                    for key, label in metrics:
                        c1, c2, c3 = st.columns([2, 2, 2])
                        with c1: st.markdown(f"<div style='text-align: right; font-weight: bold;'>{h_stats.get(key, 0)}</div>", unsafe_allow_html=True)
                        with c2: st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 13px;'>{label}</div>", unsafe_allow_html=True)
                        with c3: st.markdown(f"<div style='text-align: left; font-weight: bold;'>{a_stats.get(key, 0)}</div>", unsafe_allow_html=True)
                else:
                    st.info("Estatísticas detalhadas indisponíveis no momento.")
            
            st.markdown("</div>", unsafe_allow_html=True)

render_live_dashboard()
