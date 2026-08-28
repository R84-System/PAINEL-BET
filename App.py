from datetime import datetime
import pytz
import requests
import streamlit as st

st.set_page_config(
    page_title="Painel Pro de Futebol", page_icon="⚽", layout="wide"
)

# CSS avançado para animações, alerta de gol e otimização visual sem piscar excessivamente
st.markdown(
    """
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
@keyframes goalFlash {
    0% { background-color: #22c55e; transform: scale(1.08); color: #000; }
    50% { background-color: #facc15; transform: scale(1.12); color: #000; }
    100% { background-color: transparent; transform: scale(1); color: inherit; }
}
.goal-alert {
    animation: goalFlash 2s ease-in-out;
    border-radius: 6px;
    padding: 2px 8px;
    display: inline-block;
}
</style>
""",
    unsafe_allow_html=True,
)

# Mapeamento completo de Ligas, Copas e Internacionais com slugs oficiais da ESPN
LEAGUES = {
    "🟢 Todos os Jogos ao Vivo (Global)": "all_live",
    "🇧🇷 Brasileirão Série A": "bra.1",
    "🇧🇷 Brasileirão Série B": "bra.2",
    "🇧🇷 Copa do Brasil": "bra.copa_brasil",
    "🌎 Copa Libertadores": "conmebol.libertadores",
    "🌎 Copa Sudamericana (Sul-Americana)": "conmebol.sudamericana",
    "🇪🇺 Champions League": "uefa.champions",
    "🇪🇺 Europa League": "uefa.europa",
    "🇪🇺 Super Cup (UEFA)": "uefa.super_cup",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "eng.1",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 FA Cup (Copa da Inglaterra)": "eng.fa",
    "🇪🇸 La Liga": "esp.1",
    "🇪🇸 Copa del Rey": "esp.copa_del_rey",
    "🇮🇹 Serie A (Itália)": "ita.1",
    "🇮🇹 Coppa Italia": "ita.coppa_italia",
    "🇩🇪 Bundesliga": "ger.1",
    "🇩🇪 DFB Pokal": "ger.dfb_pokal",
    "🇫🇷 Ligue 1": "fra.1",
    "🇫🇷 Coupe de France": "fra.coupe_de_france",
    "🇵🇹 Primeira Liga": "por.1",
    "🇸🇦 Saudi Pro League": "ksa.1",
    "🇦🇷 Liga Profesional (Argentina)": "arg.1",
    "🇲🇽 Campeonato Mexicano (Liga MX)": "mex.1",
    "🇨🇴 Campeonato Colombiano": "col.1",
    "🇪🇨 Campeonato do Equador": "ecu.1",
    "🇨🇱 Liga Chilena": "chi.1",
    "🇳🇱 Eredivisie": "ned.1",
    "🇺🇸 MLS": "usa.1",
    "🇨🇳 Liga Chinesa": "chn.1",
    "🇯🇵 Liga Japonesa (J1)": "jpn.1",
    "🇰🇷 Liga Coreana (K League)": "kor.1",
    "🌍 Jogos Internacionais / Seleções (FIFA)": "fifa.friendly",
}


@st.cache_data(ttl=2)
def fetch_espn_matches(slug):
  url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
  try:
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      return res.json().get("events", [])
    return []
  except Exception:
    return []


@st.cache_data(ttl=2)
def fetch_match_summary(slug, event_id):
  url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/summary?event={event_id}"
  try:
    res = requests.get(url, timeout=3)
    if res.status_code == 200:
      return res.json()
    return {}
  except Exception:
    return {}


def format_datetime_brasilia(date_str):
  if not date_str:
    return "Em breve"
  try:
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    fuso_brasilia = pytz.timezone("America/Sao_Paulo")
    dt_br = dt.astimezone(fuso_brasilia)

    dias_semana = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }
    dia_pt = dias_semana.get(dt_br.strftime("%A"), dt_br.strftime("%A"))
    return (
        f"{dia_pt}, {dt_br.strftime('%d/%m')} às {dt_br.strftime('%I:%M %p')}"
    )
  except Exception:
    return "Horário a confirmar"


