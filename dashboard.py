import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import requests

API_BASE = "https://2gi0kne1gd.execute-api.us-east-1.amazonaws.com/prod"

app = dash.Dash(__name__, title="The Valorant Gazette")

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=IM+Fell+English:ital@0;1&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --ink:       #1a1008;
            --parchment: #f5f0e8;
            --aged:      #ede8da;
            --rule:      #8a7a5a;
            --faded:     #b0a080;
            --accent:    #c0351a;
            --win:       #2a6e3f;
            --loss:      #c0351a;
        }

        html { scroll-behavior: smooth; }

        body {
            background-color: var(--parchment);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Crect width='4' height='4' fill='%23f5f0e8'/%3E%3Crect x='0' y='0' width='1' height='1' fill='%23d4c9a8' opacity='0.25'/%3E%3Crect x='2' y='2' width='1' height='1' fill='%23c8bc9a' opacity='0.15'/%3E%3C/svg%3E");
            color: var(--ink);
            font-family: 'IM Fell English', serif;
            min-height: 100vh;
        }

        /* ── Masthead ───────────────────────────────── */
        .masthead {
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--aged);
            border-bottom: 4px double var(--ink);
            padding: 14px 40px 10px;
            text-align: center;
        }
        .masthead-rule-top {
            border-top: 1px solid var(--ink);
            border-bottom: 1px solid var(--ink);
            padding: 3px 0;
            margin-bottom: 6px;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            display: flex;
            justify-content: space-between;
        }
        .masthead-title {
            font-family: 'UnifrakturMaguntia', cursive;
            font-size: 54px;
            line-height: 1;
            color: var(--ink);
            letter-spacing: 1px;
            margin: 4px 0 2px;
        }
        .masthead-sub {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 12px;
            color: var(--rule);
            letter-spacing: 0.5px;
        }
        .masthead-rule-bot {
            border-top: 2px solid var(--ink);
            margin-top: 8px;
        }

        /* ── Headline ticker ────────────────────────── */
        .ticker-wrap {
            background: var(--ink);
            overflow: hidden;
            padding: 6px 0;
        }
        .ticker-inner {
            display: flex;
            gap: 60px;
            white-space: nowrap;
            animation: ticker 28s linear infinite;
        }
        .ticker-item {
            font-family: 'Playfair Display', serif;
            font-size: 13px;
            font-weight: 700;
            color: var(--parchment);
            flex-shrink: 0;
        }
        .ticker-item em {
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            color: var(--accent);
            letter-spacing: 2px;
            font-style: normal;
            margin-right: 8px;
        }
        @keyframes ticker {
            0%   { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        /* ── Page wrapper ───────────────────────────── */
        .page-wrap {
            max-width: 860px;
            margin: 0 auto;
            padding: 40px 40px 120px;
        }

        /* ── Dateline ───────────────────────────────── */
        .dateline {
            display: flex;
            justify-content: space-between;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 1.5px;
            color: var(--rule);
            padding-bottom: 8px;
            border-bottom: 1px solid var(--rule);
            margin-bottom: 40px;
        }

        /* ── Scroll sections ────────────────────────── */
        .section {
            min-height: 80vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 60px 0;
            opacity: 0;
            transform: translateY(32px);
            transition: opacity 0.7s ease, transform 0.7s ease;
        }
        .section.visible {
            opacity: 1;
            transform: translateY(0);
        }
        .section.faded {
            opacity: 0.08;
            transform: translateY(-24px);
        }
        .section-inner {
            width: 100%;
            border: 1px solid var(--rule);
            padding: 28px 32px;
            background: var(--aged);
            position: relative;
        }
        .section-inner::before {
            content: attr(data-label);
            position: absolute;
            top: -10px;
            left: 24px;
            background: var(--aged);
            padding: 0 8px;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            text-transform: uppercase;
        }

        /* ── Search section ─────────────────────────── */
        .search-row {
            display: flex;
            gap: 14px;
            align-items: flex-end;
            flex-wrap: wrap;
        }
        .input-col { display: flex; flex-direction: column; gap: 5px; }
        .input-col.name { flex: 2; min-width: 200px; }
        .input-col.tag  { flex: 1; min-width: 130px; }
        .field-label {
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            text-transform: uppercase;
        }
        input[type="text"] {
            background: var(--parchment) !important;
            border: 1px solid var(--rule) !important;
            border-bottom: 2px solid var(--ink) !important;
            padding: 8px 12px !important;
            font-family: 'Courier Prime', monospace !important;
            font-size: 13px !important;
            color: var(--ink) !important;
            outline: none !important;
            border-radius: 0 !important;
            width: 100% !important;
        }
        input[type="text"]::placeholder { color: var(--faded) !important; }
        input[type="text"]:focus { border-color: var(--accent) !important; border-bottom-color: var(--accent) !important; }

        .search-btn {
            padding: 9px 26px;
            background: var(--ink);
            color: var(--parchment);
            border: none;
            border-radius: 0;
            font-family: 'Courier Prime', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            cursor: pointer;
            align-self: flex-end;
            margin-bottom: 1px;
            transition: background 0.15s;
        }
        .search-btn:hover { background: var(--accent); }
        .error-msg {
            font-family: 'Courier Prime', monospace;
            font-size: 11px;
            color: var(--accent);
            margin-top: 10px;
            letter-spacing: 1px;
            min-height: 16px;
        }

        /* ── Stat cards ─────────────────────────────── */
        .stat-section-headline {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            font-weight: 900;
            font-style: italic;
            color: var(--ink);
            text-align: center;
            border-bottom: 2px solid var(--ink);
            padding-bottom: 10px;
            margin-bottom: 24px;
        }
        .stat-rule {
            display: flex;
            justify-content: center;
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 3px;
            color: var(--rule);
            margin-bottom: 24px;
            gap: 16px;
        }
        .stat-columns {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            border: 1px solid var(--rule);
        }
        .stat-col {
            padding: 20px 16px;
            text-align: center;
            border-right: 1px solid var(--rule);
        }
        .stat-col:last-child { border-right: none; }
        .stat-label {
            font-family: 'Courier Prime', monospace;
            font-size: 9px;
            letter-spacing: 2px;
            color: var(--rule);
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .stat-value {
            font-family: 'Playfair Display', serif;
            font-size: 40px;
            font-weight: 900;
            color: var(--ink);
            line-height: 1;
        }
        .stat-value .unit {
            font-size: 18px;
            color: var(--rule);
            font-weight: 700;
        }
        .stat-sub {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 11px;
            color: var(--rule);
            margin-top: 5px;
        }

        /* ── Chart sections ─────────────────────────── */
        .chart-headline {
            font-family: 'Playfair Display', serif;
            font-size: 20px;
            font-weight: 700;
            font-style: italic;
            color: var(--ink);
            border-bottom: 1px solid var(--ink);
            padding-bottom: 6px;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .chart-deck {
            font-family: 'IM Fell English', serif;
            font-style: italic;
            font-size: 12px;
            color: var(--rule);
            margin-bottom: 12px;
        }

        /* ── Progress indicator ─────────────────────── */
        .progress-rail {
            position: fixed;
            right: 24px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 200;
        }
        .progress-dot {
            width: 7px;
            height: 7px;
            border: 1px solid var(--rule);
            border-radius: 50%;
            background: transparent;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
        }
        .progress-dot.active {
            background: var(--ink);
            border-color: var(--ink);
        }
        .progress-dot.accent {
            background: var(--accent);
            border-color: var(--accent);
        }

        /* ── Divider ornament ───────────────────────── */
        .ornament {
            text-align: center;
            font-family: 'IM Fell English', serif;
            color: var(--rule);
            font-size: 18px;
            letter-spacing: 10px;
            padding: 10px 0;
        }
    </style>
</head>
<body>
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        function updateSections() {
            const sections = document.querySelectorAll(".section");
            const mid = window.innerHeight / 2;
            sections.forEach(function(sec) {
                const rect = sec.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const dist = Math.abs(center - mid);
                const threshold = window.innerHeight * 0.38;
                sec.classList.remove("visible", "faded");
                if (dist < threshold) {
                    sec.classList.add("visible");
                } else if (rect.bottom < mid) {
                    sec.classList.add("faded");
                }
            });
            // progress dots
            const dots = document.querySelectorAll(".progress-dot");
            let closest = 0;
            let minDist = Infinity;
            sections.forEach(function(sec, i) {
                const rect = sec.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const dist = Math.abs(center - mid);
                if (dist < minDist) { minDist = dist; closest = i; }
            });
            dots.forEach(function(d, i) {
                d.classList.toggle("active", i === closest);
            });
        }
        window.addEventListener("scroll", updateSections, { passive: true });
        updateSections();

        document.querySelectorAll(".progress-dot").forEach(function(dot) {
            dot.addEventListener("click", function() {
                const i = parseInt(dot.getAttribute("data-index"), 10);
                const sections = document.querySelectorAll(".section");
                if (sections[i]) sections[i].scrollIntoView({ behavior: "smooth", block: "center" });
            });
        });
    });
    </script>
</body>
</html>
'''

# ── Layout ─────────────────────────────────────────────────────────────────

TICKER_ITEMS = [
    ("BREAKING", "Radiant tier fracas erupts on Ascent — full coverage inside"),
    ("REPORT",   "Jett usage falls for third consecutive act"),
    ("ANALYSIS", "Headshot percentages at historic low this episode"),
    ("DISPATCH", "New operator found dominant on long-range sightlines"),
    ("BULLETIN", "Chamber rework draws ire of professional circuit"),
]

def ticker_html():
    items = [
        html.Span([html.Em(label), text], className="ticker-item")
        for label, text in TICKER_ITEMS * 2   # duplicate for seamless loop
    ]
    return html.Div(className="ticker-wrap", children=[
        html.Div(items, className="ticker-inner")
    ])

app.layout = html.Div(children=[

    # Sticky masthead
    html.Div(className="masthead", children=[
        html.Div(className="masthead-rule-top", children=[
            html.Span("EST. PATCH 10.03"),
            html.Span("★  OFFICIAL RECORD  ★"),
            html.Span("FIVE ROUNDS OR BUST"),
        ]),
        html.Div("The Valorant Gazette", className="masthead-title"),
        html.Div("All The Frags Fit To Print — Competitive Intelligence Since Episode I", className="masthead-sub"),
        html.Div(className="masthead-rule-bot"),
    ]),

    ticker_html(),

    # Progress dots (JS fills active class and handles clicks)
    html.Div(className="progress-rail", children=[
        html.Div(id=f"dot-{i}", className="progress-dot",
                 **{"data-index": str(i)})
        for i in range(6)
    ]),

    # Page body
    html.Div(className="page-wrap", children=[

        # Dateline
        html.Div(className="dateline", children=[
            html.Span("COMPETITIVE DIVISION — UNRANKED TO RADIANT"),
            html.Span("ALL QUEUES · ALL MAPS"),
        ]),

        # ── Section 0: Search ───────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-inner", **{"data-label": "Intelligence Bureau — Player Registry"}, children=[
                html.Div(style={"textAlign": "center", "marginBottom": "24px"}, children=[
                    html.Div("Field Correspondent Lookup", style={
                        "fontFamily": "'Playfair Display', serif",
                        "fontSize": "26px", "fontWeight": "900",
                        "fontStyle": "italic", "color": "#1a1008",
                        "borderBottom": "2px solid #1a1008",
                        "paddingBottom": "8px", "marginBottom": "6px",
                    }),
                    html.Div("Enter a Riot ID to retrieve the operative's full combat dossier.",
                             style={"fontFamily": "'IM Fell English', serif",
                                    "fontStyle": "italic", "fontSize": "13px", "color": "#8a7a5a"}),
                ]),
                html.Div(className="search-row", children=[
                    html.Div(className="input-col name", children=[
                        html.Label("Agent Designation (Riot Name)", className="field-label"),
                        dcc.Input(id="name-input", type="text", placeholder="bananabrigade"),
                    ]),
                    html.Div(className="input-col tag", children=[
                        html.Label("Regiment Tag", className="field-label"),
                        dcc.Input(id="tag-input", type="text", placeholder="banan"),
                    ]),
                    html.Button("— Dispatch —", id="search-btn", n_clicks=0, className="search-btn"),
                ]),
                html.Div(id="error-msg", className="error-msg"),
            ]),
        ]),

        html.Div("✦  ✦  ✦", className="ornament"),

        # ── Section 1: Stat cards ───────────────────
        html.Div(className="section", children=[
            html.Div(id="stat-cards-section", className="section-inner",
                     **{"data-label": "Combat Record — Summary Dispatch"},
                     children=[html.Div("Awaiting dispatch…",
                                        style={"textAlign": "center", "fontFamily": "'Courier Prime', monospace",
                                               "fontSize": "11px", "letterSpacing": "2px", "color": "#8a7a5a",
                                               "padding": "40px 0"})]),
        ]),

        html.Div("✦  ✦  ✦", className="ornament"),

        # ── Section 2: K/D trend ────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-inner", **{"data-label": "Frontline Report — Kill/Death"}, children=[
                html.Div(className="chart-headline", children=[
                    html.Span("K/D Ratio — Recent Dispatches"),
                    html.Span("PER MATCH", style={"fontFamily": "'Courier Prime', monospace",
                                                   "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Green markers denote victories; red, defeats. Dashed line marks the campaign average.",
                         className="chart-deck"),
                dcc.Graph(id="kd-trend-chart", config={"displayModeBar": False}),
            ]),
        ]),

        html.Div("✦  ✦  ✦", className="ornament"),

        # ── Section 3: HS% trend ────────────────────
        html.Div(className="section", children=[
            html.Div(className="section-inner", **{"data-label": "Marksman's Log — Headshot Analysis"}, children=[
                html.Div(className="chart-headline", children=[
                    html.Span("Headshot % — Field Reports"),
                    html.Span("PER MATCH", style={"fontFamily": "'Courier Prime', monospace",
                                                   "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Precision indexed per engagement. A steady hand separates the correspondent from the combatant.",
                         className="chart-deck"),
                dcc.Graph(id="hs-trend-chart", config={"displayModeBar": False}),
            ]),
        ]),

        html.Div("✦  ✦  ✦", className="ornament"),

        # ── Section 4: Agent win rates ──────────────
        html.Div(className="section", children=[
            html.Div(className="section-inner", **{"data-label": "Operative Profiles — Agent Deployment"}, children=[
                html.Div(className="chart-headline", children=[
                    html.Span("Agent Win Rates — Deployment Record"),
                    html.Span("WIN RATE %", style={"fontFamily": "'Courier Prime', monospace",
                                                    "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Which operatives have proven most effective in the field this campaign season.",
                         className="chart-deck"),
                dcc.Graph(id="agent-chart", config={"displayModeBar": False}),
            ]),
        ]),

        html.Div("✦  ✦  ✦", className="ornament"),

        # ── Section 5: Map win rates ────────────────
        html.Div(className="section", children=[
            html.Div(className="section-inner", **{"data-label": "Theatre of Operations — Map Record"}, children=[
                html.Div(className="chart-headline", children=[
                    html.Span("Map Win Rates — Theatre Record"),
                    html.Span("WIN RATE %", style={"fontFamily": "'Courier Prime', monospace",
                                                    "fontSize": "9px", "letterSpacing": "2px", "color": "#8a7a5a"}),
                ]),
                html.Div("Territorial dominance across all active combat zones. Know thy ground.",
                         className="chart-deck"),
                dcc.Graph(id="map-chart", config={"displayModeBar": False}),
            ]),
        ]),

    ]),

    dcc.Store(id="player-data", data=None),
])


# ── Fetch player data ───────────────────────────────────────────────────────

@app.callback(
    Output("player-data", "data"),
    Output("error-msg",   "children"),
    Input("search-btn",   "n_clicks"),
    State("name-input",   "value"),
    State("tag-input",    "value"),
    prevent_initial_call=True,
)
def fetch_player(n_clicks, game_name, tag_line):
    if not game_name or not tag_line:
        return None, "— Please enter both a name and tag. —"
    try:
        r = requests.get(f"{API_BASE}/player/{game_name.strip()}/{tag_line.strip()}")
        if r.status_code == 404:
            return None, r.json().get("detail", "Operative not found in the registry.")
        r.raise_for_status()
        return r.json(), ""
    except Exception as e:
        return None, f"Correspondent unreachable: {e}"


# ── Render all visuals ──────────────────────────────────────────────────────

@app.callback(
    Output("stat-cards-section", "children"),
    Output("kd-trend-chart",     "figure"),
    Output("hs-trend-chart",     "figure"),
    Output("agent-chart",        "figure"),
    Output("map-chart",          "figure"),
    Input("player-data",         "data"),
)
def render_visuals(player_data):
    BG      = "#ede8da"
    INK     = "#1a1008"
    RULE    = "#8a7a5a"
    FADED   = "#c8bc9a"
    ACCENT  = "#c0351a"
    WIN_CLR = "#2a6e3f"
    LOSS_CLR= "#c0351a"

    FONT = "IM Fell English, serif"
    MONO = "Courier Prime, monospace"
    DISP = "Playfair Display, serif"

    def base_layout(title="", **kwargs):
        return dict(
            title={"text": title, "font": {"color": INK, "size": 14, "family": DISP}} if title else None,
            plot_bgcolor=BG, paper_bgcolor=BG,
            font={"color": INK, "family": MONO},
            height=320,
            margin={"t": 30, "b": 50, "l": 50, "r": 20},
            xaxis={"showgrid": False, "color": RULE, "linecolor": FADED,
                   "tickfont": {"family": MONO, "size": 10}},
            yaxis={"gridcolor": FADED, "gridwidth": 0.5, "color": RULE,
                   "linecolor": FADED, "tickfont": {"family": MONO, "size": 10}},
            hoverlabel={"bgcolor": INK, "font_color": BG, "font_family": MONO, "font_size": 11},
            **kwargs,
        )

    def empty_fig():
        f = go.Figure()
        f.update_layout(**base_layout())
        f.add_annotation(text="Awaiting dispatch…", x=0.5, y=0.5,
                         xref="paper", yref="paper", showarrow=False,
                         font={"family": MONO, "size": 12, "color": RULE})
        return f

    if not player_data:
        placeholder = html.Div("Awaiting dispatch…", style={
            "textAlign": "center", "fontFamily": MONO,
            "fontSize": "11px", "letterSpacing": "2px",
            "color": RULE, "padding": "40px 0",
        })
        return placeholder, empty_fig(), empty_fig(), empty_fig(), empty_fig()

    summary    = player_data["summary"]
    matches    = player_data["matches"]
    match_nums = list(range(1, len(matches) + 1))
    colors     = [WIN_CLR if m["won"] else LOSS_CLR for m in matches]

    # ── Stat cards ──────────────────────────────────
    def stat_col(label, value, unit="", sub=""):
        return html.Div(className="stat-col", children=[
            html.Div(label, className="stat-label"),
            html.Div([value, html.Span(unit, className="unit")], className="stat-value"),
            html.Div(sub, className="stat-sub"),
        ])

    stat_section = html.Div(children=[
        html.Div("Combat Dossier — Season Summary", style={
            "fontFamily": DISP, "fontSize": "26px", "fontWeight": "900",
            "fontStyle": "italic", "color": INK, "textAlign": "center",
            "borderBottom": f"2px solid {INK}", "paddingBottom": "10px", "marginBottom": "6px",
        }),
        html.Div("✦  VERIFIED DISPATCH  ✦  ALL QUEUES  ✦  LAST 20 MATCHES  ✦", style={
            "textAlign": "center", "fontFamily": MONO, "fontSize": "9px",
            "letterSpacing": "3px", "color": RULE, "marginBottom": "20px",
        }),
        html.Div(className="stat-columns", children=[
            stat_col("Win Rate",          str(summary["win_rate"]),             "%",  "Of battles contested"),
            stat_col("Avg K/D",           str(summary["avg_kd"]),               "",   "Kills per death"),
            stat_col("Avg Headshot %",    str(summary["avg_hs_pct"]),           "%",  "Precision in the field"),
            stat_col("Avg DMG / Round",   str(summary["avg_damage_per_round"]), "",   "Damage inflicted per round"),
        ]),
    ])

    # ── K/D trend ───────────────────────────────────
    kd_fig = go.Figure()
    kd_fig.add_trace(go.Scatter(
        x=match_nums,
        y=[m["kd_ratio"] for m in matches],
        mode="lines+markers",
        line={"color": INK, "width": 1.5, "dash": "solid"},
        marker={"color": colors, "size": 9, "symbol": "circle",
                "line": {"width": 1.5, "color": BG}},
        customdata=[[m["damage_per_round"], m["rounds_played"]] for m in matches],
        hovertemplate=(
            "<b>Match %{x}</b><br>"
            "K/D: %{y}<br>"
            "DMG/R: %{customdata[0]}<br>"
            "Rounds: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))
    kd_fig.add_hline(y=summary["avg_kd"], line_dash="dash", line_color=RULE, line_width=1,
                     annotation_text=f"avg {summary['avg_kd']}",
                     annotation_font={"color": RULE, "family": MONO, "size": 10})
    kd_fig.update_layout(**base_layout(xaxis_title="Match #", yaxis_title="K/D Ratio"))

    # ── HS% trend ───────────────────────────────────
    hs_fig = go.Figure()
    hs_fig.add_trace(go.Scatter(
        x=match_nums,
        y=[m["hs_pct"] for m in matches],
        mode="lines+markers",
        line={"color": ACCENT, "width": 1.5},
        marker={"color": colors, "size": 9, "symbol": "circle",
                "line": {"width": 1.5, "color": BG}},
        hovertemplate="<b>Match %{x}</b><br>HS%%: %{y}%%<extra></extra>",
    ))
    hs_fig.add_hline(y=summary["avg_hs_pct"], line_dash="dash", line_color=RULE, line_width=1,
                     annotation_text=f"avg {summary['avg_hs_pct']}%",
                     annotation_font={"color": RULE, "family": MONO, "size": 10})
    hs_fig.update_layout(**base_layout(xaxis_title="Match #", yaxis_title="Headshot %"))

    # ── Agent win rates ──────────────────────────────
    agent_fig = go.Figure(go.Bar(
        x=list(summary["agent_win_rates"].keys()),
        y=list(summary["agent_win_rates"].values()),
        marker_color=INK,
        marker_pattern_shape="/",
        marker_pattern_fgcolor=BG,
        marker_pattern_size=6,
        marker_line_color=INK,
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Win rate: %{y}%<extra></extra>",
    ))
    agent_fig.update_layout(**base_layout(xaxis_title="Agent", yaxis_title="Win Rate %", yaxis_range=[0, 100]))

    # ── Map win rates ────────────────────────────────
    map_fig = go.Figure(go.Bar(
        x=list(summary["map_win_rates"].keys()),
        y=list(summary["map_win_rates"].values()),
        marker_color=ACCENT,
        marker_pattern_shape="\\",
        marker_pattern_fgcolor=BG,
        marker_pattern_size=6,
        marker_line_color=ACCENT,
        marker_line_width=1,
        hovertemplate="<b>%{x}</b><br>Win rate: %{y}%<extra></extra>",
    ))
    map_fig.update_layout(**base_layout(xaxis_title="Map", yaxis_title="Win Rate %", yaxis_range=[0, 100]))

    return stat_section, kd_fig, hs_fig, agent_fig, map_fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)