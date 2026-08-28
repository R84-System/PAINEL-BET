import streamlit as st
import requests
from datetime import datetime, timezone

# Configuração da página
st.set_page_config(
    page_title="Painel de Futebol - Football-Data.org",
    page_icon="⚽",
    layout="wide"
)

# Barra lateral para configurações
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Insira sua Chave da API", type="password", value="")
st.sidebar.markdown("""
---
**Como obter sua chave gratuita:**
1. Acesse [football-data.org](https://www.football-data.org/).
2. Cadastre-se gratuitamente.
3. Copie sua chave de API (X-Auth-Token) e cole no campo acima.
""")

# Dicionário de Ligas suportadas pela API gratuita
LEAGUES = {
    "🇧🇷 Brasileirão Série A": "BSA",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "PL",
    "🇪🇸 La Liga": "PD",
    "🇮🇹 Serie A (Itália)": "SA",
    "🇩🇪 Bundesliga": "BL1",
    "🇫🇷 Ligue 1": "FL1",
    "🇵🇹 Primeira Liga": "PPL",
    "🇪🇺 Champions League": "CL"
}

selected_league_name = st.sidebar.selectbox("Selecione a Competição", list(LEAGUES.keys()))
league_code = LEAGUES[selected_league_name]

# Cabeçalho Principal
st.title("⚽ Painel de Futebol ao Vivo & Classificação")
st.markdown(f"Competição selecionada: **{selected_league_name}**")

if not api_key:
    st.warning("⚠️ Por favor, insira sua chave da API do **football-data.org** na barra lateral para carregar os dados.")
else:
    headers = {"X-Auth-Token": api_key}
    base_url = "https://api.football-data.org/v4"

    # Função para buscar partidas com cache de 60 segundos
    @st.cache_data(ttl=60)
    def fetch_matches(code):
        try:
            url = f"{base_url}/competitions/{code}/matches"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("matches", [])
            else:
                st.error(f"Erro na API (Partidas): Código {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return []

    # Função para buscar tabela de classificação com cache de 5 minutos
    @st.cache_data(ttl=300)
    def fetch_standings(code):
        try:
            url = f"{base_url}/competitions/{code}/standings"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("standings", [])
            else:
                return []
        except Exception:
            return []

    with st.spinner("Carregando dados da API..."):
        matches = fetch_matches(league_code)
        standings = fetch_standings(league_code)

    # Abas para separar Partidas e Classificação
    tab_matches, tab_standings = st.tabs(["📅 Partidas", "🏆 Tabela de Classificação"])

    with tab_matches:
        st.subheader("Partidas da Competição")
        if not matches:
            st.info("Nenhuma partida encontrada ou chave inválida.")
        else:
            # Filtrar jogos ao vivo primeiro, se houver
            live_matches = [m for m in matches if m.get("status") in ["LIVE", "IN_PLAY", "PAUSED"]]
            
            now_utc = datetime.now(timezone.utc)
            today_str = now_utc.strftime("%Y-%m-%d")
            today_matches = [m for m in matches if m.get("utcDate", "").startswith(today_str)]
            
            # Prioriza exibição de jogos ao vivo ou do dia atual
            display_matches = live_matches if live_matches else (today_matches if today_matches else matches[:20])
            
            if live_matches:
                st.markdown("🔴 **PARTIDAS AO VIVO AGORA**")
            
            for m in display_matches:
                home = m.get("homeTeam", {}).get("name", "Casa")
                away = m.get("awayTeam", {}).get("name", "Fora")
                
                score = m.get("score", {})
                ft = score.get("fullTime", {})
                home_goals = ft.get("home") if ft.get("home") is not None else "-"
                away_goals = ft.get("away") if ft.get("away") is not None else "-"
                
                status = m.get("status", "SCHEDULED")
                utc_date = m.get("utcDate", "")
                
                time_str = "A definir"
                if utc_date:
                    try:
                        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
                        time_str = dt.strftime("%d/%m/%Y %H:%M (UTC)")
                    except:
                        pass

                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                with col1:
                    st.write(f"**{home}** vs **{away}**")
                with col2:
                    st.markdown(f"### {home_goals} x {away_goals}")
                with col3:
                    if status in ["LIVE", "IN_PLAY"]:
                        st.markdown(":red[**AO VIVO**]")
                    elif status == "FINISHED":
                        st.markdown("Fim de Jogo")
                    else:
                        st.markdown(f"🕒 {time_str}")
                with col4:
                    st.write(f"Status: `{status}`")
                st.divider()

    with tab_standings:
        st.subheader("Tabela de Classificação Atual")
        if not standings:
            st.info("Tabela de classificação indisponível para esta competição no momento.")
        else:
            total_table = []
            for s in standings:
                if s.get("type") == "TOTAL":
                    total_table = s.get("table", [])
                    break
            
            if not total_table and standings:
                total_table = standings[0].get("table", [])
                
            if total_table:
                table_data = []
                for row in total_table:
                    team_name = row.get("team", {}).get("name", "")
                    table_data.append({
                        "Pos": row.get("position"),
                        "Time": team_name,
                        "Pts": row.get("points"),
                        "J": row.get("playedGames"),
                        "V": row.get("won"),
                        "E": row.get("draw"),
                        "D": row.get("lost"),
                        "GP": row.get("goalsFor"),
                        "GC": row.get("goalsAgainst"),
                        "SG": row.get("goalDifference")
                    })
                st.dataframe(table_data, use_container_width=True)
            else:
                st.info("Dados de classificação não encontrados.")
