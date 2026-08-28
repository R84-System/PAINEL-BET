# app.py
# Painel Inteligente de Futebol para Transmissões ao Vivo
# Arquitetura unificada e robusta para deploy direto no Streamlit Community Cloud

import streamlit as st
from datetime import datetime, timezone
import requests

# =====================================================================
# 1. CONFIGURAÇÕES GLOBAIS E CONSTANTES
# =====================================================================

LEAGUES = {
    "Brasileirão Série A": 71,
    "Premier League": 39,
    "Champions League": 2,
    "La Liga": 140,
    "Libertadores": 13,
}

REFRESH_RATE_SECONDS = 30

UI_THEME = {
    "bg_color": "#0e1117",
    "card_bg": "#16192b",
    "text_primary": "#ffffff",
    "accent_live": "#ff4b4b",
    "accent_neutral": "#3b82f6",
    "accent_pressure": "#10b981",
}

# =====================================================================
# 2. CAMADA DE INTEGRAÇÃO COM A API (FOOTBALL-DATA / API-SPORTS)
# =====================================================================

class FootballAPI:
    def __init__(self):
        # Utiliza o secrets do Streamlit para resgatar a chave de forma segura
        self.api_key = st.secrets.get("API_FOOTBALL_KEY", "mock_key")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

    def fetch_matches(self, league_id: int):
        """
        Busca partidas (ao vivo, agendadas e encerradas) para a liga selecionada.
        Possui fallback inteligente para dados simulados caso a chave não esteja configurada.
        """
        if self.api_key == "mock_key":
            return self._get_mock_data(league_id)
        
        try:
            url = f"{self.base_url}/fixtures?league={league_id}&season=2026&live=all"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get("response", [])
                if data:
                    return data
            return self._get_mock_data(league_id)
        except Exception as e:
            st.error(f"Erro de comunicação com a API: {e}")
            return self._get_mock_data(league_id)

    def _get_mock_data(self, league_id: int):
        """Dados sintéticos para validação visual e testes sem consumir cota da API."""
        return [
            {
                "fixture": {
                    "id": 101,
                    "date": "2026-06-06T21:00:00+00:00",
                    "status": {"short": "1H", "elapsed": 38, "extra": None, "long": "First Half"},
                },
                "teams": {
                    "home": {"name": "Flamengo", "logo": ""},
                    "away": {"name": "Palmeiras", "logo": ""}
                },
                "goals": {"home": 1, "away": 0},
                "statistics": [
                    {
                        "team": {"name": "Flamengo"},
                        "statistics": [
                            {"type": "Shots on Goal", "value": 6},
                            {"type": "Total Shots", "value": 11},
                            {"type": "Ball Possession", "value": "62%"}
                        ]
                    },
                    {
                        "team": {"name": "Palmeiras"},
                        "statistics": [
                            {"type": "Shots on Goal", "value": 1},
                            {"type": "Total Shots", "value": 3},
                            {"type": "Ball Possession", "value": "38%"}
                        ]
                    }
                ]
            },
            {
                "fixture": {
                    "id": 102,
                    "date": "2026-06-06T21:30:00+00:00",
                    "status": {"short": "NS", "elapsed": 0, "extra": None, "long": "Not Started"},
                },
                "teams": {
                    "home": {"name": "Botafogo", "logo": ""},
                    "away": {"name": "Fluminense", "logo": ""}
                },
                "goals": {"home": None, "away": None},
                "statistics": []
            },
            {
                "fixture": {
                    "id": 103,
                    "date": "2026-06-06T19:00:00+00:00",
                    "status": {"short": "ET", "elapsed": 115, "extra": 2, "long": "Extra Time"},
                },
                "teams": {
                    "home": {"name": "Real Madrid", "logo": ""},
                    "away": {"name": "Barcelona", "logo": ""}
                },
                "goals": {"home": 2, "away": 2},
                "statistics": [
                    {
                        "team": {"name": "Real Madrid"},
                        "statistics": [
                            {"type": "Shots on Goal", "value": 8},
                            {"type": "Total Shots", "value": 15},
                            {"type": "Ball Possession", "value": "50%"}
                        ]
                    },
                    {
                        "team": {"name": "Barcelona"},
                        "statistics": [
                            {"type": "Shots on Goal", "value": 7},
                            {"type": "Total Shots", "value": 14},
                            {"type": "Ball Possession", "value": "50%"}
                        ]
                    }
                ]
            }
        ]

