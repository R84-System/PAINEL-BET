// ==========================================
// PAINEL AO VIVO - FUTEBOL & TERMÔMETRO DE PRESSÃO
// ==========================================

// Configuração global de áudio e estado
let audioAlertEnabled = true;
let lastProcessedEventId = null;
let previousScoreHome = null;
let previousScoreAway = null;

// Elementos de som (Sintetizador Web Audio API para alertas e gols)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playGoalSound() {
    if (!audioAlertEnabled) return;
    try {
        if (audioCtx.state === 'suspended') audioCtx.resume();
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(440, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.6);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.6);
    } catch (e) {
        console.error("Erro ao reproduzir som de gol:", e);
    }
}

function playAlertSound() {
    if (!audioAlertEnabled) return;
    try {
        if (audioCtx.state === 'suspended') audioCtx.resume();
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
        gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.2);
    } catch (e) {
        console.error("Erro ao reproduzir alerta:", e);
    }
}

// Utilitário para conversão segura de números
function parseNum(val) {
    let n = parseFloat(val);
    return isNaN(n) ? 0 : n;
}

// ==========================================
// PROCESSAMENTO DE ESTATÍSTICAS E DEFESAS
// ==========================================
function processMatchStats(boxscoreData) {
    if (!boxscoreData || !boxscoreData.teams || boxscoreData.teams.length < 2) return null;

    const homeTeamStats = boxscoreData.teams[0].statistics || [];
    const awayTeamStats = boxscoreData.teams[1].statistics || [];

    let hStats = {};
    let aStats = {};

    homeTeamStats.forEach(stat => {
        hStats[stat.name || stat.key] = stat.displayValue || stat.value;
    });

    awayTeamStats.forEach(stat => {
        aStats[stat.name || stat.key] = stat.displayValue || stat.value;
    });

    // Captura de Defesas (Saves) com suporte a múltiplos nomes de campos da API
    let hSaves = parseNum(hStats.saves || hStats.defesas || hStats.goalkeeperSaves || 0);
    let aSaves = parseNum(aStats.saves || aStats.defesas || aStats.goalkeeperSaves || 0);

    let hShotsOn = parseNum(hStats.shotsOnTarget || hStats.chutesNoGol || 0);
    let aShotsOn = parseNum(aStats.shotsOnTarget || aStats.chutesNoGol || 0);

    let hShotsTot = parseNum(hStats.totalShots || hStats.chutesTotais || 0);
    let aShotsTot = parseNum(aStats.totalShots || aStats.chutesTotais || 0);

    let hCorners = parseNum(hStats.wonCorners || hStats.escanteios || 0);
    let aCorners = parseNum(aStats.wonCorners || aStats.escanteios || 0);

    let hPoss = parseNum(hStats.possessionPct || hStats.posse || 50);
    let aPoss = parseNum(aStats.possessionPct || aStats.posse || 50);

    return {
        hSaves, aSaves,
        hShotsOn, aShotsOn,
        hShotsTot, aShotsTot,
        hCorners, aCorners,
        hPoss, aPoss
    };
}

// ==========================================
// CÁLCULO DO TERMÔMETRO DE PRESSÃO
// ==========================================
function calculatePressureThermometer(matchData, statsData, currentPeriod) {
    let hScorePress = 50;
    let aScorePress = 50;

    // Se estiver no primeiro tempo ou usando base estatística geral de boxscore
    if (statsData) {
        // Pesos refinados: Chutes no gol (3.0), Chutes Totais (1.0), Escanteios (1.5), Posse (0.2), Defesas do Goleiro Adversário (1.5)
        hScorePress = (statsData.hShotsOn * 3.0) + (statsData.hShotsTot * 1.0) + (statsData.hCorners * 1.5) + (statsData.hPoss * 0.2) + (statsData.aSaves * 1.5);
        aScorePress = (statsData.aShotsOn * 3.0) + (statsData.aShotsTot * 1.0) + (statsData.aCorners * 1.5) + (statsData.aPoss * 0.2) + (statsData.hSaves * 1.5);
    }

    // Se houver eventos dinâmicos recentes no segundo tempo, ajusta com base na linha do tempo
    const events = matchData.details || matchData.plays || [];
    if (events.length > 0) {
        let recentEvents = events.slice(-10); // Últimos 10 eventos para forte dinamismo
        let liveHBonus = 0;
        let liveABonus = 0;

        recentEvents.forEach(ev => {
            const teamId = ev.team?.id;
            const isHome = teamId === matchData.competitors?.[0]?.team?.id;
            const textEv = (ev.text || ev.type?.text || '').toLowerCase();

            let weight = 0;
            if (textEv.includes('goal') || textEv.includes('gol')) weight = 6.0;
            else if (textEv.includes('yellow') || textEv.includes('cartão amarelo')) weight = -1.0;
            else if (textEv.includes('red') || textEv.includes('vermelho')) weight = -3.0;
            else if (textEv.includes('shot') || textEv.includes('chute') || textEv.includes('finalização')) weight = 2.0;
            else if (textEv.includes('corner') || textEv.includes('escanteio')) weight = 1.5;

            if (isHome) liveHBonus += weight;
            else liveABonus += weight;
        });

        hScorePress += liveHBonus;
        aScorePress += liveABonus;
    }

    // Normalização para percentual 0-100%
    let total = hScorePress + aScorePress;
    if (total <= 0) return { homePct: 50, awayPct: 50 };

    let homePct = Math.round((hScorePress / total) * 100);
    let awayPct = 100 - homePct;

    return { homePct, awayPct };
}