def extract_venue(event):
  try:
    competition = event.get("competitions", [{}])[0]
    venue = competition.get("venue", {})
    v_name = venue.get("fullName", "")
    address = venue.get("address", {})
    city = address.get("city", "")
    country = address.get("country", "")

    loc_parts = []
    if v_name:
      loc_parts.append(v_name)
    if city:
      loc_parts.append(city)
    if country and country != "Brazil":
      loc_parts.append(country)

    return " - ".join(loc_parts) if loc_parts else "Local não informado"
  except Exception:
    return "Local não informado"


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
  home_players, away_players = [], []
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


def extract_goals(summary_data):
  """Extrai os autores dos gols, tempo e time usando scoringPlays e details da API."""
  goals_list = []
  scoring_plays = summary_data.get("scoringPlays", [])

  if scoring_plays:
    for play in scoring_plays:
      clock = play.get("clock", {}).get("displayValue", "")
      text = play.get("text", "")
      athletes = play.get("athletesInvolved", [])
      scorer = athletes[0].get("displayName", "Gol") if athletes else "Gol"
      team = play.get("team", {}).get("displayName", "")
      is_own_goal = "own goal" in text.lower() or "contra" in text.lower()
      goals_list.append({
          "scorer": f"{scorer} (Contra)" if is_own_goal else scorer,
          "clock": clock,
          "team": team,
      })
  else:
    details = summary_data.get("details", [])
    for item in details:
      text = str(item.get("type", {}).get("text", "")).lower()
      if "goal" in text or "gol" in text:
        athlete = item.get("athlete", {})
        scorer = athlete.get("displayName", "Gol")
        clock = item.get("clock", {}).get("displayValue", "")
        team = item.get("team", {}).get("displayName", "")
        is_own_goal = (
            "own goal" in text or "contra" in text or "gol contra" in text
        )
        goals_list.append({
            "scorer": f"{scorer} (Contra)" if is_own_goal else scorer,
            "clock": clock,
            "team": team,
        })
  return goals_list


def calculate_pressure(home_stats, away_stats):
  def parse_num(val):
    try:
      return float(str(val).replace("%", "").strip())
    except ValueError:
      return 0.0

  h_score = (
      (parse_num(home_stats.get("shotsOnTarget", 0)) * 3.0)
      + (parse_num(home_stats.get("totalShots", 0)) * 1.0)
      + (parse_num(home_stats.get("wonCorners", 0)) * 1.5)
      + (parse_num(home_stats.get("possessionPct", 50)) * 0.2)
  )

  a_score = (
      (parse_num(away_stats.get("shotsOnTarget", 0)) * 3.0)
      + (parse_num(away_stats.get("totalShots", 0)) * 1.0)
      + (parse_num(away_stats.get("wonCorners", 0)) * 1.5)
      + (parse_num(away_stats.get("possessionPct", 50)) * 0.2)
  )

  total = h_score + a_score
  if total == 0:
    return 50, 50

  h_pct = int(round((h_score / total) * 100))
  return h_pct, 100 - h_pct


def get_custom_bar(percentage, side):
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