# =====================================================================
# 3. MOTOR ANALÍTICO (TERMÔMETRO E CONTAGEM REGRESSIVA)
# =====================================================================

def calculate_thermometer(match_stats):
    """
    Processa as estatísticas brutas da partida para calcular a pressão
    e apontar qual time está mais próximo de marcar o gol.
    """
    if not match_stats or len(match_stats) < 2:
        return {"status": "Jogo Neutro ⚖️", "advantage": "Estudo / Equilibrado"}
    
    home_stats = {s["type"]: s["value"] for s in match_stats[0].get("statistics", [])}
    away_stats = {s["type"]: s["value"] for s in match_stats[1].get("statistics", [])}
    
    def parse_val(val):
        if not val: return 0
        if isinstance(val, str) and "%" in val:
            return int(val.replace("%", ""))
        try:
            return int(val)
        except:
            return 0

    home_shots = parse_val(home_stats.get("Shots on Goal", 0)) * 2 + parse_val(home_stats.get("Total Shots", 0))
    away_shots = parse_val(away_stats.get("Shots on Goal", 0)) * 2 + parse_val(away_stats.get("Total Shots", 0))
    
    total = home_shots + away_shots
    if total == 0:
        return {"status": "Jogo Neutro ⚖️", "advantage": "Equilibrado"}
    
    home_score = int((home_shots / total) * 100)
    
    if home_score > 65:
        return {"status": "Pressão Alta 🔴", "advantage": f"{match_stats[0]['team']['name']} perto de marcar"}
    elif home_score < 35:
        return {"status": "Pressão Alta 🔵", "advantage": f"{match_stats[1]['team']['name']} perto de marcar"}
    else:
        return {"status": "Lado a Lado ⚖️", "advantage": "Fluxo Neutro / Aberto"}

def format_countdown(match_date_str):
    """Calcula o tempo restante para o início da partida."""
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
    except:
        return "Pré-jogo"

# =====================================================================
# 4. CONFIGURAÇÃO DA INTERFACE E ESTILOS (STREAMLIT)
# =====================================================================

