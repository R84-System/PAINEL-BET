# app.py
# Painel Inteligente de Futebol para Transmissões ao Vivo (Com Termômetro em Barra e Estatísticas Expandidas)

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
    "accent_home": "#3b82f6",
    "accent_away": "#ef4444",
}

# =====================================================================
# 2. CAMADA DE INTEGRAÇÃO COM A API (DADOS REAIS DA API-FOOTBALL)
# =====================================================================

class FootballAPI:
    def __init__(self):
        # Resgata a chave configurada nos Secrets do Streamlit Cloud
        self.api_key = st.secrets.get("API_FOOTBALL_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

    def fetch_live_matches(self, league_id: int):
        """Busca partidas ao vivo em tempo real para a liga selecionada."""
        if not self.api_key:
            st.warning("⚠️ Chave da API (API_FOOTBALL_KEY) não configurada nos Secrets do Streamlit.")
            return []
        
        try:
            url = f"{self.base_url}/fixtures?league={league_id}&season=2026&live=all"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", [])
            return []
        except Exception as e:
            st.error(f"Erro de comunicação com a API: {e}")
            return []

    def fetch_match_statistics(self, fixture_id: int):
        """Busca estatísticas detalhadas de uma partida específica ao clicar nela."""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/fixtures/statistics?fixture={fixture_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", [])
            return []
        except:
            return []

# =====================================================================
# 3. MOTOR ANALÍTICO (CÁLCULO DA BARRA DE PRESSÃO E TERMÔMETRO)
# =====================================================================

def calculate_thermometer(stats_data):
    """
    Processa as estatísticas reais (finalizações e posse) para gerar 
    as porcentagens da barra de progresso do termômetro.
    """
    if not stats_data or len(stats_data) < 2:
        return {"home_pct": 50, "away_pct": 50, "status": "Jogo Neutro ⚖️", "trend": "Equilibrado"}
    
    try:
        home_stats = {s["type"]: s["value"] for s in stats_data[0].get("statistics", [])}
        away_stats = {s["type"]: s["value"] for s in stats_data[1].get("statistics", [])}
        
        def parse_val(val):
            if not val: return 0
            if isinstance(val, str) and "%" in val:
                return int(val.replace("%", ""))
            try:
                return int(val)
            except:
                return 0

        # Peso maior para finalizações no alvo e total de finalizações
        home_shots = parse_val(home_stats.get("Shots on Goal", 0)) * 3 + parse_val(home_stats.get("Total Shots", 0))
        away_shots = parse_val(away_stats.get("Shots on Goal", 0)) * 3 + parse_val(away_stats.get("Total Shots", 0))
        
        total = home_shots + away_shots
        if total == 0:
            return {"home_pct": 50, "away_pct": 50, "status": "Jogo Neutro ⚖️", "trend": "Estudo em campo"}
        
        home_pct = int((home_shots / total) * 100)
        away_pct = 100 - home_pct
        
        if home_pct > 65:
            status = "Pressão Forte 🔴"
            trend = f"{stats_data[0]['team']['name']} mais perto do gol"
        elif away_pct > 65:
            status = "Pressão Forte 🔵"
            trend = f"{stats_data[1]['team']['name']} mais perto do gol"
        else:
            status = "Lado a Lado ⚖️"
            trend = "Jogo Aberto / Neutro"
            
        return {"home_pct": home_pct, "away_pct": away_pct, "status": status, "trend": trend}
    except:
        return {"home_pct": 50, "away_pct": 50, "status": "Jogo Neutro ⚖️", "trend": "Equilibrado"}

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

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {UI_THEME['bg_color']};
    }}
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
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
    }}
    .thermometer-container {{
        margin-top: 12px;
        background-color: #121522;
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #22273d;
    }}
    .progress-bar-bg {{
        background-color: #2a2f45;
        border-radius: 4px;
        overflow: hidden;
        height: 10px;
        display: flex;
        width: 100%;
        margin-top: 6px;
        margin-bottom: 6px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 5. PAINEL ADMINISTRATIVO (BARRA LATERAL)
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
        st.caption("Filtro aplicado instantaneamente na live.")
    else:
        st.info("Insira a senha de ADM para alterar os campeonatos.")

st.title("⚽ Painel Inteligente de Partidas")

# =====================================================================
# 6. RENDERIZAÇÃO EM TEMPO REAL COM ESTATÍSTICAS EXPANSÍVEIS
# =====================================================================

@st.fragment(run_every="30s")
def render_broadcast_dashboard():
    league_id = st.session_state.selected_league
    matches = api.fetch_live_matches(league_id)
    
    if not matches:
        st.info("Nenhuma partida ao vivo no momento para esta liga. Verifique se a chave da API está ativa nos Secrets.")
        return

    for match in matches:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})
        
        fixture_id = fixture.get("id")
        status_short = fixture.get("status", {}).get("short", "NS")
        elapsed = fixture.get("status", {}).get("elapsed", 0)
        extra = fixture.get("status", {}).get("extra")
        
        home_team = teams.get("home", {}).get("name", "Casa")
        away_team = teams.get("away", {}).get("name", "Fora")
        home_goals = goals.get("home") if goals.get("home") is not None else 0
        away_goals = goals.get("away") if goals.get("away") is not None else 0
        
        time_display = f"{elapsed}'"
        if extra:
            time_display += f"+{extra}'"

        # Cada jogo fica dentro de um container expansível (clicável para ver estatísticas)
        with st.container():
            st.markdown("<div class='match-card'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 2, 3])
            with col1:
                st.markdown(f"<h3 style='text-align: right; margin: 0; color: #ffffff;'>{home_team}</h3>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='text-align: center;'><span class='live-badge'>AO VIVO {time_display}</span><h2 style='margin: 4px 0 0 0; color: #ffffff;'>{home_goals} x {away_goals}</h2></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<h3 style='text-align: left; margin: 0; color: #ffffff;'>{away_team}</h3>", unsafe_allow_html=True)
            
            # Busca estatísticas em tempo real para alimentar o termômetro em barra
            stats_data = api.fetch_match_statistics(fixture_id)
            thermometer = calculate_thermometer(stats_data)
            
            # Renderização visual da barra de progresso do termômetro
            st.markdown(f"""
            <div class='thermometer-container'>
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
            
            # Botão interativo / Expander para abrir as estatísticas detalhadas ao clicar no jogo
            with st.expander("📊 Clique para ver Estatísticas Detalhadas (Posse, Chutes, Escanteios)"):
                if stats_data and len(stats_data) >= 2:
                    st.markdown("#### Comparativo da Partida")
                    
                    team_h_stats = {s["type"]: s["value"] for s in stats_data[0].get("statistics", [])}
                    team_a_stats = {s["type"]: s["value"] for s in stats_data[1].get("statistics", [])}
                    
                    metrics_to_show = [
                        ("Ball Possession", "Posse de Bola"),
                        ("Shots on Goal", "Chutes ao Gol"),
                        ("Total Shots", "Total de Finalizações"),
                        ("Corner Kicks", "Escanteios"),
                        ("Yellow Cards", "Cartões Amarelos"),
                        ("Fouls", "Faltas")
                    ]
                    
                    for key, label in metrics_to_show:
                        val_h = team_h_stats.get(key, 0)
                        val_a = team_a_stats.get(key, 0)
                        col_m1, col_m2, col_m3 = st.columns([2, 2, 2])
                        with col_m1:
                            st.markdown(f"<div style='text-align: right; font-weight: bold;'>{val_h}</div>", unsafe_allow_html=True)
                        with col_m2:
                            st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 13px;'>{label}</div>", unsafe_allow_html=True)
                        with col_m3:
                            st.markdown(f"<div style='text-align: left; font-weight: bold;'>{val_a}</div>", unsafe_allow_html=True)
                else:
                    st.info("Estatísticas detalhadas indisponíveis no momento para este confronto.")
            
            st.markdown("</div>", unsafe_allow_html=True)

render_broadcast_dashboard()
