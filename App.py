import streamlit as st

st.set_page_config(
    page_title="Painel Pro de Futebol", page_icon="⚽", layout="wide"
)

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
            padding: 10px;
            background-color: #0e1117;
            color: #fafafa;
        }
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
        @keyframes topGoalPulse {
            0% { background-color: #166534; border-color: #22c55e; transform: scale(1); }
            50% { background-color: #ca8a04; border-color: #facc15; transform: scale(1.01); }
            100% { background-color: #166534; border-color: #22c55e; transform: scale(1); }
        }
        .top-goal-banner {
            background-color: #166534;
            border: 2px solid #22c55e;
            color: #fff;
            padding: 14px 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            text-align: center;
            font-size: 15px;
            font-weight: bold;
            animation: topGoalPulse 1.5s infinite ease-in-out;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.6);
            display: none;
            line-height: 1.5;
        }
        .card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .header-league {
            font-size: 12px;
            color: #94a3b8;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .match-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 15px;
        }
        .team-home {
            text-align: right;
            font-size: 18px;
            font-weight: bold;
        }
        .team-away {
            text-align: left;
            font-size: 18px;
            font-weight: bold;
        }
        .center-info {
            text-align: center;
        }
        .score-box {
            font-size: 24px;
            font-weight: 900;
            background-color: #0f172a;
            padding: 6px 16px;
            border-radius: 6px;
            border: 1px solid #334155;
            display: inline-block;
            margin: 5px 0;
        }
        .badge-live {
            background-color: #0f172a;
            color: white;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            border: 1px solid #334155;
            display: inline-block;
        }
        .badge-halftime {
            background-color: #eab308;
            color: #000;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            display: inline-block;
        }
        .badge-post {
            color: #94a3b8;
            font-weight: bold;
            font-size: 14px;
        }
        .badge-pre {
            background-color: #3b82f6;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
        }
        .venue-text {
            font-size: 11px;
            color: #94a3b8;
            margin-top: 4px;
        }
        .yellow-card {
            background-color: #eab308;
            color: #000;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            display: inline-block;
        }
        .red-card {
            background-color: #ef4444;
            color: white;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            display: inline-block;
        }
        .pressure-label {
            font-size: 11px;
            font-weight: bold;
        }
        .pressure-track {
            background-color: #334155;
            border-radius: 4px;
            width: 100%;
            height: 8px;
            overflow: hidden;
            margin-top: 3px;
        }
        .pressure-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .controls {
            margin-bottom: 15px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            background: #1e293b;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        .controls select, .controls input {
            background: #0f172a;
            color: #fff;
            border: 1px solid #334155;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        }
        .controls input {
            flex-grow: 1;
        }
        .ticker-bar {
            background: #1e293b;
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #334155;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .ticker-title {
            font-size: 11px;
            color: #22c55e;
            font-weight: bold;
            margin-bottom: 6px;
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
            margin-top: 10px;
            background: #0f172a;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #334155;
            font-size: 12px;
        }
        summary {
            cursor: pointer;
            font-weight: bold;
            color: #38bdf8;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            text-align: center;
            margin-top: 8px;
            gap: 10px;
        }
        .standings-table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #334155;
            margin-top: 15px;
        }
        .standings-table th, .standings-table td {
            padding: 10px 12px;
            text-align: center;
            font-size: 13px;
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
            gap: 20px;
            margin-top: 15px;
        }
        .bracket-round-title {
            background: #0f172a;
            color: #facc15;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            border-left: 4px solid #facc15;
            margin-bottom: 10px;
        }
        .bracket-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 12px;
        }
        .bracket-match-card {
            background: #162032;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px;
        }
    </style>
</head>
<body>

    <h2 style="margin-top:0; margin-bottom:12px; display:flex; align-items:center; gap:10px;">
        ⚽ Painel Pro de Futebol ao Vivo
    </h2>

    <div id="topGoalAlert" class="top-goal-banner"></div>

    <div class="ticker-bar" id="tickerContainer" style="display:none;">
        <div class="ticker-title">🟢 TICKER AO VIVO (GLOBAL) - PLACAR EM TEMPO REAL</div>
        <div class="ticker-wrap">
            <div class="ticker-move" id="tickerContent"></div>
        </div>
    </div>

    <div class="controls">
        <div>
            <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">Visualização</label>
            <select id="viewSelect">
                <option value="matches">⚽ Partidas & Jogos</option>
                <option value="standings">📊 Classificação & Chaveamentos</option>
            </select>
        </div>
        <div>
            <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">Campeonato</label>
            <select id="leagueSelect">
                <option value="all_live">🟢 Todos os Jogos ao Vivo (Global)</option>
                <option value="bra.1">🇧🇷 Brasileirão Série A</option>
                <option value="bra.2">🇧🇷 Brasileirão Série B</option>
                <option value="bra.copa_brasil">🇧🇷 Copa do Brasil</option>
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
            <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">Buscar Time</label>
            <input type="text" id="searchInput" placeholder="Ex: Flamengo, Real Madrid, Grêmio...">
        </div>
    </div>

    <div id="mainContainer">Carregando partidas...</div>

    <script>
        const LEAGUES = {
            "bra.1": "Brasileirão Série A", "bra.2": "Brasileirão Série B", "bra.copa_brasil": "Copa do Brasil",
            "conmebol.libertadores": "Copa Libertadores", "conmebol.sudamericana": "Copa Sudamericana",
            "uefa.champions": "Champions League", "uefa.europa": "Europa League",
            "eng.1": "Premier League", "esp.1": "La Liga", "ita.1": "Serie A (Itália)", "ger.1": "Bundesliga",
            "fra.1": "Ligue 1", "por.1": "Primeira Liga", "ksa.1": "Saudi Pro League",
            "arg.1": "Liga Profesional", "mex.1": "Liga MX", "col.1": "Campeonato Colombiano",
            "ecu.1": "Campeonato do Equador", "chi.1": "Liga Chilena", "ned.1": "Eredivisie",
            "usa.1": "MLS", "fifa.friendly": "Jogos Internacionais"
        };

        let previousScores = {};
        let summariesCache = {};
        let standingsCache = {};
        let openStates = {};
        let goalAlertTimer = null;
        let pollInterval = null;
        let currentLoadedStandingsKey = "";

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

        function getDateString(offsetDays) {
            let d = new Date();
            d.setDate(d.getDate() + offsetDays);
            let year = d.getFullYear();
            let month = String(d.getMonth() + 1).padStart(2, '0');
            let day = String(d.getDate()).padStart(2, '0');
            return `${year}${month}${day}`;
        }

        async function asyncizedFetchSummary(slug, eventId) {
            let key = `${slug}_${eventId}`;
            if (summariesCache[key]) return summariesCache[key];
            try {
                let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${slug}/summary?event=${eventId}`);
                if (res.ok) {
                    let data = await res.json();
                    summariesCache[key] = data;
                    return data;
                }
            } catch(e) {}
            return {};
        }

        async function updateGlobalTicker() {
            let tickerMatches = [];
            let yestStr = getDateString(-1);
            let todayStr = getDateString(0);

            for (let lSlug of Object.keys(LEAGUES)) {
                try {
                    let [resYest, resToday] = await Promise.all([
                        fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?dates=${yestStr}`),
                        fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?dates=${todayStr}`)
                    ]);

                    let dataYest = resYest.ok ? await resYest.json() : { events: [] };
                    let dataToday = resToday.ok ? await resToday.json() : { events: [] };

                    let eventMap = {};
                    (dataYest.events || []).forEach(ev => eventMap[ev.id] = ev);
                    (dataToday.events || []).forEach(ev => eventMap[ev.id] = ev);
                    let events = Object.values(eventMap);

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

        function triggerTopGoalAlert(scoringTeam, scorerName, hTeam, aTeam, hScore, aScore) {
            let banner = document.getElementById('topGoalAlert');
            if (!banner) return;
            banner.innerHTML = `⚽ GOL DO <b>${scoringTeam.toUpperCase()}</b><br>Autor: <b>${scorerName}</b><br><span style="font-size:14px; color:#facc15;">${hTeam} ${hScore} x ${aScore} ${aTeam}</span>`;
            banner.style.display = "block";
            if (goalAlertTimer) clearTimeout(goalAlertTimer);
            goalAlertTimer = setTimeout(() => {
                banner.style.display = "none";
            }, 12000);
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

            mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:30px;'>Carregando classificação e chaveamentos...</div>";

            let isCup = lSlug.includes('copa_brasil') || lSlug.includes('libertadores') || lSlug.includes('sudamericana') || lSlug.includes('champions') || lSlug.includes('europa') || lSlug.includes('friendly');

            if (isCup) {
                try {
                    let res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard`);
                    if (res.ok) {
                        let data = await res.json();
                        let events = data.events || [];
                        let leagueTitle = LEAGUES[lSlug] || lSlug;
                        
                        let html = `<h3 style="color:#38bdf8; margin-bottom:10px;">🏆 Chaveamento & Confrontos (Mata-Mata) - ${leagueTitle}</h3>`;
                        
                        if (events.length === 0) {
                            html = `
                                <h3 style="color:#38bdf8; margin-bottom:10px;">🏆 Chaveamento & Confrontos (Mata-Mata) - ${leagueTitle}</h3>
                                <div style='text-align:center; color:#94a3b8; padding:30px;'>Nenhum confronto de mata-mata encontrado no momento para este campeonato.</div>
                            `;
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
                            if (!roundsMap[roundName]) roundsMap[roundName] = [];
                            roundsMap[roundName].push({ ev, comp });
                        }

                        html += `<div class="bracket-container">`;
                        for (let [rName, matchesList] of Object.entries(roundsMap)) {
                            html += `
                                <div>
                                    <div class="bracket-round-title">📌 ${rName}</div>
                                    <div class="bracket-grid">
                            `;
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
                                let statusDetail = comp.status.type.detail || comp.status.type.description || comp.status.type.name;

                                html += `
                                    <div class="bracket-match-card">
                                        <div style="font-size:10px; color:#94a3b8; margin-bottom:4px;">📅 ${dateStr}</div>
                                        <div style="display:flex; justify-content:space-between; align-items:center; font-size:14px; font-weight:bold; margin:6px 0;">
                                            <span style="flex:1; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${hTeam}">${hTeam}</span>
                                            <span style="background:#0f172a; padding:3px 8px; border-radius:4px; margin:0 8px; border:1px solid #334155; font-size:13px;">${hScore} x ${aScore}</span>
                                            <span style="flex:1; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${aTeam}">${aTeam}</span>
                                        </div>
                                        <div style="text-align:center; font-size:10px; color:#38bdf8; margin-top:4px;">${statusDetail}</div>
                                    </div>
                                `;
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
                    let errHtml = "<div style='text-align:center; color:#94a3b8; padding:30px;'>Classificação indisponível para esta liga no momento.</div>";
                    mainContainer.innerHTML = errHtml;
                    return;
                }
                let data = await res.json();
                let standingsGroups = data.standings || [];

                if (standingsGroups.length === 0 && data.children) {
                    for (let child of data.children) {
                        if (child.standings) {
                            standingsGroups = standingsGroups.concat(child.standings);
                        }
                    }
                }

                if (standingsGroups.length === 0) {
                    let errHtml = "<div style='text-align:center; color:#94a3b8; padding:30px;'>Nenhuma tabela encontrada para este campeonato.</div>";
                    mainContainer.innerHTML = errHtml;
                    return;
                }

                let html = `<h3 style="color:#38bdf8; margin-bottom:10px;">📊 Classificação - ${LEAGUES[lSlug] || lSlug}</h3>`;

                for (let group of standingsGroups) {
                    let entries = group.entries || [];
                    if (entries.length === 0) continue;

                    entries.sort((a, b) => {
                        let getRank = (ent) => {
                            let s = {};
                            for (let st of (ent.stats || [])) s[st.name] = st.displayValue;
                            return parseInt(s.rank || 999);
                        };
                        return getRank(a) - getRank(b);
                    });

                    html += `
                        <div style="font-weight:bold; color:#facc15; margin-top:15px; margin-bottom:5px;">${group.name || 'Tabela Principal'}</div>
                        <table class="standings-table">
                            <thead>
                                <tr>
                                    <th>Pos</th>
                                    <th>Time</th>
                                    <th>P</th>
                                    <th>J</th>
                                    <th>V</th>
                                    <th>E</th>
                                    <th>D</th>
                                    <th>GP</th>
                                    <th>GC</th>
                                    <th>SG</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;

                    for (let entry of entries) {
                        let stats = {};
                        for (let stat of (entry.stats || [])) {
                            stats[stat.name] = stat.displayValue;
                        }
                        let teamName = entry.team.displayName || entry.team.name;
                        let pos = stats.rank || '-';
                        let pts = stats.points || '0';
                        let p = stats.gamesPlayed || '0';
                        let w = stats.wins || '0';
                        let d = stats.ties || '0';
                        let l = stats.losses || '0';
                        let gf = stats.pointsFor || '0';
                        let ga = stats.pointsAgainst || '0';
                        let gd = stats.pointDifferential || '0';

                        html += `
                            <tr>
                                <td><b>${pos}</b></td>
                                <td>${teamName}</td>
                                <td><b>${pts}</b></td>
                                <td>${p}</td>
                                <td>${w}</td>
                                <td>${d}</td>
                                <td>${l}</td>
                                <td>${gf}</td>
                                <td>${ga}</td>
                                <td>${gd}</td>
                            </tr>
                        `;
                    }
                    html += `</tbody></table>`;
                }
                standingsCache[lSlug] = html;
                mainContainer.innerHTML = html;
                currentLoadedStandingsKey = lSlug;
            } catch(e) {
                mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:30px;'>Erro ao carregar a classificação.</div>";
            }
        }

        async function fetchAllData() {
            let viewMode = document.getElementById('viewSelect').value;
            let searchContainer = document.getElementById('searchContainer');
            
            if (viewMode === 'standings') {
                searchContainer.style.display = 'none';
                document.getElementById('tickerContainer').style.display = 'none';
                if (pollInterval) {
                    clearInterval(pollInterval);
                    pollInterval = null;
                }
                await fetchStandings();
                return;
            } else {
                searchContainer.style.display = 'block';
                if (!pollInterval) {
                    pollInterval = setInterval(fetchAllData, 5000);
                }
            }

            let selectedLeague = document.getElementById('leagueSelect').value;
            let searchQuery = document.getElementById('searchInput').value.toLowerCase().trim();
            
            let matchesToDisplay = [];
            let leaguesToFetch = selectedLeague === 'all_live' ? Object.keys(LEAGUES) : [selectedLeague];

            let yestStr = getDateString(-1);
            let todayStr = getDateString(0);
            let tomorrowStr = getDateString(1);

            for (let lSlug of leaguesToFetch) {
                try {
                    let [resYest, resToday, resTomorrow] = await Promise.all([
                        fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?dates=${yestStr}`),
                        fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?dates=${todayStr}`),
                        fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lSlug}/scoreboard?dates=${tomorrowStr}`)
                    ]);

                    let dataYest = resYest.ok ? await resYest.json() : { events: [] };
                    let dataToday = resToday.ok ? await resToday.json() : { events: [] };
                    let dataTomorrow = resTomorrow.ok ? await resTomorrow.json() : { events: [] };

                    let eventMap = {};
                    (dataYest.events || []).forEach(ev => eventMap[ev.id] = ev);
                    (dataToday.events || []).forEach(ev => eventMap[ev.id] = ev);
                    (dataTomorrow.events || []).forEach(ev => eventMap[ev.id] = ev);
                    let events = Object.values(eventMap);

                    for (let ev of events) {
                        let comp = ev.competitions[0];
                        let state = comp.status.type.state;
                        let leagueName = LEAGUES[lSlug] || lSlug;

                        if (searchQuery) {
                            if (ev.name.toLowerCase().includes(searchQuery)) {
                                matchesToDisplay.push({ leagueName, lSlug, event: ev });
                            }
                        } else if (selectedLeague === 'all_live') {
                            if (state === 'in' || comp.status.type.name === 'STATUS_HALFTIME') {
                                matchesToDisplay.push({ leagueName, lSlug, event: ev });
                            }
                        } else {
                            matchesToDisplay.push({ leagueName, lSlug, event: ev });
                        }
                    }
                } catch(e) {}
            }

            for (let item of matchesToDisplay) {
                await asyncizedFetchSummary(item.lSlug, item.event.id);
            }

            updateGlobalTicker();

            let mainContainer = document.getElementById('mainContainer');
            if (matchesToDisplay.length === 0) {
                mainContainer.innerHTML = "<div style='text-align:center; color:#94a3b8; padding:30px;'>Nenhuma partida encontrada no momento para esta seleção/filtro.</div>";
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

                let allDetails = [];
                if (competition.details) allDetails = allDetails.concat(competition.details);
                if (summary.details) allDetails = allDetails.concat(summary.details);
                if (summary.scoringPlays) {
                    for (let sp of summary.scoringPlays) {
                        allDetails.push({
                            type: { name: "goal", text: sp.type?.text || "Goal" },
                            clock: sp.clock,
                            team: sp.team,
                            athlete: sp.athlete,
                            athletesInvolved: sp.athletesInvolved
                        });
                    }
                }

                for (let d of allDetails) {
                    let text = (d.type && d.type.text) ? d.type.text.toLowerCase() : "";
                    let typeName = (d.type && d.type.name) ? d.type.name.toLowerCase() : "";
                    let isHome = d.team && d.team.id === homeTeamId;
                    let isAway = d.team && d.team.id === awayTeamId;

                    if (text.includes("yellow card") || text.includes("cartão amarelo") || typeName.includes("yellow") || typeName.includes("yellowcard")) {
                        if (isHome) hYellowCount++;
                        if (isAway) aYellowCount++;
                    }
                    if (text.includes("red card") || text.includes("cartão vermelho") || typeName.includes("red") || typeName.includes("redcard")) {
                        if (isHome) hRedCount++;
                        if (isAway) aRedCount++;

                        let player = "Jogador";
                        if (d.athlete && d.athlete.displayName) player = d.athlete.displayName;
                        else if (d.athletesInvolved && d.athletesInvolved[0] && d.athletesInvolved[0].displayName) player = d.athletesInvolved[0].displayName;

                        let clockVal = (d.clock && d.clock.displayValue) ? d.clock.displayValue : "";
                        let redStr = `🟥 <b>${player}</b> ${clockVal ? '(' + clockVal + "')" : ''}`;
                        if (isHome) {
                            if (!hRedCardsList.includes(redStr)) hRedCardsList.push(redStr);
                        } else if (isAway) {
                            if (!aRedCardsList.includes(redStr)) aRedCardsList.push(redStr);
                        }
                    }
                    
                    let isGoal = text.includes("goal") || text.includes("gol") || text.includes("penalty") || text.includes("pênalti") || text.includes("penal") || typeName.includes("goal") || typeName.includes("penalty") || d.scoringPlay === true;
                    
                    if (isGoal) {
                        let scorer = "Gol";
                        if (d.athlete && d.athlete.displayName) scorer = d.athlete.displayName;
                        else if (d.athletesInvolved && d.athletesInvolved[0] && d.athletesInvolved[0].displayName) scorer = d.athletesInvolved[0].displayName;
                        
                        let clockVal = (d.clock && d.clock.displayValue) ? d.clock.displayValue : "";
                        let isOwn = text.includes("own goal") || text.includes("contra");
                        let isPenalty = text.includes("penalty") || text.includes("pênalti") || text.includes("penal") || typeName.includes("penalty");
                        
                        let goalStr = `⚽ ${isPenalty ? '(Pên) ' : ''}<b>${scorer}${isOwn ? ' (Contra)' : ''}</b> ${clockVal ? '(' + clockVal + "')" : ''}`;
                        if (isHome) {
                            if (!hGoalsList.includes(goalStr)) hGoalsList.push(goalStr);
                        } else if (isAway) {
                            if (!aGoalsList.includes(goalStr)) aGoalsList.push(goalStr);
                        }
                    }
                }

                let matchKey = `${eventId}`;
                let scoreKey = `${homeScore}-${awayScore}`;
                if (previousScores[matchKey] && previousScores[matchKey] !== scoreKey) {
                    let [prevH, prevA] = previousScores[matchKey].split('-').map(Number);
                    let curH = parseInt(homeScore), curA = parseInt(awayScore);
                    
                    let scoringTeamName = curH > prevH ? homeTeam : awayTeam;
                    let scorerName = curH > prevH ? 
                        (hGoalsList.length > 0 ? hGoalsList[hGoalsList.length - 1].replace(/<\/?[^>]+(>|$)/g, "").replace(/^⚽\s*(\(Pên\)\s*)?/, "") : "Desconhecido") :
                        (aGoalsList.length > 0 ? aGoalsList[aGoalsList.length - 1].replace(/<\/?[^>]+(>|$)/g, "").replace(/^⚽\s*(\(Pên\)\s*)?/, "") : "Desconhecido");

                    triggerTopGoalAlert(scoringTeamName, scorerName, homeTeam, awayTeam, homeScore, awayScore);
                }
                previousScores[matchKey] = scoreKey;

                let state = competition.status.type.state;
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
                let hShotsOn = parseNum(hStats.shotsOnTarget || 0);
                let hShotsTot = parseNum(hStats.totalShots || 0);
                let hCorners = parseNum(hStats.wonCorners || 0);
                let hPoss = parseNum(hStats.possessionPct || 50);

                let aShotsOn = parseNum(aStats.shotsOnTarget || 0);
                let aShotsTot = parseNum(aStats.totalShots || 0);
                let aCorners = parseNum(aStats.wonCorners || 0);
                let aPoss = parseNum(aStats.possessionPct || 50);

                let hScorePress = (hShotsOn * 3.0) + (hShotsTot * 1.0) + (hCorners * 1.5) + (hPoss * 0.2);
                let aScorePress = (aShotsOn * 3.0) + (aShotsTot * 1.0) + (aCorners * 1.5) + (aPoss * 0.2);
                let totalPress = hScorePress + aScorePress;
                let hPct = totalPress === 0 ? 50 : Math.round((hScorePress / totalPress) * 100);
                let aPct = 100 - hPct;

                let getBarColor = (pct) => pct > 65 ? "#22c55e" : (pct > 51 ? "#f97316" : (pct >= 35 ? "#ffffff" : "#ef4444"));
                let getBarLabel = (pct) => pct > 65 ? "Pressão Alta" : (pct > 51 ? "Pressão Moderada" : (pct >= 35 ? "Neutro" : "Defensiva / Baixa"));

                let hGoalsHtml = hGoalsList.length > 0 ? `<div style="text-align:right; font-size:11px; color:#facc15; margin-bottom:4px;">${hGoalsList.join("<br>")}</div>` : '';
                let hRedCardsHtml = hRedCardsList.length > 0 ? `<div style="text-align:right; font-size:11px; color:#facc15; margin-bottom:4px;">${hRedCardsList.join("<br>")}</div>` : '';

                let aGoalsHtml = aGoalsList.length > 0 ? `<div style="text-align:left; font-size:11px; color:#facc15; margin-bottom:4px;">${aGoalsList.join("<br>")}</div>` : '';
                let aRedCardsHtml = aRedCardsList.length > 0 ? `<div style="text-align:left; font-size:11px; color:#facc15; margin-bottom:4px;">${aRedCardsList.join("<br>")}</div>` : '';

                let centerBadge = "";
                let isHalftime = (statusName === 'STATUS_HALFTIME' || rawDetail.toLowerCase().includes('halftime') || rawDetail.toLowerCase().includes('intervalo'));

                if (isHalftime) {
                    centerBadge = `
                        <div>
                            <span class="badge-halftime">⏸️ INTERVALO</span>
                            <div style="margin:6px 0;"><h2 class="score-box" style="margin:0;">${homeScore} x ${awayScore}</h2></div>
                        </div>
                    `;
                } else if (state === 'in') {
                    let pName = period === 1 ? "1º Tempo" : (period === 2 ? "2º Tempo" : (period >= 3 ? "Prorrogação/Pênaltis" : `Tempo ${period}`));
                    let clockDisp = displayClock ? ` (${displayClock}')` : ` (${rawDetail})`;
                    centerBadge = `
                        <div>
                            <span class="badge-live"><span class="blinking-dot"></span>AO VIVO • ${pName}${clockDisp}</span>
                            <div style="margin:6px 0;"><h2 class="score-box" style="margin:0;">${homeScore} x ${awayScore}</h2></div>
                        </div>
                    `;
                } else if (state === 'post') {
                    centerBadge = `
                        <div>
                            <span class="badge-post">ENCERRADO</span>
                            <h2 style="color:#fff; margin:6px 0;">${homeScore} x ${awayScore}</h2>
                        </div>
                    `;
                } else {
                    centerBadge = `
                        <div>
                            <span class="badge-pre">🕒 ${kickoff}</span>
                            <div class="venue-text">📍 ${venueName}</div>
                            <h3 style="color:#94a3b8; margin:4px 0;">vs</h3>
                        </div>
                    `;
                }

                let isOpen = openStates[eventId] ? 'open' : '';
                let possH = hStats.possessionPct || "0%"; if(!possH.includes("%") && possH !== "0") possH += "%";
                let possA = aStats.possessionPct || "0%"; if(!possA.includes("%") && possA !== "0") possA += "%";

                let statsInnerHtml = `
                    <p style='text-align: right;'><b>${possH}</b><br>${hStats.shotsOnTarget || '0'}<br>${hStats.totalShots || '0'}<br>${hStats.wonCorners || '0'}<br>${hStats.foulsCommitted || hStats.fouls || '0'}<br><span class="yellow-card">🟨 ${hYellowCount}</span><br><span class="red-card">🟥 ${hRedCount}</span></p>
                    <p style='text-align: center; color: #94a3b8;'>Posse de Bola<br>Chutes no Gol<br>Chutes Totais<br>Escanteios<br>Faltas Cometidas<br>Cartões Amarelos<br>Cartões Vermelhos</p>
                    <p style='text-align: left;'><b>${possA}</b><br>${aStats.shotsOnTarget || '0'}<br>${aStats.totalShots || '0'}<br>${aStats.wonCorners || '0'}<br>${aStats.foulsCommitted || aStats.fouls || '0'}<br><span class="yellow-card">🟨 ${aYellowCount}</span><br><span class="red-card">🟥 ${aRedCount}</span></p>
                `;

                html += `
                    <div class="card">
                        <div class="header-league">🏆 Campeonato: ${lName}</div>
                        <div class="match-grid">
                            <div>
                                ${hGoalsHtml}
                                ${hRedCardsHtml}
                                <div class="team-home">${homeTeam}</div>
                                <div style="text-align:right; margin-top:6px;">
                                    <span class="pressure-label" style="color: ${getBarColor(hPct)};">${getBarLabel(hPct)} (${hPct}%)</span>
                                    <div class="pressure-track"><div class="pressure-fill" style="background-color: ${getBarColor(hPct)}; width: ${hPct}%;"></div></div>
                                </div>
                            </div>
                            <div class="center-info">
                                ${centerBadge}
                            </div>
                            <div>
                                ${aGoalsHtml}
                                ${aRedCardsHtml}
                                <div class="team-away">${awayTeam}</div>
                                <div style="text-align:left; margin-top:6px;">
                                    <span class="pressure-label" style="color: ${getBarColor(aPct)};">${getBarLabel(aPct)} (${aPct}%)</span>
                                    <div class="pressure-track"><div class="pressure-fill" style="background-color: ${getBarColor(aPct)}; width: ${aPct}%;"></div></div>
                                </div>
                            </div>
                        </div>

                        <details data-event-id="${eventId}" ${isOpen} ontoggle="openStates['${eventId}'] = this.open;">
                            <summary>📊 Ver Estatísticas Detalhadas (${homeTeam} vs ${awayTeam})</summary>
                            <div id="stats_${eventId}" class="stats-grid">
                                ${statsInnerHtml}
                            </div>
                        </details>
                    </div>
                `;
            }

            mainContainer.innerHTML = html;
        }

        document.getElementById('viewSelect').addEventListener('change', fetchAllData);
        document.getElementById('leagueSelect').addEventListener('change', () => {
            currentLoadedStandingsKey = "";
            fetchAllData();
        });
        document.getElementById('searchInput').addEventListener('input', fetchAllData);

        fetchAllData();
        pollInterval = setInterval(fetchAllData, 5000);
    </script>
</body>
</html>
"""

st.components.v1.html(dashboard_html, height=1200, scrolling=True)
