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
        @keyframes goalFlash {
            0% { background-color: #22c55e; transform: scale(1.05); color: #000; }
            50% { background-color: #facc15; transform: scale(1.08); color: #000; }
            100% { background-color: transparent; transform: scale(1); color: inherit; }
        }
        .goal-alert {
            animation: goalFlash 2s ease-in-out;
            border-radius: 6px;
            padding: 2px 8px;
            display: inline-block;
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
        .goals-container {
            text-align: center;
            font-size: 11px;
            color: #facc15;
            margin-top: 8px;
            background: rgba(250, 204, 21, 0.1);
            padding: 6px;
            border-radius: 6px;
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
        .pressure-bar-container {
            margin-top: 6px;
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
    </style>
</head>
<body>

    <h2 style="margin-top:0; margin-bottom:12px; display:flex; align-items:center; gap:10px;">
        ⚽ Painel Pro de Futebol ao Vivo
    </h2>

    <div class="ticker-bar" id="tickerContainer" style="display:none;">
        <div class="ticker-title">🟢 TICKER AO VIVO (GLOBAL) - PLACAR EM TEMPO REAL</div>
        <div class="ticker-wrap">
            <div class="ticker-move" id="tickerContent"></div>
        </div>
    </div>

    <div class="controls">
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
        <div style="flex-grow: 1;">
            <label style="font-size:12px; color:#94a3b8; display:block; margin-bottom:4px;">Buscar Time</label>
            <input type="text" id="searchInput" placeholder="Ex: Flamengo, Real Madrid, Goiás...">
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
        let openStates = {};

        function formatDateBrasilia(dateStr) {
            if (!dateStr) return "Em breve";
            try {
                let dt = new Date(dateStr);
                return dt.toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
            } catch(e) { return "Horário a confirmar"; }
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

        async function fetchAllData() {
            let selectedLeague = document.getElementById('leagueSelect').value;
            let searchQuery = document.getElementById('searchInput').value.toLowerCase().trim();
            
            let matchesToDisplay = [];
            let leaguesToFetch = selectedLeague === 'all_live' ? Object.keys(LEAGUES) : [selectedLeague];

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

                let matchKey = `${eventId}`;
                let scoreKey = `${homeScore}-${awayScore}`;
                let isGoalAlert = false;
                if (previousScores[matchKey] && previousScores[matchKey] !== scoreKey) {
                    isGoalAlert = true;
                }
                previousScores[matchKey] = scoreKey;

                let state = competition.status.type.state;
                let statusName = competition.status.type.name || "";
                let rawDetail = competition.status.type.detail || "";
                let displayClock = competition.status.displayClock || "";
                let period = competition.status.period || 1;
                let venueName = competition.venue ? competition.venue.fullName : "Local não informado";
                let kickoff = formatDateBrasilia(ev.date);

                let summary = summariesCache[`${lSlug}_${eventId}`] || {};
                
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

                let getBarColor = (pct) => pct >= 65 ? "#22c55e" : (pct >= 35 ? "#ffffff" : "#ef4444");
                let getBarLabel = (pct) => pct >= 65 ? "🔥 Pressão Alta" : (pct >= 35 ? "⚖️ Neutro" : "🛡️ Defensiva / Baixa");

                let hYellowCount = 0, aYellowCount = 0;
                let hRedCount = 0, aRedCount = 0;
                let goalsHtmlList = [];

                // Unificar fontes de detalhes (Scoreboard details + Summary scoringPlays / details)
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
                    }
                    if (text.includes("goal") || text.includes("gol") || typeName.includes("goal")) {
                        let scorer = "Gol";
                        if (d.athlete && d.athlete.displayName) scorer = d.athlete.displayName;
                        else if (d.athletesInvolved && d.athletesInvolved[0] && d.athletesInvolved[0].displayName) scorer = d.athletesInvolved[0].displayName;
                        
                        let clockVal = (d.clock && d.clock.displayValue) ? d.clock.displayValue : "";
                        let isOwn = text.includes("own goal") || text.includes("contra");
                        
                        let goalStr = `⚽ <b>${scorer}${isOwn ? ' (Contra)' : ''}</b> ${clockVal ? '(' + clockVal + "')" : ''}`;
                        if (!goalsHtmlList.includes(goalStr)) {
                            goalsHtmlList.push(goalStr);
                        }
                    }
                }

                let hBadges = `<div style="text-align:right; margin-bottom:4px; display:flex; justify-content:flex-end; gap:4px;">
                    <span class="yellow-card">🟨 ${hYellowCount}</span>
                    <span class="red-card">🟥 ${hRedCount}</span>
                </div>`;

                let aBadges = `<div style="text-align:left; margin-bottom:4px; display:flex; justify-content:flex-start; gap:4px;">
                    <span class="yellow-card">🟨 ${aYellowCount}</span>
                    <span class="red-card">🟥 ${aRedCount}</span>
                </div>`;

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
                    let scClass = isGoalAlert ? "goal-alert" : "";
                    centerBadge = `
                        <div>
                            <span class="badge-live"><span class="blinking-dot"></span>AO VIVO • ${pName}${clockDisp}</span>
                            <div style="margin:6px 0;"><h2 class="score-box ${scClass}" style="margin:0;">${homeScore} x ${awayScore}</h2></div>
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

                let goalsHtml = goalsHtmlList.length > 0 ? `<div class="goals-container"><b>Gols:</b> ${goalsHtmlList.join(" | ")}</div>` : '';

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
                                ${hBadges}
                                <div class="team-home">${homeTeam}</div>
                                <div style="text-align:right; margin-top:6px;">
                                    <span class="pressure-label" style="color: ${getBarColor(hPct)};">${getBarLabel(hPct)} (${hPct}%)</span>
                                    <div class="pressure-track"><div class="pressure-fill" style="background-color: ${getBarColor(hPct)}; width: ${hPct}%;"></div></div>
                                </div>
                            </div>
                            <div class="center-info">
                                ${centerBadge}
                                ${goalsHtml}
                            </div>
                            <div>
                                ${aBadges}
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

        document.getElementById('leagueSelect').addEventListener('change', fetchAllData);
        document.getElementById('searchInput').addEventListener('input', fetchAllData);

        fetchAllData();
        setInterval(fetchAllData, 2000);
    </script>
</body>
</html>
"""

st.title("⚽ Painel Pro de Futebol ao Vivo")
st.components.v1.html(dashboard_html, height=1200, scrolling=True)