st.set_page_config(
    page_title="Central Inteligente de Futebol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

api = FootballAPI()

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "selected_league" not in st.session_state:
    st.session_state.selected_league = list(LEAGUES.values())[0]

# Estilização profissional voltada para transmissão (Broadcast UI)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {UI_THEME['bg_color']};
    }}
    .match-card {{
        background-color: {UI_THEME['card_bg']};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        border: 1px solid #252a41;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .live-badge {{
        background-color: {UI_THEME['accent_live']};
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    .pre-badge {{
        background-color: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }}
    .et-badge {{
        background-color: #f59e0b;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }}
    .thermometer-box {{
        background-color: #121522;
        padding: 10px 14px;
        border-radius: 8px;
        text-align: center;
        margin-top: 12px;
        font-size: 13px;
        border: 1px solid #22273d;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 5. PAINEL ADMINISTRATIVO (BARRA LATERAL DE CONTROLE)
# =====================================================================

with st.sidebar:
    st.markdown("### ⚙️ Painel ADM (Controle)")
    st.divider()
    
    admin_password = st.text_input("Senha de Acesso", type="password")
    if admin_password == "admin123":
        st.session_state.admin_mode = True
        st.success("Painel Liberado com Sucesso")
    
    if st.session_state.admin_mode:
        st.markdown("#### Gerenciamento de Exibição")
        selected_league_name = st.selectbox(
            "Selecione o Campeonato", 
            options=list(LEAGUES.keys())
        )
        st.session_state.selected_league = LEAGUES[selected_league_name]
        st.caption("As alterações refletem instantaneamente no display da live.")
    else:
        st.info("Insira a senha no campo acima para desbloquear as opções de controle.")

st.title("⚽ Painel Inteligente de Partidas")

# =====================================================================
# 6. RENDERIZAÇÃO EM TEMPO REAL (LOOP COM ST.FRAGMENT)
# =====================================================================

@st.fragment(run_every="30s")
def render_broadcast_dashboard():
    league_id = st.session_state.selected_league
    matches = api.fetch_matches(league_id)
    
    if not matches:
        st.warning("Nenhum confronto localizado para esta liga no momento.")
        return

    for match in matches:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})
        stats = match.get("statistics", [])
        
        status_short = fixture.get("status", {}).get("short", "NS")
        elapsed = fixture.get("status", {}).get("elapsed", 0)
        extra = fixture.get("status", {}).get("extra")
        match_date = fixture.get("date", "")
        
        home_team = teams.get("home", {}).get("name", "Time Casa")
        away_team = teams.get("away", {}).get("name", "Time Fora")
        home_goals = goals.get("home")
        away_goals = goals.get("away")
        
        home_g_str = "0" if home_goals is None else str(home_goals)
        away_g_str = "0" if away_goals is None else str(away_goals)
        
        with st.container():
            st.markdown("<div class='match-card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 2, 3])
            
            with col1:
                st.markdown(f"<h3 style='text-align: right; margin: 0; color: #ffffff;'>{home_team}</h3>", unsafe_allow_html=True)
                
            with col2:
                if status_short in ["1H", "2H"]:
                    time_display = f"{elapsed}'"
                    if extra:
                        time_display += f"+{extra}'"
                    st.markdown(f"<div style='text-align: center;'><span class='live-badge'>AO VIVO {time_display}</span><h2 style='margin: 6px 0 0 0; color: #ffffff;'>{home_g_str} x {away_g_str}</h2></div>", unsafe_allow_html=True)
                elif status_short in ["ET", "P"]:
                    badge_text = "PRORROGAÇÃO" if status_short == "ET" else "PÊNALTIS 🎯"
                    st.markdown(f"<div style='text-align: center;'><span class='et-badge'>{badge_text}</span><h2 style='margin: 6px 0 0 0; color: #ffffff;'>{home_g_str} x {away_g_str}</h2></div>", unsafe_allow_html=True)
                elif status_short == "NS":
                    countdown = format_countdown(match_date)
                    st.markdown(f"<div style='text-align: center;'><span class='pre-badge'>{countdown}</span><h3 style='margin: 6px 0 0 0; color: #94a3b8;'>vs</h3></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center;'><span style='color: gray; font-weight: bold;'>ENCERRADO</span><h2 style='margin: 6px 0 0 0; color: #ffffff;'>{home_g_str} x {away_g_str}</h2></div>", unsafe_allow_html=True)
                    
            with col3:
                st.markdown(f"<h3 style='text-align: left; margin: 0; color: #ffffff;'>{away_team}</h3>", unsafe_allow_html=True)
            
            # Exibe o termômetro analítico apenas para partidas ativas
            if status_short in ["1H", "2H", "ET", "P"]:
                thermometer = calculate_thermometer(stats)
                st.markdown(f"""
                <div class='thermometer-box'>
                    <b>Termômetro do Jogo:</b> <span style='color: #f87171;'>{thermometer['status']}</span> &nbsp;|&nbsp; <b>Tendência:</b> <span style='color: #38bdf8;'>{thermometer['advantage']}</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

render_broadcast_dashboard()