// ==========================================
// ESCALAÇÕES E SUBSTITUIÇÕES AO VIVO
// ==========================================
function renderLineupsAndSubs(matchData) {
    const homeTeam = matchData.competitors?.[0];
    const awayTeam = matchData.competitors?.[1];
    
    const events = matchData.details || matchData.plays || [];
    
    // Filtro cirúrgico para capturar eventos de substituição ("Entrou X, Saiu Y")
    const substitutions = events.filter(ev => {
        const txt = (ev.text || ev.type?.text || '').toLowerCase();
        return txt.includes('substitution') || txt.includes('substituição') || txt.includes('substitution') || txt.includes('entra') || txt.includes('sai');
    });

    let subsHtml = substitutions.length > 0 ? substitutions.map(sub => {
        const timeDisplay = sub.clock?.displayValue || sub.minute || '⏱️';
        const teamName = sub.team?.displayName || '';
        const subText = sub.text || 'Substituição realizada';
        return `
            <div class="sub-event-item" style="display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 13px;">
                <span style="background: rgba(74, 222, 128, 0.15); color: #4ade80; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-family: monospace;">${timeDisplay}'</span>
                <div style="color: #f1f5f9; flex: 1;">
                    <span style="color: #38bdf8; font-weight: 600; margin-right: 4px;">[${teamName}]</span>
                    <span>🔄 ${subText}</span>
                </div>
            </div>
        `;
    }).join('') : '<div style="color: #94a3b8; font-size: 13px; font-style: italic; padding: 8px 0;">Nenhuma alteração registrada até o momento.</div>';

    return `
        <div class="live-lineups-container" style="margin-top: 20px; background: rgba(15, 23, 42, 0.7); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(8px);">
            <h3 style="color: #f8fafc; font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                <span>🔄</span> Alterações e Substituições em Tempo Real
            </h3>
            <div class="sub-list" style="max-height: 200px; overflow-y: auto; margin-bottom: 18px; padding-right: 4px;">
                ${subsHtml}
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
                <div class="team-roster-home" style="background: rgba(30, 41, 59, 0.5); padding: 10px; border-radius: 8px;">
                    <h4 style="color: #38bdf8; font-size: 13px; margin-bottom: 8px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${homeTeam?.team?.displayName || 'Time Casa'}
                    </h4>
                    <div style="font-size: 12px; color: #cbd5e1; max-height: 160px; overflow-y: auto;">
                        ${renderRosterList(homeTeam?.roster || homeTeam?.athletes)}
                    </div>
                </div>
                
                <div class="team-roster-away" style="background: rgba(30, 41, 59, 0.5); padding: 10px; border-radius: 8px;">
                    <h4 style="color: #f43f5e; font-size: 13px; margin-bottom: 8px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${awayTeam?.team?.displayName || 'Time Visitante'}
                    </h4>
                    <div style="font-size: 12px; color: #cbd5e1; max-height: 160px; overflow-y: auto;">
                        ${renderRosterList(awayTeam?.roster || awayTeam?.athletes)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderRosterList(roster) {
    if (!roster || roster.length === 0) return '<span style="color: #64748b; font-style: italic;">Escalação não divulgada</span>';
    return roster.map(player => `
        <div style="padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.03); display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="color: #94a3b8; font-weight: bold; margin-right: 6px; font-family: monospace;">#${player.jersey || player.shirtNumber || ''}</span>
                <span style="color: #e2e8f0;">${player.athlete?.displayName || player.name || player.fullName || 'Atleta'}</span>
            </div>
            <span style="font-size: 10px; color: #64748b; background: rgba(255,255,255,0.05); padding: 1px 4px; border-radius: 3px;">${player.position?.abbreviation || player.pos || ''}</span>
        </div>
    `).join('');
}

// ==========================================
// RENDERIZAÇÃO COMPLETA DO PAINEL DE ESTATÍSTICAS E PLACAR
// ==========================================
function updateMatchDashboard(matchData) {
    const stats = processMatchStats(matchData);
    const pressure = calculatePressureThermometer(matchData, stats, matchData.status?.type?.detail);

    // Verificação de alteração de placar para banner de gol e som
    const currentHomeScore = parseNum(matchData.homeScore);
    const currentAwayScore = parseNum(matchData.awayScore);

    if (previousScoreHome !== null && previousScoreAway !== null) {
        if (currentHomeScore > previousScoreHome || currentAwayScore > previousScoreAway) {
            playGoalSound();
            triggerGoalBanner(matchData);
        }
    }
    previousScoreHome = currentHomeScore;
    previousScoreAway = currentAwayScore;

    // Renderização visual das defesas na interface de estatísticas
    const savesHome = stats ? stats.hSaves : 0;
    const savesAway = stats ? stats.aSaves : 0;

    console.log(`Estatísticas atualizadas - Defesas Casa: ${savesHome} | Defesas Visitante: ${savesAway}`);
    console.log(`Termômetro de Pressão - Casa: ${pressure.homePct}% | Visitante: ${pressure.awayPct}%`);

    // Injeção opcional do bloco de substituições e escalações no DOM se o container existir
    const container = document.getElementById('match-extended-stats-container');
    if (container) {
        container.innerHTML = renderLineupsAndSubs(matchData);
    }
}

function triggerGoalBanner(matchData) {
    let banner = document.getElementById('goal-alert-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'goal-alert-banner';
        banner.style.cssText = "position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 14px 28px; border-radius: 12px; font-weight: bold; font-size: 18px; z-index: 9999; box-shadow: 0 10px 25px rgba(0,0,0,0.4); animation: bounceIn 0.5s ease;";
        document.body.appendChild(banner);
    }
    banner.innerHTML = `⚽ GOOOOOOL! Placar atualizado!`;
    banner.style.display = 'block';
    setTimeout(() => {
        banner.style.display = 'none';
    }, 4000);
}
