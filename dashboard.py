import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import requests

API_BASE = "https://2gi0kne1gd.execute-api.us-east-1.amazonaws.com/prod"

app = dash.Dash(__name__, title="Valorant Dashboard")

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: "Inter", sans-serif;
            transition: background-color 0.25s, color 0.25s;
        }

        body.light { background-color: #f0f2f5; color: #222; }
        body.dark  { background-color: #0d1117; color: #e5e5e5; }

        .page-wrap {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 3rem;
            min-height: 100vh;
        }

        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #ff4655;
        }
        .header h1 {
            font-size: 26px;
            font-weight: 700;
            color: #ff4655;
            letter-spacing: 1.5px;
            font-family: "Inter", sans-serif;
        }
        .header p { font-size: 13px; margin-top: 5px; }
        body.light .header p { color: #666; }
        body.dark  .header p { color: #888; }

        /* Toggle button */
        .toggle-btn {
            padding: 8px 18px;
            border-radius: 20px;
            border: 1.5px solid #ff4655;
            background: transparent;
            color: #ff4655;
            font-size: 13px;
            font-weight: 600;
            font-family: "Inter", sans-serif;
            cursor: pointer;
            white-space: nowrap;
            transition: background 0.15s, color 0.15s;
        }
        .toggle-btn:hover { background: #ff4655; color: white; }

        /* Search card */
        .search-card {
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        body.light .search-card { background: white;   box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
        body.dark  .search-card { background: #161b22; box-shadow: 0 1px 6px rgba(0,0,0,0.3);  }

        .search-row {
            display: flex;
            gap: 12px;
            align-items: flex-start;
            flex-wrap: wrap;
        }

        .input-group { display: flex; flex-direction: column; }
        .input-group.name { flex: 2; min-width: 200px; }
        .input-group.tag  { flex: 1; min-width: 140px; }

        .input-label {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 6px;
            display: block;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }
        body.light .input-label { color: #555; }
        body.dark  .input-label { color: #aaa; }

        .input-hint { font-size: 11px; margin-top: 5px; }
        body.light .input-hint { color: #bbb; }
        body.dark  .input-hint { color: #555; }

        /* Input fix — line-height prevents descender clipping */
        input[type="text"] {
            width: 100% !important;
            padding: 10px 14px !important;
            line-height: 1.6 !important;
            font-size: 14px !important;
            font-family: "Inter", sans-serif !important;
            border-radius: 7px !important;
            outline: none;
            transition: border-color 0.15s, background 0.15s, color 0.15s;
        }
        body.light input[type="text"] {
            background: #fafafa; color: #222;
            border: 1px solid #ddd !important;
        }
        body.dark input[type="text"] {
            background: #0d1117; color: #e5e5e5;
            border: 1px solid #2e3f50 !important;
        }
        input[type="text"]:focus { border-color: #ff4655 !important; }

        /* Search button */
        .search-btn {
            padding: 11px 28px;
            background-color: #ff4655;
            color: white;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-weight: 700;
            font-size: 14px;
            font-family: "Inter", sans-serif;
            align-self: flex-start;
            margin-top: 24px;
            transition: background 0.15s;
            letter-spacing: 0.3px;
        }
        .search-btn:hover { background-color: #e03545; }

        .error-msg { color: #ff4655; font-size: 13px; margin-top: 10px; min-height: 18px; }

        /* Stat cards */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 2rem;
        }
        .stat-card {
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            text-align: center;
            transition: background 0.25s, box-shadow 0.25s;
        }
        body.light .stat-card { background: white;   box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
        body.dark  .stat-card { background: #161b22; box-shadow: 0 1px 6px rgba(0,0,0,0.3);  }

        .stat-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 8px;
        }
        body.light .stat-label { color: #999; }
        body.dark  .stat-label { color: #666; }

        .stat-value {
            font-size: 28px;
            font-weight: 700;
            line-height: 1;
        }
        body.light .stat-value { color: #111; }
        body.dark  .stat-value { color: #f0f0f0; }

        /* Chart cards */
        .chart-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }
        .chart-card {
            border-radius: 12px;
            padding: 1rem;
            transition: background 0.25s, box-shadow 0.25s;
        }
        body.light .chart-card { background: white;   box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
        body.dark  .chart-card { background: #161b22; box-shadow: 0 1px 6px rgba(0,0,0,0.3);  }
    </style>
</head>
<body class="light">
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
</body>
</html>
'''

# --- Layout ---

app.layout = html.Div(className="page-wrap", children=[

    # Header
    html.Div(className="header", children=[
        html.Div(children=[
            html.H1("VALORANT Stats Dashboard"),
            html.P("Enter a player's Riot ID to view their competitive stats."),
        ]),
        html.Button("Dark Mode", id="theme-btn", n_clicks=0, className="toggle-btn"),
    ]),

    # Search card
    html.Div(className="search-card", children=[
        html.Div(className="search-row", children=[
            html.Div(className="input-group name", children=[
                html.Label("Riot Name", className="input-label"),
                dcc.Input(id="name-input", type="text", placeholder="e.g. bananabrigade"),
                html.P("Your Riot display name", className="input-hint"),
            ]),
            html.Div(className="input-group tag", children=[
                html.Label("Tag", className="input-label"),
                dcc.Input(id="tag-input", type="text", placeholder="e.g. banan"),
                html.P("Without the #", className="input-hint"),
            ]),
            html.Button("Search", id="search-btn", n_clicks=0, className="search-btn"),
        ]),
        html.Div(id="error-msg", className="error-msg"),
    ]),

    # Stat cards — rendered by callback so theme applies immediately
    html.Div(id="stat-cards", className="stat-grid"),

    # Charts
    html.Div(className="chart-row", children=[
        html.Div(className="chart-card", children=[dcc.Graph(id="kd-trend-chart",  config={"displayModeBar": False})]),
        html.Div(className="chart-card", children=[dcc.Graph(id="agent-chart",     config={"displayModeBar": False})]),
    ]),
    html.Div(className="chart-row", children=[
        html.Div(className="chart-card", children=[dcc.Graph(id="hs-trend-chart",  config={"displayModeBar": False})]),
        html.Div(className="chart-card", children=[dcc.Graph(id="map-chart",       config={"displayModeBar": False})]),
    ]),

    dcc.Store(id="theme-store", data="light"),
    dcc.Store(id="player-data", data=None),
])


# --- Dark mode toggle (clientside — no server round trip) ---

app.clientside_callback(
    """
    function(n_clicks, current_theme) {
        const newTheme = current_theme === "light" ? "dark" : "light";
        document.body.className = newTheme;
        return [newTheme, newTheme === "dark" ? "Light Mode" : "Dark Mode"];
    }
    """,
    Output("theme-store", "data"),
    Output("theme-btn",   "children"),
    Input("theme-btn",    "n_clicks"),
    State("theme-store",  "data"),
    prevent_initial_call=True,
)


# --- Fetch data on search, store in dcc.Store ---

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
        return None, "Please enter both a name and tag."
    try:
        r = requests.get(f"{API_BASE}/player/{game_name.strip()}/{tag_line.strip()}")
        if r.status_code == 404:
            return None, r.json().get("detail", "Player not found.")
        r.raise_for_status()
        return r.json(), ""
    except Exception as e:
        return None, f"Could not reach API: {e}"


# --- Render all visuals (re-runs on theme change AND new data) ---

@app.callback(
    Output("stat-cards",     "children"),
    Output("kd-trend-chart", "figure"),
    Output("hs-trend-chart", "figure"),
    Output("agent-chart",    "figure"),
    Output("map-chart",      "figure"),
    Input("theme-store",     "data"),
    Input("player-data",     "data"),
)
def render_visuals(theme, player_data):
    dark = theme == "dark"

    bg         = "#161b22" if dark else "white"
    grid_color = "#2a3441" if dark else "#f0f0f0"
    font_color = "#e5e5e5" if dark else "#333"
    axis_color = "#555"    if dark else "#999"

    def base_layout(title, **kwargs):
        return dict(
            title={"text": title, "font": {"color": font_color, "size": 14, "family": "Inter"}},
            plot_bgcolor=bg, paper_bgcolor=bg,
            font={"color": font_color, "family": "Inter"},
            height=300,
            margin={"t": 44, "b": 44, "l": 44, "r": 20},
            xaxis={"showgrid": False, "color": axis_color, "linecolor": grid_color},
            yaxis={"gridcolor": grid_color, "color": axis_color, "linecolor": grid_color},
            **kwargs,
        )

    def empty_fig(title):
        f = go.Figure()
        f.update_layout(**base_layout(title))
        return f

    if not player_data:
        cards = []
        return (
            cards,
            empty_fig("K/D Ratio per Match"),
            empty_fig("Headshot % per Match"),
            empty_fig("Agent Win Rates"),
            empty_fig("Map Win Rates"),
        )

    summary    = player_data["summary"]
    matches    = player_data["matches"]
    match_nums = list(range(1, len(matches) + 1))
    colors     = ["#22c55e" if m["won"] else "#ff4655" for m in matches]

    # Stat cards — use CSS classes so theme transitions apply automatically
    cards = [
        make_stat_card("Win Rate",            f"{summary['win_rate']}%",   "#ff4655"),
        make_stat_card("Avg K/D",             str(summary["avg_kd"]),      "#7c3aed"),
        make_stat_card("Avg HS%",             f"{summary['avg_hs_pct']}%", "#f97316"),
        make_stat_card("Avg Damage / Round", str(summary["avg_damage_per_round"]), "#22c55e"),
    ]

    # K/D trend
    kd_fig = go.Figure()
    kd_fig.add_trace(go.Scatter(
        x=match_nums,
        y=[m["kd_ratio"] for m in matches],
        mode="lines+markers",
        line={"color": "#ff4655", "width": 2},
        marker={"color": colors, "size": 9, "line": {"width": 1.5, "color": bg}},
        customdata=[[m["damage_per_round"], m["rounds_played"]] for m in matches],
        hovertemplate=(
            "Match %{x}<br>"
            "K/D: %{y}<br>"
            "DMG/R: %{customdata[0]}<br>"
            "Rounds: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))
    kd_fig.add_hline(y=summary["avg_kd"], line_dash="dash", line_color="#555",
                     annotation_text=f"Avg {summary['avg_kd']}",
                     annotation_font_color="#888")
    kd_fig.update_layout(**base_layout("K/D Ratio per Match",
                                       xaxis_title="Match #", yaxis_title="K/D"))

    # HS% trend
    hs_fig = go.Figure()
    hs_fig.add_trace(go.Scatter(
        x=match_nums, y=[m["hs_pct"] for m in matches],
        mode="lines+markers",
        line={"color": "#f97316", "width": 2},
        marker={"color": colors, "size": 9, "line": {"width": 1.5, "color": bg}},
        hovertemplate="Match %{x}<br>HS%%: %{y}%<extra></extra>",
    ))
    hs_fig.add_hline(y=summary["avg_hs_pct"], line_dash="dash", line_color="#555",
                     annotation_text=f"Avg {summary['avg_hs_pct']}%",
                     annotation_font_color="#888")
    hs_fig.update_layout(**base_layout("Headshot % per Match",
                                       xaxis_title="Match #", yaxis_title="HS%"))

    # Agent win rates
    agent_fig = go.Figure(go.Bar(
        x=list(summary["agent_win_rates"].keys()),
        y=list(summary["agent_win_rates"].values()),
        marker_color="#ff4655",
        hovertemplate="%{x}<br>Win rate: %{y}%<extra></extra>",
    ))
    agent_fig.update_layout(**base_layout("Agent Win Rates",
                                          xaxis_title="Agent", yaxis_title="Win Rate %",
                                          yaxis_range=[0, 100]))

    # Map win rates
    map_fig = go.Figure(go.Bar(
        x=list(summary["map_win_rates"].keys()),
        y=list(summary["map_win_rates"].values()),
        marker_color="#7c3aed",
        hovertemplate="%{x}<br>Win rate: %{y}%<extra></extra>",
    ))
    map_fig.update_layout(**base_layout("Map Win Rates",
                                        xaxis_title="Map", yaxis_title="Win Rate %",
                                        yaxis_range=[0, 100]))

    return cards, kd_fig, hs_fig, agent_fig, map_fig


def make_stat_card(label: str, value: str, color: str) -> html.Div:
    return html.Div(className="stat-card", style={"borderTop": f"3px solid {color}"}, children=[
        html.P(label, className="stat-label"),
        html.P(value, className="stat-value"),
    ])


if __name__ == "__main__":
    app.run(debug=True, port=8050)