def render_live_ticker():
  """Ticker ao vivo sincronizado com dados em tempo real, sem fundo branco e relógio alinhado."""
  ticker_matches = []
  for l_name, l_slug in LEAGUES.items():
    if l_slug == "all_live":
      continue
    events = fetch_espn_matches(l_slug)
    for ev in events:
      comp = ev.get("competitions", [{}])[0]
      state = comp.get("status", {}).get("type", {}).get("state")
      if state == "in":
        competitors = comp.get("competitors", [])
        h_team, a_team, h_score, a_score = "Casa", "Fora", "0", "0"
        for c in competitors:
          if c.get("homeAway") == "home":
            h_team = c.get("team", {}).get(
                "shortDisplayName",
                c.get("team", {}).get("displayName", "Casa"),
            )
            h_score = c.get("score", "0")
          else:
            a_team = c.get("team", {}).get(
                "shortDisplayName",
                c.get("team", {}).get("displayName", "Fora"),
            )
            a_score = c.get("score", "0")
        clock = comp.get("status", {}).get("displayClock", "")
        item_html = (
            f"⚽ <span style='color: #facc15; font-weight: 900;'>{h_team}</span>"
            f" &nbsp;<span style='color: #000000; background-color: #f8fafc; padding:"
            f" 2px 6px; border-radius: 4px;'><b>{h_score} x {a_score}</b></span>"
            f"&nbsp; <span style='color: #facc15; font-weight:"
            f" 900;'>{a_team}</span> &nbsp;({clock})"
        )
        ticker_matches.append(item_html)

  if ticker_matches:
    content = " &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; ".join(ticker_matches)
    st.markdown(
        f"""
        <div style="background-color: transparent; padding: 4px 0px 8px 0px; border-bottom: 1px solid #334155; margin-bottom: 15px;">
            <div style="font-size: 11px; color: #22c55e; font-weight: bold; margin-bottom: 4px;">🟢 TICKER AO VIVO (GLOBAL) - PLACAR EM TEMPO REAL</div>
            <marquee behavior="scroll" direction="left" scrollamount="4" style="color: #ffffff; font-weight: bold; font-size: 14px;">
                {content}
            </marquee>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- RENDERIZA O TICKER NO TOPO ---
render_live_ticker()

st.title("⚽ Painel Pro de Futebol ao Vivo")

st.sidebar.title("⚙️ Configurações")
selected_league_name = st.sidebar.selectbox("Campeonato", list(LEAGUES.keys()))
league_slug = LEAGUES[selected_league_name]

search_query = st.text_input(
    "🔍 Buscar time (ex: Flamengo, Real Madrid, Al Nassr...)", ""
).strip().lower()

# Inicializa o estado dos placares para detecção de gols
if "previous_scores" not in st.session_state:
  st.session_state.previous_scores = {}


@st.fragment(run_every=2)
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
    st.markdown("### 🟢 Todos os Jogos Ao Vivo no Mundo")
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
    st.info(
        "Nenhuma partida encontrada no momento para esta seleção/filtro."
    )
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

    match_key = f"{event_id}"
    score_key = f"{home_score}-{away_score}"
    is_goal_alert = False

    if match_key in st.session_state.previous_scores:
      old_score = st.session_state.previous_scores[match_key]
      if old_score != score_key:
        is_goal_alert = True
    st.session_state.previous_scores[match_key] = score_key

    status_type = competition.get("status", {}).get("type", {})
    state = status_type.get("state", "pre")
    raw_detail = status_type.get("detail", "")
    event_date = event.get("date", "")

    formatted_kickoff = format_datetime_brasilia(event_date)
    venue_name = extract_venue(event)

    status_obj = competition.get("status", {})
    display_clock = status_obj.get("displayClock", "")
    period = status_obj.get("period", 1)

    summary = fetch_match_summary(l_slug, event_id)
    stats = extract_stats(summary)
    h_red_players, a_red_players = extract_red_cards(
        summary, home_team_id, away_team_id
    )
    match_goals = extract_goals(summary)

    h_press, a_press = calculate_pressure(stats["home"], stats["away"])

    if query or slug == "all_live":
      st.caption(f"🏆 Campeonato: **{l_name}**")

    h_red_badge = (
        f"<div style='text-align: right; margin-bottom: 2px;'><span"
        f" style='background-color: #ef4444; color: white; padding: 1px 6px;"
        f" border-radius: 4px; font-size: 10px; font-weight: bold;'>🟥"
        f" EXPULSO ({len(h_red_players)})</span></div>"
        if h_red_players
        else ""
    )
    a_red_badge = (
        f"<div style='text-align: left; margin-bottom: 2px;'><span"
        f" style='background-color: #ef4444; color: white; padding: 1px 6px;"
        f" border-radius: 4px; font-size: 10px; font-weight: bold;'>🟥"
        f" EXPULSO ({len(a_red_players)})</span></div>"
        if a_red_players
        else ""
    )

    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
      st.markdown(h_red_badge, unsafe_allow_html=True)
      st.markdown(
          f"<h3 style='text-align: right; color: #fff; margin-top: 0;"
          f" margin-bottom: 0;'>{home_team}</h3>",
          unsafe_allow_html=True,
      )
      st.markdown(get_custom_bar(h_press, "home"), unsafe_allow_html=True)

    with col2:
      if state == "in":
        if period == 1:
          period_name = "1º Tempo"
        elif period == 2:
          period_name = "2º Tempo"
        elif period in [3, 4]:
          period_name = "Prorrogação"
        elif (
            period >= 5
            or "pen" in raw_detail.lower()
            or "pênalt" in raw_detail.lower()
        ):
          period_name = "Pênaltis"
        else:
          period_name = f"Tempo {period}"

        clock_display = (
            f" ({display_clock})" if display_clock else f" ({raw_detail})"
        )
        score_html_class = "goal-alert" if is_goal_alert else ""

        st.markdown(
            f"""
                <div style='text-align: center;'>
                    <span style='background-color:#1e293b; color:white; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:bold; border: 1px solid #334155;'>
                        <span class="blinking-dot"></span>AO VIVO • {period_name}{clock_display}
                    </span>
                    <div style='margin:6px 0;'><h2 class='{score_html_class}' style='color:#fff; margin:0; display:inline-block;'>{home_score} x {away_score}</h2></div>
                </div>
                """,
            unsafe_allow_html=True,
        )

        if match_goals:
          goals_html = " | ".join([
              f"⚽ <b>{g['scorer']}</b> ({g['clock']})" for g in match_goals
          ])
          st.markdown(
              f"""
                    <div style='text-align: center; font-size: 11px; color: #facc15; margin-top: 4px; background: rgba(250, 204, 21, 0.1); padding: 3px; border-radius: 4px;'>
                        <b>Gols:</b> {goals_html}
                    </div>
                    """,
              unsafe_allow_html=True,
          )

      elif state == "post":
        st.markdown(
            f"""
                <div style='text-align: center;'>
                    <span style='color:#94a3b8; font-weight:bold;'>ENCERRADO</span>
                    <h2 style='color:#fff; margin:6px 0;'>{home_score} x {away_score}</h2>
                </div>
                """,
            unsafe_allow_html=True,
        )
        if match_goals:
          goals_html = " | ".join([
              f"⚽ <b>{g['scorer']}</b> ({g['clock']})" for g in match_goals
          ])
          st.markdown(
              f"""
                    <div style='text-align: center; font-size: 11px; color: #facc15; margin-top: 4px;'>
                        <b>Gols:</b> {goals_html}
                    </div>
                    """,
              unsafe_allow_html=True,
          )
      else:
        st.markdown(
            f"""
                <div style='text-align: center;'>
                    <span style='background-color:#3b82f6; color:white; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:bold;'>🕒 {formatted_kickoff}</span>
                    <div style='font-size: 11px; color: #94a3b8; margin-top: 3px;'>📍 {venue_name}</div>
                    <h3 style='color:#94a3b8; margin:4px 0;'>vs</h3>
                </div>
                """,
            unsafe_allow_html=True,
        )

    with col3:
      st.markdown(a_red_badge, unsafe_allow_html=True)
      st.markdown(
          f"<h3 style='text-align: left; color: #fff; margin-top: 0;"
          f" margin-bottom: 0;'>{away_team}</h3>",
          unsafe_allow_html=True,
      )
      st.markdown(get_custom_bar(a_press, "away"), unsafe_allow_html=True)

    with st.expander(
        f"📊 Ver Estatísticas Detalhadas ({home_team} vs {away_team})"
    ):
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
        cards_h_str += (
            "<br><span style='font-size:10px; color:#ef4444;'>Expulso(s):"
            f" {', '.join(h_red_players)}</span>"
        )
      if a_red_players:
        cards_a_str += (
            "<br><span style='font-size:10px; color:#ef4444;'>Expulso(s):"
            f" {', '.join(a_red_players)}</span>"
        )

      m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
      with m_col1:
        st.markdown(
            f"""
                <p style='text-align: right;'>
                    <b>{poss_h}</b><br>
                    {h_stats.get('shotsOnTarget', '0')}<br>
                    {h_stats.get('totalShots', '0')}<br>
                    {h_stats.get('wonCorners', '0')}<br>
                    {fouls_h}<br>
                    {cards_h_str}
                </p>
                """,
            unsafe_allow_html=True,
        )
      with m_col2:
        st.markdown(
            """
                <p style='text-align: center; color: #94a3b8;'>
                    Posse de Bola<br>
                    Chutes no Gol<br>
                    Chutes Totais<br>
                    Escanteios<br>
                    Faltas Cometidas<br>
                    Cartões (Amarelos | Vermelhos)
                </p>
                """,
            unsafe_allow_html=True,
        )
      with m_col3:
        st.markdown(
            f"""
                <p style='text-align: left;'>
                    <b>{poss_a}</b><br>
                    {a_stats.get('shotsOnTarget', '0')}<br>
                    {a_stats.get('totalShots', '0')}<br>
                    {a_stats.get('wonCorners', '0')}<br>
                    {fouls_a}<br>
                    {cards_a_str}
                </p>
                """,
            unsafe_allow_html=True,
        )

    st.divider()


render_live_panel(league_slug, selected_league_name, search_query)
