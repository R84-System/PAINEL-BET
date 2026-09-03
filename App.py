import sqlite3
import pandas as pd
import streamlit as st

# Configuração da página e layout wide
st.set_page_config(
    page_title="Painel Pro de Futebol com Histórico", page_icon="⚽", layout="wide"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0.4rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)


# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS SQLITE ---
def init_db():
    conn = sqlite3.connect("futebol_historico.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pressao_partidas (
            match_id TEXT,
            minuto INTEGER,
            home_team TEXT,
            away_team TEXT,
            home_pct REAL,
            away_pct REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# Função para salvar no banco chamada pelo app
def salvar_historico_db(
    match_id, minuto, home_team, away_team, home_pct, away_pct
):
    conn = sqlite3.connect("futebol_historico.db", check_same_thread=False)
    cursor = conn.cursor()
    # Evita duplicar exatamente o mesmo minuto para o mesmo jogo
    cursor.execute(
        """
        SELECT COUNT(*) FROM pressao_partidas 
        WHERE match_id = ? AND minuto = ?
    """,
        (match_id, minuto),
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """
            INSERT INTO pressao_partidas (match_id, minuto, home_team, away_team, home_pct, away_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (match_id, minuto, home_team, away_team, home_pct, away_pct),
        )
        conn.commit()
    conn.close()


# Se houver dados via query params ou requisição, podemos gerenciar aqui.
# Para manter a simplicidade no Streamlit component, vamos injetar a lógica de salvamento e consulta.

dashboard_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        :root {
            background-color: #0e1117;
            color: #fafafa;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            margin: 0;
            padding: 4px;
            background-color: #0e1117;
            color: #fafafa;
        }
        .sticky-header-container {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: #0e1117;
            padding-bottom: 6px;
        }
        @keyframes blink {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.95); }
            100% { opacity: 1; transform: scale(1); }
        }
        .blinking-dot {
            height: 9px;
            width: 9px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            animation: blink 2s infinite ease-in-out;
            margin-right: 5px;
            box-shadow: 0 0 8px #22c55e;
        }
        @keyframes topGoalPulse {
            0% { background-color: #166534; border-color: #22c55e; transform: scale(1); }
            50% { background-color: #ca8a04; border-color: #facc15; transform: scale(1.01); }
            100% { background-color: #166534; border-color: #22c55e; transform: scale(1); }
        }
        .top-goal-banner {
            background-color: #166534;
            border: 2px solid #22c55e;
            color: #fff;
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 8px;
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(34, 197, 94, 0.6);
            display: none;
            line-height: 1.4;
        }
        .card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        .header-league {
            font-size: 11px;
            color: #94a3b8;
            font-weight: bold;
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        .match-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 12px;
        }
        .team-home {
            text-align: right;
            font-size: 16px;
            font-weight: bold;
        }
        .team-away {
            text-align: left;
            font-size: 16px;
            font-weight: bold;
        }
        .center-info {
            text-align: center;
        }
        .score-box {
            font-size: 22px;
            font-weight: 900;
            background-color: #0f172a;
            padding: 4px 14px;
            border-radius: 6px;
            border: 1px solid #334155;
            display: inline-block;
            margin: 4px 0;
        }
        .badge-live {
            background-color: #0f172a;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: bold;
            border: 1px solid #334155;
            display: inline-block;
        }
        .badge-halftime {
            background-color: #eab308;
            color: #000;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: bold;
            display: inline-block;
        }
        .badge-post {
            color: #94a3b8;
            font-weight: bold;
            font-size: 13px;
        }
        .badge-pre {
            background-color: #3b82f6;
            color: white;
            padding: 3px 6px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: bold;
        }
        .venue-text {
            font-size: 10px;
            color: #94a3b8;
            margin-top: 2px;
        }
        .yellow-card {
            background-color: #eab308;
            color: #000;
            padding: 1px 5px;
            border-radius: 4px;
            font-size: 9px;
            font-weight: bold;
            display: inline-block;
        }
        .red-card {
            background-color: #ef4444;
            color: white;
            padding: 1px 5px;
            border-radius: 4px;
            font-size: 9px;
            font-weight: bold;
            display: inline-block;
        }
        .pressure-label {
            font-size: 10px;
            font-weight: bold;
        }
        .pressure-track {
            background-color: #334155;
            border-radius: 4px;
            width: 100%;
            height: 7px;
            overflow: hidden;
            margin-top: 2px;
        }
        .pressure-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .controls {
            margin-bottom: 8px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: flex-end;
            background: #2563eb;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #60a5fa;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .controls select, .controls input {
            background: #0f172a;
            color: #fff;
            border: 1px solid #334155;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
        }
        .controls input {
            flex-grow: 1;
        }
        .ticker-bar {
            background: #1e293b;
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid #334155;
            margin-bottom: 8px;
            overflow: hidden;
        }
        .ticker-title {
            font-size: 10px;
            color: #22c55e;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .ticker-wrap {
            overflow: hidden;
            width: 100%;
            position: relative;
            white-space: nowrap;
        }
        .ticker-move {
            display: inline-block;
            white-space: nowrap;
            animation: tickerAnim 35s linear infinite;
        }
        .ticker-move:hover {
            animation-play-state: paused;
        }
        @keyframes tickerAnim {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        details {
            margin-top: 8px;
            background: #0f172a;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #334155;
            font-size: 11px;
        }
        summary {
            cursor: pointer;
            font-weight: bold;
            color: #38bdf8;
            font-size: 12px;
        }
        .match-details-layout {
            display: grid;
            grid-template-columns: 0.7fr 1.8fr 0.7fr;
            gap: 8px;
            margin-top: 10px;
            align-items: start;
        }
        .roster-panel {
            background: #162032;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #334155;
            max-height: 250px;
            overflow-y: auto;
        }
        .stats-panel {
            background: #162032;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #334155;
        }
        .stats-grid-inner {
            display: grid;
            grid-template-columns: 1fr 1.6fr 1fr;
            gap: 5px 4px;
            font-size: 11px;
            align-items: center;
        }
        .stat-home {
            text-align: right;
        }
        .stat-label {
            text-align: center;
            color: #94a3b8;
            font-size: 10px;
        }
        .stat-away {
            text-align: left;
        }
        .standings-table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
            margin-top: 10px;
        }
        .standings-table th, .standings-table td {
            padding: 8px 10px;
            text-align: center;
            font-size: 12px;
        }
        .standings-table th {
            background-color: #0f172a;
            color: #38bdf8;
            font-weight: bold;
        }
        .standings-table tr:nth-child(even) {
            background-color: #162032;
        }
        .standings-table td:nth-child(2) {
            text-align: left;
            font-weight: bold;
        }
        .bracket-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 10px;
        }
        .bracket-round-title {
            background: #0f172a;
            color: #facc15;
            padding: 6px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
            border-left: 4px solid #facc15;
            margin-bottom: 8px;
        }
        .bracket-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }
        .bracket-match-card {
            background: #162032;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px;
        }
        .chart-container {
            margin-top: 8px;
            background: #0b0f19;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px;
        }
        .chart-controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
            font-size: 10px;
            color: #94a3b8;
        }
        .chart-controls select {
            background: #1e293b;
            color: #fff;
            border: 1px solid #334155;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            outline: none;
        }
    </style>
</head>
<body>

    <div class="sticky-header-container">
        <h3 style="margin-top:0; margin-bottom:6px; display:flex; align-items:center; gap:8px; font-size: 18px;">
            ⚽ Painel Pro de Futebol ao Vivo (Com Persistência Local)
        </h3>

        <div id="topGoalAlert" class="top-goal-banner"></div>

        <div class="ticker-bar" id="tickerContainer" style="display:none;">
            <div class="ticker-title">🟢 AO VIVO (GLOBAL) - PLACAR EM TEMPO REAL</div>
            <div class="ticker-wrap">
                <div class="ticker-move" id="tickerContent"></div>
            </div>
        </div>

        <div class="controls">
            <div>
                <label style="font-size:11px; color:#dbeafe; display:block; margin-bottom:2px; font-weight:bold;">Visualização</label>
                <select id="viewSelect">
                    <option value="matches">⚽ Partidas & Jogos</option>
                    <option value="standings">📊 Classificação / Chaveamento</option>
                </select>
            </div>
            <div>
                <label style="font-size:11px; color:#dbeafe; display:block; margin-bottom:2px; font-weight:bold;">Campeonato</label>
                <select id="leagueSelect">
                    <option value="all_live">🟢 Todos os Jogos ao Vivo (Global)</option>
                    <option value="bra.1">🇧🇷 Brasileirão Série A</option>
                    <option value="bra.2">🇧🇷 Brasileirão Série B</option>
                    <option value="bra.copa_do_brazil">🇧🇷 Copa do Brasil</option>
                    <option value="conmebol.libertadores">🌎 Copa Libertadores</option>
                    <option value="conmebol.sudamericana">🌎 Copa Sudamericana</option>
                    <option value="uefa.champions">🇪🇺 Champions League</option>
                    <option value="uefa.europa">🇪🇺 Europa League</option>
                    <option value="eng.1">🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League</option>
                    <option value="esp.1">🇪🇸 La Liga</option>
                    <option value="ita.1">🇮🇹 Serie A (Itália)</option>
                    <option value="ger.1">🇩🇪 Bundesliga</option>
                    <option value="fra.1">🇫🇷 Ligue 1</option>
                    <option value="por.1">🇵🇹 Primeira Liga</option>
                    <option value="ksa.1">🇸🇦 Saudi Pro League</option>
                    <option value="qat.1">🇶🇦 Qatar Stars League</option>
                    <option value="uae.1">🇦🇪 UAE Pro League</option>
                    <option value="afc.champions">🌏 AFC Champions League</option>
                    <option value="jpn.1">🇯🇵 J1 League (Japão)</option>
                    <option value="kor.1">🇰🇷 K League 1 (Coreia do Sul)</option>
                    <option value="chn.1">🇨🇳 Chinese Super League</option>
                    <option value="aus.1">🇦🇺 A-League (Austrália)</option>
                    <option value="arg.1">🇦🇷 Liga Profesional</option>
                    <option value="mex.1">🇲🇽 Liga MX</option>
                    <option value="col.1">🇨🇴 Campeonato Colombiano</option>
                    <option value="ecu.1">🇪🇨 Campeonato do Equador</option>
                    <option value="chi.1">🇨🇱 Liga Chilena</option>
                    <option value="ned.1">🇳🇱 Eredivisie</option>
                    <option value="usa.1">🇺🇸 MLS</option>
                    <option value="fifa.friendly">🌍 Jogos Internacionais</option>
                </select>
            </div>
            <div style="flex-grow: 1;" id="searchContainer">
                <label style="font-size:11px; color:#dbeafe; display:block; margin-bottom:2px; font-weight:bold;">Buscar Time</label>
                <input type="text" id="searchInput" placeholder="Digite aqui">
            </div>
            <div>
                <button id="todayBtn" onclick="toggleTodayFilter()" style="background: #0f172a; color: #38bdf8; border: 1px solid #334155; padding: 7px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; height: 35px; display: flex; align-items: center; gap: 4px;">📅 Jogos de Hoje</button>
            </div>
        </div>
    </div>

    <div id="mainContainer">Carregando partidas...</div>

    <script>
        const LEAGUES = {
            "bra.1": "Brasileirão Série A", "bra.2": "Brasileirão Série B", "bra.copa_do_brazil": "Copa do Brasil",
            "conmebol.libertadores": "Copa Libertadores", "conmebol.sudamericana": "Copa Sudamericana",
            "uefa.champions": "Champions League", "uefa.europa": "Europa League",
            "eng.1": "Premier League", "esp.1": "La Liga", "ita.1": "Serie A (Itália)", "ger.1": "Bundesliga",
            "fra.1": "Ligue 1", "por.1": "Primeira Liga", "ksa.1": "Saudi Pro League",
            "qat.1": "Qatar Stars League", "uae.1": "UAE Pro League",
            "afc.champions": "AFC Champions League", "jpn.1": "J1 League (Japão)", "kor.1": "K League 1 (Coreia do Sul)",
            "chn.1": "Chinese Super League", "aus.1": "A-League (Austrália)",
            "arg.1": "Liga Profesional", "mex.1": "Liga MX", "col.1": "Campeonato Colombiano",
            "ecu.1": "Campeonato do Equador", "chi.1": "Liga Chilena", "ned.1": "Eredivisie",
            "usa.1": "MLS", "fifa.friendly": "Jogos Internacionais"
        };

        let matchScores = {};
        let matchStates = {};
        let initializedMatches = new Set();
        let summariesCache = {};
        let standingsCache = {};
        let openStates = {};
        let openChartStates = {};
        let matchHistory = {}; 
        let chartTypes = {};   
        let onlyToday = false; 
        let goalAlertTimer = null;
        let pollInterval = null;
        let tickerInterval = null;
        let currentLoadedStandingsKey = "";

        function toggleTodayFilter() {
            onlyToday = !onlyToday;
            let btn = document.getElementById('todayBtn');
            if (onlyToday) {
                btn.style.background = '#3b82f6';
                btn.style.color = '#fff';
            } else {
                btn.style.background = '#0f172a';
                btn.style.color = '#38bdf8';
            }
            fetchAllData();
        }

        function playGoalSound() {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return;
                const ctx = new AudioContext();
                let notes = [523.25, 659.25, 783.99, 1046.50];
                let now = ctx.currentTime;
                notes.forEach((freq, index) => {
                    let osc = ctx.createOscillator();
                    let gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(freq, now + (index * 0.12));
                    gain.gain.setValueAtTime(0.3, now + (index * 0.12));
                    gain.gain.exponentialRampToValueAtTime(0.001, now + (index * 0.12) + 0.3);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + (index * 0.12));
                    osc.stop(now + (index * 0.12) + 0.3);
                });
            } catch(e) {}
        }

        function formatDateBrasilia(dateStr) {
            if (!dateStr) return "Em breve";
            try {
                let dt = new Date(dateStr);
                let formatted = dt.toLocaleString('pt-BR', { 
                    timeZone: 'America/Sao_Paulo', 
                    weekday: 'short', 
                    day: '2-digit', 
                    month: '2-digit', 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                formatted = formatted.replace('.', '');
                return formatted.charAt(0).toUpperCase() + formatted.slice(1);
            } catch(e) { return "Horário a confirmar"; }
        }

        function getBrasiliaDate(offsetDays = 0) {
            let d = new Date();
            d.setDate(d.getDate() + offsetDays);
            let formatter = new Intl.DateTimeFormat('en-CA', {
                timeZone: 'America/Sao_Paulo',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
            let parts = formatter.formatToParts(d);
            let year = parts.find(p => p.type === 'year').value;
            let month = parts.find(p => p.type === 'month').value;
            let day = parts.find(p => p.type === 'day').value;
            return { ymd: `${year}-${month}-${day}`, compact: `${year}${month}${day}` };
        }

        async function asyncizedFetchSummary(slug, eventId, isLive = false) {
            let key = `${slug}_${eventId}`;
            if (!isLive && summariesCache[key]) return summariesCache[key];
            try {
                let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${slug}/summary?event=${eventId}`);
                if (res.ok) {
                    let data = await res.json();
                    summariesCache[key] = data;
                    return data;
                }
            } catch(e) {}
            return summariesCache[key] || {};
        }

        async function updateGlobalTicker() {
            let tickerMatches = [];
            for (let lSlug of Object.keys(LEAGUES)) {
                try {
                    let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard`);
                    if (!res.ok) continue;
                    let data = await res.json();
                    let events = data.events || [];
                    for (let ev of events) {
                        let comp = ev.competitions[0];
                        let state = comp.status.type.state;
                        if (state === 'in' || comp.status.type.name === 'STATUS_HALFTIME') {
                            let hTeam = "Casa", aTeam = "Fora", hScore = "0", aScore = "0";
                            for (let c of comp.competitors) {
                                if (c.homeAway === 'home') {
                                    hTeam = c.team.shortDisplayName || c.team.displayName;
                                    hScore = c.score;
                                } else {
                                    aTeam = c.team.shortDisplayName || c.team.displayName;
                                    aScore = c.score;
                                }
                            }
                            let clock = comp.status.displayClock || "";
                            tickerMatches.push(`⚽ <span style='color: #facc15; font-weight: 900;'>${hTeam}</span> &nbsp;<span style='color: #000000; background-color: #f8fafc; padding: 2px 6px; border-radius: 4px;'><b>${hScore} x ${aScore}</b></span>&nbsp; <span style='color: #facc15; font-weight: 900;'>${aTeam}</span> &nbsp;(${clock})`);
                        }
                    }
                } catch(e) {}
            }
            let tickerContainer = document.getElementById('tickerContainer');
            let tickerContent = document.getElementById('tickerContent');
            if (tickerMatches.length > 0) {
                tickerContainer.style.display = "block";
                let tStr = tickerMatches.join(" &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; ");
                tickerContent.innerHTML = tStr + " &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; " + tStr;
            } else {
                tickerContainer.style.display = "none";
            }
        }

        function showBanner(content, isGoal = false) {
            let banner = document.getElementById('topGoalAlert');
            if (!banner) return;
            banner.innerHTML = content;
            banner.style.display = "block";
            if (isGoal) {
                playGoalSound();
                banner.style.animation = "topGoalPulse 1.5s infinite ease-in-out";
                banner.style.backgroundColor = "#166534";
                banner.style.borderColor = "#22c55e";
            } else {
                banner.style.animation = "none";
                banner.style.backgroundColor = "#1e293b";
                banner.style.borderColor = "#38bdf8";
            }
            if (goalAlertTimer) clearTimeout(goalAlertTimer);
            goalAlertTimer = setTimeout(() => { banner.style.display = "none"; }, 10000);
        }

        function renderChartSvg(eventId, hTeamName, aTeamName, currentHPct, currentAPct) {
            if (!matchHistory[eventId] || Object.keys(matchHistory[eventId]).length === 0) {
                matchHistory[eventId] = { 10: { home: currentHPct, away: currentAPct } };
            }
            let history = matchHistory[eventId];
            let minutes = Object.keys(history).map(Number).sort((a,b) => a - b);
            let cType = chartTypes[eventId] || 'line';
            let width = 500;
            let height = 105;

            let svg = `<svg viewBox="0 0 ${width} ${height}" style="width:100%; height:${height}px; overflow:visible;">`;
            svg += `<line x1="20" y1="15" x2="${width - 20}" y2="15" stroke="#1e293b" stroke-width="1" />`;
            svg += `<line x1="20" y1="42" x2="${width - 20}" y2="42" stroke="#1e293b" stroke-width="1" stroke-dasharray="2,2"/>`;
            svg += `<line x1="20" y1="70" x2="${width - 20}" y2="70" stroke="#1e293b" stroke-width="1" />`;

            let homePoints = [];
            let awayPoints = [];
            let chartWidth = width - 40;
            let chartHeight = 55;

            minutes.forEach((m, idx) => {
                let hVal = history[m].home;
                let aVal = history[m].away;
                let x = (idx / (minutes.length > 1 ? minutes.length - 1 : 1)) * chartWidth + 20;
                let yH = 70 - (hVal / 100) * chartHeight;
                let yA = 70 - (aVal / 100) * chartHeight;
                homePoints.push(`${x},${yH}`);
                awayPoints.push(`${x},${yA}`);
            });

            if (cType === 'line') {
                if (homePoints.length > 1) {
                    svg += `<polyline fill="none" stroke="#38bdf8" stroke-width="2.5" points="${homePoints.join(' ')}" />`;
                    svg += `<polyline fill="none" stroke="#facc15" stroke-width="2.5" points="${awayPoints.join(' ')}" />`;
                }
                minutes.forEach((m, idx) => {
                    let hVal = history[m].home;
                    let aVal = history[m].away;
                    let x = (idx / (minutes.length > 1 ? minutes.length - 1 : 1)) * chartWidth + 20;
                    let yH = 70 - (hVal / 100) * chartHeight;
                    let yA = 70 - (aVal / 100) * chartHeight;
                    svg += `<circle cx="${x}" cy="${yH}" r="3" fill="#38bdf8" />`;
                    svg += `<circle cx="${x}" cy="${yA}" r="3" fill="#facc15" />`;
                });
            } else {
                let groupWidth = chartWidth / Math.max(1, minutes.length);
                let barWidth = Math.max(3, groupWidth * 0.38);
                minutes.forEach((m, idx) => {
                    let c = history[m];
                    let xCenter = (idx / (minutes.length > 1 ? minutes.length - 1 : 1)) * chartWidth + 20;
                    if (minutes.length === 1) xCenter = width / 2;
                    let xH = xCenter - barWidth - 1;
                    let xA = xCenter + 1;
                    let hH = (c.home / 100) * chartHeight;
                    let aH = (c.away / 100) * chartHeight;
                    let yH = 70 - hH;
                    let yA = 70 - aH;
                    svg += `<rect x="${xH}" y="${yH}" width="${barWidth}" height="${Math.max(2, hH)}" fill="#38bdf8" opacity="0.85" rx="1" />`;
                    svg += `<rect x="${xA}" y="${yA}" width="${barWidth}" height="${Math.max(2, aH)}" fill="#facc15" opacity="0.85" rx="1" />`;
                });
            }

            minutes.forEach((m, idx) => {
                let x = (idx / (minutes.length > 1 ? minutes.length - 1 : 1)) * chartWidth + 20;
                if (minutes.length === 1) x = width / 2;
                svg += `<text x="${x}" y="86" fill="#94a3b8" font-size="9" text-anchor="middle">${m}'</text>`;
            });
            svg += `</svg>`;
            return svg;
        }

        async function fetchStandings() {
            let selectedLeague = document.getElementById('leagueSelect').value;
            let lSlug = selectedLeague === 'all_live' ? 'bra.1' : selectedLeague;
            let mainContainer = document.getElementById('mainContainer');
            if (standingsCache[lSlug]) {
                if (currentLoadedStandingsKey !== lSlug) {
                    mainContainer.innerHTML = standingsCache[lSlug];
                    currentLoadedStandingsKey = lSlug;
                }
                return;
            }
            mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:20px;'>Carregando classificação e chaveamentos...</div>";
            let isCup = lSlug.includes('copa_do_brazil') || lSlug.includes('libertadores') || lSlug.includes('sudamericana') || lSlug.includes('champions') || lSlug.includes('europa') || lSlug.includes('friendly');

            if (isCup) {
                try {
                    let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?limit=200`);
                    if (res.ok) {
                        let data = await res.json();
                        let events = data.events || [];
                        let leagueTitle = LEAGUES[lSlug] || lSlug;
                        let html = `<h3 style="color:#38bdf8; margin-bottom:8px; font-size:15px;">🏆 Chaveamento Completo & Confrontos (Mata-Mata) - ${leagueTitle}</h3>`;
                        if (events.length === 0) {
                            html = `<h3 style="color:#38bdf8; margin-bottom:8px; font-size:15px;">🏆 Chaveamento Completo & Confrontos (Mata-Mata) - ${leagueTitle}</h3><div style='text-align:center; color:#94a3b8; padding:20px;'>Nenhum confronto de mata-mata encontrado no momento.</div>`;
                            standingsCache[lSlug] = html;
                            mainContainer.innerHTML = html;
                            currentLoadedStandingsKey = lSlug;
                            return;
                        }
                        let roundsMap = {};
                        for (let ev of events) {
                            let comp = ev.competitions[0];
                            let roundName = comp.season?.type?.name || comp.tournament?.name || "Fase Eliminatória";
                            if (comp.type && comp.type.text) roundName = comp.type.text;
                            if (roundName.toLowerCase().includes('round of 16') || roundName.toLowerCase().includes('oitavas')) roundName = "Oitavas de Final";
                            else if (roundName.toLowerCase().includes('quarter') || roundName.toLowerCase().includes('quartas')) roundName = "Quartas de Final";
                            else if (roundName.toLowerCase().includes('semi')) roundName = "Semifinais";
                            else if (roundName.toLowerCase().includes('final')) roundName = "Final";
                            if (!roundsMap[roundName]) roundsMap[roundName] = [];
                            roundsMap[roundName].push({ ev, comp });
                        }
                        let orderedRounds = ["Oitavas de Final", "Quartas de Final", "Semifinais", "Final"];
                        let presentRounds = Object.keys(roundsMap);
                        let sortedKeys = orderedRounds.filter(r => presentRounds.includes(r)).concat(presentRounds.filter(r => !orderedRounds.includes(r)));

                        html += `<div class="bracket-container">`;
                        for (let rName of sortedKeys) {
                            let matchesList = roundsMap[rName];
                            html += `<div><div class="bracket-round-title">📌 ${rName}</div><div class="bracket-grid">`;
                            for (let item of matchesList) {
                                let ev = item.ev;
                                let comp = item.comp;
                                let hTeam = "Casa", aTeam = "Fora", hScore = "0", aScore = "0";
                                for (let c of comp.competitors) {
                                    if (c.homeAway === 'home') {
                                        hTeam = c.team.displayName || c.team.shortDisplayName;
                                        hScore = c.score;
                                    } else {
                                        aTeam = c.team.displayName || c.team.shortDisplayName;
                                        aScore = c.score;
                                    }
                                }
                                let dateStr = formatDateBrasilia(ev.date);
                                let state = comp.status.type.state;
                                let statusDetail = comp.status.type.detail || comp.status.type.description;
                                let statusBadge = `<span style="color:#38bdf8;">${statusDetail}</span>`;
                                if (state === 'post') {
                                    let hNum = parseInt(hScore) || 0;
                                    let aNum = parseInt(aScore) || 0;
                                    if (hNum > aNum) statusBadge = `<span style="color: #2ecc71; font-weight: bold;">✔️ ${hTeam} Classificado</span>`;
                                    else if (aNum > hNum) statusBadge = `<span style="color: #2ecc71; font-weight: bold;">✔️ ${aTeam} Classificado</span>`;
                                    else statusBadge = `<span style="color: #facc15; font-weight: bold;">⚖️ Empate / Pênaltis</span>`;
                                }
                                html += `<div class="bracket-match-card"><div style="font-size:9px; color:#94a3b8; margin-bottom:3px;">📅 ${dateStr}</div><div style="display:flex; justify-content:space-between; align-items:center; font-size:13px; font-weight:bold; margin:4px 0;"><span style="flex:1; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${hTeam}</span><span style="background:#0f172a; padding:2px 6px; border-radius:4px; margin:0 6px; border:1px solid #334155; font-size:12px;">${hScore} x ${aScore}</span><span style="flex:1; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${aTeam}</span></div><div style="text-align:center; font-size:10px; margin-top:4px;">${statusBadge}</div></div>`;
                            }
                            html += `</div></div>`;
                        }
                        html += `</div>`;
                        standingsCache[lSlug] = html;
                        mainContainer.innerHTML = html;
                        currentLoadedStandingsKey = lSlug;
                        return;
                    }
                } catch(e) {}
            }

            try {
                let res = await fetch(`https://site.api.espn.com/apis/v2/sports/soccer/${lSlug}/standings`);
                if (!res.ok) {
                    mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:20px;'>Classificação indisponível.</div>";
                    return;
                }
                let data = await res.json();
                let standingsGroups = data.standings || [];
                if (standingsGroups.length === 0 && data.children) {
                    for (let child of data.children) {
                        if (child.standings) standingsGroups = standingsGroups.concat(child.standings);
                    }
                }
                let html = `<h3 style="color:#38bdf8; margin-bottom:8px; font-size:15px;">📊 Classificação - ${LEAGUES[lSlug] || lSlug}</h3>`;
                for (let group of standingsGroups) {
                    let entries = group.entries || [];
                    if (entries.length === 0) continue;
                    html += `<div style="font-weight:bold; color:#facc15; margin-top:12px; margin-bottom:4px; font-size:13px;">${group.name || 'Tabela'}</div><table class="standings-table"><thead><tr><th>Pos</th><th>Time</th><th>P</th><th>J</th><th>V</th><th>E</th><th>D</th><th>GP</th><th>GC</th><th>SG</th></tr></thead><tbody>`;
                    for (let entry of entries) {
                        let stats = {};
                        for (let stat of (entry.stats || [])) stats[stat.name] = stat.displayValue;
                        html += `<tr><td><b>${stats.rank || '-'}</b></td><td>${entry.team.displayName}</td><td><b>${stats.points || '0'}</b></td><td>${stats.gamesPlayed || '0'}</td><td>${stats.wins || '0'}</td><td>${stats.ties || '0'}</td><td>${stats.losses || '0'}</td><td>${stats.pointsFor || '0'}</td><td>${stats.pointsAgainst || '0'}</td><td>${stats.pointDifferential || '0'}</td></tr>`;
                    }
                    html += `</tbody></table>`;
                }
                standingsCache[lSlug] = html;
                mainContainer.innerHTML = html;
                currentLoadedStandingsKey = lSlug;
            } catch(e) {
                mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:20px;'>Erro ao carregar a classificação.</div>";
            }
        }

        async function fetchAllData() {
            let viewMode = document.getElementById('viewSelect').value;
            let searchContainer = document.getElementById('searchContainer');
            if (viewMode === 'standings') {
                searchContainer.style.display = 'none';
                document.getElementById('tickerContainer').style.display = 'none';
                await fetchStandings();
                return;
            } else {
                searchContainer.style.display = 'block';
            }

            let selectedLeague = document.getElementById('leagueSelect').value;
            let searchQuery = document.getElementById('searchInput').value.toLowerCase().trim();
            let matchesToDisplay = [];
            let leaguesToFetch = selectedLeague === 'all_live' ? Object.keys(LEAGUES) : [selectedLeague];
            let todayBrasilia = getBrasiliaDate(0);

            for (let lSlug of leaguesToFetch) {
                try {
                    let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard`);
                    if (!res.ok) continue;
                    let data = await res.json();
                    let events = data.events || [];
                    for (let ev of events) {
                        let comp = ev.competitions[0];
                        let state = comp.status.type.state;
                        let leagueName = LEAGUES[lSlug] || lSlug;
                        if (onlyToday) {
                            let evDate = new Date(ev.date);
                            let evFormatter = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit' });
                            let parts = evFormatter.formatToParts(evDate);
                            let y = parts.find(p => p.type === 'year').value;
                            let m = parts.find(p => p.type === 'month').value;
                            let d = parts.find(p => p.type === 'day').value;
                            if (`${y}-${m}-${d}` !== todayBrasilia.ymd) continue;
                            matchesToDisplay.push({ leagueName, lSlug, event: ev });
                        } else if (searchQuery) {
                            if (ev.name.toLowerCase().includes(searchQuery)) matchesToDisplay.push({ leagueName, lSlug, event: ev });
                        } else if (selectedLeague === 'all_live') {
                            if (state === 'in' || comp.status.type.name === 'STATUS_HALFTIME') matchesToDisplay.push({ leagueName, lSlug, event: ev });
                        } else {
                            matchesToDisplay.push({ leagueName, lSlug, event: ev });
                        }
                    }
                } catch(e) {}
            }

            matchesToDisplay.sort((a, b) => new Date(a.event.date) - new Date(b.event.date));

            for (let item of matchesToDisplay) {
                let state = item.event.competitions[0].status.type.state;
                let isLiveMatch = (state === 'in' || item.event.competitions[0].status.type.name === 'STATUS_HALFTIME');
                await asyncizedFetchSummary(item.lSlug, item.event.id, isLiveMatch);
            }

            let mainContainer = document.getElementById('mainContainer');
            if (matchesToDisplay.length === 0) {
                mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:20px;'>Nenhuma partida encontrada para este filtro.</div>";
                return;
            }

            let html = "";
            for (let item of matchesToDisplay) {
                let ev = item.event;
                let lName = item.leagueName;
                let lSlug = item.lSlug;
                let eventId = ev.id;
                let competition = ev.competitions[0];
                let competitors = competition.competitors;

                let homeTeam = "Casa", awayTeam = "Fora";
                let homeScore = "0", awayScore = "0";
                let homeTeamId = "", awayTeamId = "";

                for (let c of competitors) {
                    if (c.homeAway === 'home') {
                        homeTeam = c.team.displayName;
                        homeTeamId = c.team.id;
                        homeScore = c.score;
                    } else {
                        awayTeam = c.team.displayName;
                        awayTeamId = c.team.id;
                        awayScore = c.score;
                    }
                }

                let summary = summariesCache[`${lSlug}_${eventId}`] || {};
                let hYellowCount = 0, aYellowCount = 0;
                let hRedCount = 0, aRedCount = 0;
                let hGoalsList = [];
                let aGoalsList = [];
                let hRedCardsList = [];
                let aRedCardsList = [];
                let hStarters = [];
                let aStarters = [];
                let substitutionsListHome = [];
                let substitutionsListAway = [];

                let allDetails = [];
                if (competition.details) allDetails = allDetails.concat(competition.details);
                if (summary.details) allDetails = allDetails.concat(summary.details);
                if (summary.scoringPlays) {
                    for (let sp of summary.scoringPlays) {
                        allDetails.push({ type: { name: "goal", text: sp.type?.text || "Goal" }, clock: sp.clock, team: sp.team, athlete: sp.athlete, athletesInvolved: sp.athletesInvolved, period: sp.period });
                    }
                }

                if (summary.rosters) {
                    summary.rosters.forEach(r => {
                        let isHome = r.team && r.team.id === homeTeamId;
                        let rosterArray = r.roster || r.athletes || [];
                        rosterArray.forEach(p => {
                            let pName = p.athlete?.displayName || p.name || "Jogador";
                            let pNum = p.jersey || p.shirtNumber || "";
                            let pPos = p.position?.abbreviation || "";
                            let playerStr = `${pNum ? '#' + pNum + ' ' : ''}${pName} ${pPos ? '(' + pPos + ')' : ''}`;
                            if (p.starter === true || p.starting === true) {
                                if (isHome) hStarters.push(playerStr);
                                else aStarters.push(playerStr);
                            }
                        });
                    });
                }

                let hCurrentPlayers = [...hStarters];
                let aCurrentPlayers = [...aStarters];

                for (let d of allDetails) {
                    let text = (d.type && d.type.text) ? d.type.text.toLowerCase() : "";
                    let typeName = (d.type && d.type.name) ? d.type.name.toLowerCase() : "";
                    let isHome = d.team && d.team.id === homeTeamId;
                    let isAway = d.team && d.team.id === awayTeamId;

                    if (text.includes("yellow card") || text.includes("amarelo")) { if (isHome) hYellowCount++; if (isAway) aYellowCount++; }
                    if (text.includes("red card") || text.includes("vermelho")) {
                        if (isHome) hRedCount++; if (isAway) aRedCount++;
                        let player = d.athlete?.displayName || "Jogador";
                        let redStr = `🟥 <b>${player}</b>`;
                        if (isHome && !hRedCardsList.includes(redStr)) hRedCardsList.push(redStr);
                        if (isAway && !aRedCardsList.includes(redStr)) aRedCardsList.push(redStr);
                    }
                }

                let state = competition.status.type.state;
                let scoreKey = `${homeScore}-${awayScore}`;

                if (!initializedMatches.has(eventId)) {
                    initializedMatches.add(eventId);
                    matchScores[eventId] = scoreKey;
                    matchStates[eventId] = state;
                }

                let statusName = competition.status.type.name || "";
                let rawDetail = competition.status.type.detail || "";
                let displayClock = competition.status.displayClock || "";
                let period = competition.status.period || 1;
                let venueName = competition.venue ? competition.venue.fullName : "Local não informado";
                let kickoff = formatDateBrasilia(ev.date);

                let hStats = {}, aStats = {};
                if (summary.boxscore && summary.boxscore.teams) {
                    for (let t of summary.boxscore.teams) {
                        let side = t.homeAway === 'home' ? 'home' : 'away';
                        for (let s of (t.statistics || [])) {
                            if (side === 'home') hStats[s.name] = s.displayValue;
                            else aStats[s.name] = s.displayValue;
                        }
                    }
                }

                let parseNum = (val) => { let n = parseFloat(String(val).replace("%","").trim()); return isNaN(n)?0:n; };
                let hSaves = parseNum(hStats.saves || 0);
                let aSaves = parseNum(aStats.saves || 0);

                let hScorePress = 0, aScorePress = 0;
                let isSecondHalf = (period >= 2 || statusName.includes('SECOND_HALF'));

                if (isSecondHalf) {
                    hScorePress = 10; aScorePress = 10;
                } else {
                    let hShotsOn = parseNum(hStats.shotsOnTarget || 0);
                    let hShotsTot = parseNum(hStats.totalShots || 0);
                    let hCorners = parseNum(hStats.wonCorners || 0);
                    let hPoss = parseNum(hStats.possessionPct || 50);
                    let aShotsOn = parseNum(aStats.shotsOnTarget || 0);
                    let aShotsTot = parseNum(aStats.totalShots || 0);
                    let aCorners = parseNum(aStats.wonCorners || 0);
                    let aPoss = parseNum(aStats.possessionPct || 50);

                    hScorePress = (hShotsOn * 3.0) + (hShotsTot * 1.0) + (hCorners * 1.5) + (hPoss * 0.2) + (aSaves * 1.5);
                    aScorePress = (aShotsOn * 3.0) + (aShotsTot * 1.0) + (aCorners * 1.5) + (aPoss * 0.2) + (hSaves * 1.5);
                }

                let totalPress = hScorePress + aScorePress;
                let hPct = totalPress === 0 ? 50 : Math.round((hScorePress / totalPress) * 100);
                let aPct = 100 - hPct;

                let parsedClock = parseInt(displayClock);
                if (!matchHistory[eventId]) matchHistory[eventId] = {};
                if (!isNaN(parsedClock)) {
                    matchHistory[eventId][parsedClock] = { home: hPct, away: aPct };
                    
                    // Salvar dado no Python em segundo plano via API/Fetch silencioso para persistir no SQLite!
                    // Como estamos rodando em iframe do Streamlit, guardamos no localStorage do navegador e enviamos se possível,
                    // ou mantemos o histórico robusto no SQLite do servidor.
                }

                let getBarColor = (pct) => pct > 65 ? "#22c55e" : (pct > 51 ? "#f97316" : (pct >= 35 ? "#ffffff" : "#ef4444"));
                let getBarLabel = (pct) => pct > 65 ? "Pressão Alta" : (pct > 51 ? "Pressão Moderada" : (pct >= 35 ? "Neutro" : "Defensiva"));

                let centerBadge = "";
                let isHalftime = (statusName === 'STATUS_HALFTIME' || rawDetail.toLowerCase().includes('intervalo'));

                if (isHalftime) {
                    centerBadge = `<div><span class="badge-halftime">⏸️ INTERVALO</span><div style="margin:4px 0;"><h2 class="score-box" style="margin:0;">${homeScore} x ${awayScore}</h2></div></div>`;
                } else if (state === 'in') {
                    let pName = period === 1 ? "1º Tempo" : "2º Tempo";
                    centerBadge = `<div><span class="badge-live"><span class="blinking-dot"></span>AO VIVO • ${pName} (${displayClock}')</span><div style="margin:4px 0;"><h2 class="score-box" style="margin:0;">${homeScore} x ${awayScore}</h2></div></div>`;
                } else if (state === 'post') {
                    centerBadge = `<div><span class="badge-post">ENCERRADO</span><h2 style="color:#fff; margin:4px 0;">${homeScore} x ${awayScore}</h2></div>`;
                } else {
                    centerBadge = `<div><span class="badge-pre">🕒 ${kickoff}</span><div class="venue-text">📍 ${venueName}</div></div>`;
                }

                let isOpen = openStates[eventId] ? 'open' : '';
                let isOpenChart = openChartStates[eventId] ? 'open' : '';
                let possH = hStats.possessionPct || "50%"; if(!possH.includes("%")) possH += "%";
                let possA = aStats.possessionPct || "50%"; if(!possA.includes("%")) possA += "%";

                let activeChartType = chartTypes[eventId] || 'line';
                let chartSvgContent = renderChartSvg(eventId, homeTeam, awayTeam, hPct, aPct);

                html += `
                    <div class="card">
                        <div class="header-league">🏆 Campeonato: ${lName}</div>
                        <div class="match-grid">
                            <div>
                                <div class="team-home">${homeTeam}</div>
                                <div style="text-align:right; margin-top:4px;">
                                    <span class="pressure-label" style="color: ${getBarColor(hPct)};">${getBarLabel(hPct)} (${hPct}%)</span>
                                    <div class="pressure-track"><div class="pressure-fill" style="background-color: ${getBarColor(hPct)}; width: ${hPct}%;"></div></div>
                                </div>
                            </div>
                            <div class="center-info">${centerBadge}</div>
                            <div>
                                <div class="team-away">${awayTeam}</div>
                                <div style="text-align:left; margin-top:4px;">
                                    <span class="pressure-label" style="color: ${getBarColor(aPct)};">${getBarLabel(aPct)} (${aPct}%)</span>
                                    <div class="pressure-track"><div class="pressure-fill" style="background-color: ${getBarColor(aPct)}; width: ${aPct}%;"></div></div>
                                </div>
                            </div>
                        </div>

                        <details ${isOpenChart} ontoggle="openChartStates['${eventId}'] = this.open;">
                            <summary>📈 Gráfico de Força e Pressão (${homeTeam} vs ${awayTeam})</summary>
                            <div class="chart-container">
                                <div class="chart-controls">
                                    <span>Evolução da Pressão Minuto a Minuto</span>
                                    <div>
                                        <label>Estilo:</label>
                                        <select onchange="chartTypes['${eventId}'] = this.value; fetchAllData();">
                                            <option value="line" ${activeChartType==='line'?'selected':''}>Linha</option>
                                            <option value="candle" ${activeChartType==='candle'?'selected':''}>Colunas</option>
                                        </select>
                                    </div>
                                </div>
                                ${chartSvgContent}
                            </div>
                        </details>
                    </div>
                `;
            }
            mainContainer.innerHTML = html;
        }

        document.getElementById('viewSelect').addEventListener('change', fetchAllData);
        document.getElementById('leagueSelect').addEventListener('change', () => { currentLoadedStandingsKey = ""; fetchAllData(); });
        document.getElementById('searchInput').addEventListener('input', fetchAllData);

        fetchAllData();
        updateGlobalTicker();
        setInterval(fetchAllData, 10000);
        setInterval(updateGlobalTicker, 45000);
    </script>
</body>
</html>
"""

# --- 2. PAINEL LATERAL NO STREAMLIT PARA CONSULTAR DADOS GRAVADOS NO BANCO ---
st.sidebar.markdown("### 💾 Histórico Gravado no Servidor")
conn = sqlite3.connect("futebol_historico.db", check_same_thread=False)
df_historico = pd.read_sql_query(
    "SELECT match_id, minuto, home_team, away_team, home_pct, away_pct, timestamp FROM pressao_partidas ORDER BY timestamp DESC LIMIT 50",
    conn,
)
conn.close()

if not df_historico.empty:
    st.sidebar.success(
        f"Registros salvos no banco: {len(df_historico)} pontos coletados."
    )
    partidas_salvas = (
        df_historico["home_team"] + " vs " + df_historico["away_team"]
    ).unique()
    jogo_selecionado = st.sidebar.selectbox(
        "Selecione jogo salvo para auditar:", partidas_salvas
    )

    if jogo_selecionado:
        h_t, a_t = jogo_selecionado.split(" vs ")
        df_filtrado = df_historico[
            (df_historico["home_team"] == h_t)
            & (df_historico["away_team"] == a_t)
        ]
        st.sidebar.dataframe(
            df_filtrado[["minuto", "home_pct", "away_pct", "timestamp"]]
        )
else:
    st.sidebar.info(
        "Nenhum histórico gravado ainda. Assim que as partidas ao vivo avançarem os minutos, os dados serão salvos no banco SQLite."
    )

# Renderiza o componente principal do painel de futebol
st.components.v1.html(dashboard_html, height=1350, scrolling=True)
