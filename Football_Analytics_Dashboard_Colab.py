# ============================================================
#  FOOTBALL ANALYTICS & PLAYER VALUATION DASHBOARD
#  Senior Sports Data Scientist | Single-Cell Colab Script
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from google.colab import files

np.random.seed(42)

# ============================================================
# STEP 1 — GENERATE REALISTIC SPORTS DATA
# ============================================================

first_names = [
    "Luca", "Marco", "Carlos", "Arjen", "Kylian", "Erling", "Pedri", "Vini",
    "Bruno", "Rodri", "Declan", "Bukayo", "Phil", "Jamal", "Federico",
    "Antoine", "Bernardo", "Rúben", "Trent", "Virgil", "Marquinhos", "Jules",
    "Aymeric", "William", "Theo", "Marcus", "Rasmus", "Darwin", "Dušan",
    "Victor", "Randal", "Khvicha", "Leroy", "Ilkay", "Toni", "Lautaro",
    "Paulo", "Raphael", "Ousmane", "Nico"
]
last_names = [
    "Modrić", "Verratti", "Soler", "Robben", "Mbappé", "Haaland", "González",
    "Júnior", "Fernandes", "Busquets", "Rice", "Saka", "Foden", "Musiala",
    "Chiesa", "Griezmann", "Silva", "Dias", "Alexander-Arnold", "van Dijk",
    "Marquinhos", "Koundé", "Laporte", "Saliba", "Hernández", "Rashford",
    "Højlund", "Núñez", "Vlahović", "Osimhen", "Koné", "Kvaratskhelia",
    "Sané", "Gündogan", "Kroos", "Martínez", "Dybala", "Guerreiro",
    "Dembélé", "Williams"
]
player_names = [f"{f} {l}" for f, l in zip(first_names, last_names)]

positions_pool = (
    ["FW"] * 14 + ["MID"] * 14 + ["DEF"] * 12
)
np.random.shuffle(positions_pool)
positions = positions_pool[:40]

signing_status = (
    ["New Signing"] * 4 +
    ["Academy"] * 8 +
    ["Core Team"] * 28
)
np.random.shuffle(signing_status)

rows = []
for i in range(40):
    pos    = positions[i]
    status = signing_status[i]

    # --- Minutes Played ---
    minutes = int(np.random.normal(2200, 500))
    minutes = np.clip(minutes, 600, 3600)

    scale = minutes / 3400  # 0..1 scale relative to full season

    # --- Position-based base stats ---
    if pos == "FW":
        base_xg    = np.random.uniform(8, 20) * scale
        base_xa    = np.random.uniform(3, 10) * scale
    elif pos == "MID":
        base_xg    = np.random.uniform(3, 12) * scale
        base_xa    = np.random.uniform(5, 14) * scale
    else:  # DEF
        base_xg    = np.random.uniform(0.5, 5) * scale
        base_xa    = np.random.uniform(1, 6) * scale

    # --- Market Value ---
    if status == "New Signing":
        mv = np.random.uniform(50, 80)
    elif status == "Academy":
        mv = np.random.uniform(5, 15)
    else:
        mv = np.random.uniform(10, 55)

    # --- Conversion logic ---
    if status == "New Signing":
        # High xG but very low actual goals (underperforming expensive signings)
        xg     = round(base_xg * np.random.uniform(1.1, 1.4), 2)
        goals  = max(0, int(xg * np.random.uniform(0.3, 0.55)))
        xa     = round(base_xa * np.random.uniform(0.9, 1.1), 2)
        assists = max(0, int(xa * np.random.uniform(0.4, 0.65)))

    elif status == "Academy" and np.random.rand() < 0.65:
        # Hidden gems — over-perform their xG
        xg     = round(base_xg * np.random.uniform(0.7, 1.0), 2)
        goals  = int(xg * np.random.uniform(1.3, 1.8))   # clinical
        xa     = round(base_xa * np.random.uniform(0.7, 1.0), 2)
        assists = int(xa * np.random.uniform(1.2, 1.6))

    else:
        # Normal variance around xG
        xg     = round(base_xg, 2)
        goals  = max(0, int(np.random.normal(xg, xg * 0.25)))
        xa     = round(base_xa, 2)
        assists = max(0, int(np.random.normal(xa, xa * 0.25)))

    rows.append({
        "Player_Name":    player_names[i],
        "Position":       pos,
        "Market_Value_M": round(mv, 1),
        "Minutes_Played": minutes,
        "Goals":          goals,
        "Assists":        assists,
        "xG":             xg,
        "xA":             xa,
        "Signing_Status": status,
    })

df = pd.DataFrame(rows)

# ============================================================
# STEP 2 — KPI CALCULATIONS
# ============================================================

df["G_plus_A"]         = df["Goals"] + df["Assists"]
df["Value_For_Money"]  = (df["G_plus_A"] / df["Market_Value_M"]).round(3)
df["Conversion_Delta"] = (df["Goals"] - df["xG"]).round(2)

top_scorer_row      = df.loc[df["Goals"].idxmax()]
best_value_row      = df.loc[df["Value_For_Money"].idxmax()]
underperformer_row  = df.loc[df["Conversion_Delta"].idxmin()]

kpi_top_scorer     = f"{top_scorer_row['Player_Name']} ({int(top_scorer_row['Goals'])} goals)"
kpi_best_value     = f"{best_value_row['Player_Name']} ({best_value_row['Value_For_Money']:.2f} G+A/M€)"
kpi_underperformer = f"{underperformer_row['Player_Name']} ({underperformer_row['Conversion_Delta']:.1f} goals vs xG)"

print("✅ Data Generated & KPIs Calculated")
print(f"   🥇 Top Scorer:       {kpi_top_scorer}")
print(f"   💎 Best Value:       {kpi_best_value}")
print(f"   ⚠️  Underperformer:  {kpi_underperformer}")

# ============================================================
# STEP 3 — PLOTLY FIGURES
# ============================================================

PALETTE = {
    "bg":          "#0f1117",
    "card":        "#1a1d27",
    "crimson":     "#dc2626",
    "crimson_lt":  "#ef4444",
    "silver":      "#e2e8f0",
    "muted":       "#64748b",
    "grid":        "#1e2330",
    "fw":          "#dc2626",
    "mid":         "#f59e0b",
    "def":         "#3b82f6",
}

FONT   = "Rajdhani, Barlow Condensed, Arial Narrow, Arial, sans-serif"
LAYOUT = dict(
    paper_bgcolor = PALETTE["bg"],
    plot_bgcolor  = PALETTE["card"],
    font          = dict(family=FONT, color=PALETTE["silver"], size=13),
)
MARGIN_DEFAULT = dict(l=20, r=20,  t=55, b=20)
MARGIN_ROI     = dict(l=20, r=80,  t=55, b=20)

pos_colors = {"FW": PALETTE["fw"], "MID": PALETTE["mid"], "DEF": PALETTE["def"]}

# ── Figure 1: Clinical Finishers Matrix ──────────────────────
diag_max = max(df["xG"].max(), df["Goals"].max()) * 1.1

fig_matrix = go.Figure()

# Diagonal reference line
fig_matrix.add_trace(go.Scatter(
    x=[0, diag_max], y=[0, diag_max],
    mode="lines",
    line=dict(color="#475569", dash="dash", width=1.5),
    name="xG = Goals",
    hoverinfo="skip",
))

for pos, color in pos_colors.items():
    sub = df[df["Position"] == pos]
    fig_matrix.add_trace(go.Scatter(
        x=sub["xG"],
        y=sub["Goals"],
        mode="markers",
        name=pos,
        marker=dict(
            size=sub["Market_Value_M"] / 3.5,
            color=color,
            opacity=0.85,
            line=dict(color="#ffffff", width=0.8),
        ),
        customdata=sub[["Player_Name","Market_Value_M","Signing_Status","Conversion_Delta"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "xG: %{x:.2f} | Goals: %{y}<br>"
            "Market Value: €%{customdata[1]}M<br>"
            "Status: %{customdata[2]}<br>"
            "Δ Conversion: %{customdata[3]:+.2f}<extra></extra>"
        ),
    ))

fig_matrix.update_layout(
    **LAYOUT,
    title=dict(
        text="<b>CLINICAL FINISHERS MATRIX</b>  <span style='font-size:12px;color:#64748b'>xG vs Actual Goals · Bubble = Market Value</span>",
        font=dict(size=16, color=PALETTE["silver"]),
        x=0.02,
    ),
    xaxis=dict(title="Expected Goals (xG)", gridcolor=PALETTE["grid"], zeroline=False),
    yaxis=dict(title="Actual Goals",         gridcolor=PALETTE["grid"], zeroline=False),
    legend=dict(
        bgcolor="#1a1d27", bordercolor="#2d3748", borderwidth=1,
        font=dict(size=12),
        title=dict(text="Position", font=dict(size=12)),
    ),
    margin=MARGIN_DEFAULT,
    height=480,
)

# ── Figure 2: Value for Money – Top 10 Bar ───────────────────
top10 = df.nlargest(10, "Value_For_Money").sort_values("Value_For_Money")
bar_colors = [pos_colors[p] for p in top10["Position"]]

fig_roi = go.Figure(go.Bar(
    x=top10["Value_For_Money"],
    y=top10["Player_Name"],
    orientation="h",
    marker=dict(
        color=bar_colors,
        opacity=0.9,
        line=dict(color="#0f1117", width=0.5),
    ),
    customdata=top10[["G_plus_A","Market_Value_M","Position","Signing_Status"]].values,
    hovertemplate=(
        "<b>%{y}</b><br>"
        "G+A / M€: %{x:.3f}<br>"
        "G+A: %{customdata[0]} | Value: €%{customdata[1]}M<br>"
        "Position: %{customdata[2]} | %{customdata[3]}<extra></extra>"
    ),
    text=top10["Value_For_Money"].apply(lambda v: f"{v:.2f}"),
    textposition="outside",
    textfont=dict(color=PALETTE["silver"], size=11),
))

fig_roi.update_layout(
    **LAYOUT,
    title=dict(
        text="<b>VALUE FOR MONEY</b>  <span style='font-size:12px;color:#64748b'>Top 10 · G+A per M€</span>",
        font=dict(size=16, color=PALETTE["silver"]),
        x=0.02,
    ),
    xaxis=dict(title="G+A per Million €", gridcolor=PALETTE["grid"], zeroline=False),
    yaxis=dict(tickfont=dict(size=12)),
    height=420,
    margin=MARGIN_ROI,
)

# ── Figure 3: Goals by Position – Donut ──────────────────────
pos_goals = df.groupby("Position")["Goals"].sum().reset_index()

fig_position = go.Figure(go.Pie(
    labels=pos_goals["Position"],
    values=pos_goals["Goals"],
    hole=0.55,
    marker=dict(
        colors=[pos_colors[p] for p in pos_goals["Position"]],
        line=dict(color="#0f1117", width=3),
    ),
    textinfo="label+percent",
    textfont=dict(size=13, color="#ffffff"),
    hovertemplate="<b>%{label}</b><br>Goals: %{value}<br>Share: %{percent}<extra></extra>",
    rotation=90,
))

total_goals = int(df["Goals"].sum())
fig_position.add_annotation(
    text=f"<b>{total_goals}</b><br><span style='font-size:11px'>TOTAL</span>",
    x=0.5, y=0.5,
    xanchor="center", yanchor="middle",
    showarrow=False,
    font=dict(size=22, color=PALETTE["silver"], family=FONT),
)

fig_position.update_layout(
    **LAYOUT,
    title=dict(
        text="<b>GOALS BY POSITION</b>  <span style='font-size:12px;color:#64748b'>All Players · 2 Seasons</span>",
        font=dict(size=16, color=PALETTE["silver"]),
        x=0.02,
    ),
    legend=dict(
        bgcolor="#1a1d27", bordercolor="#2d3748", borderwidth=1,
        font=dict(size=12),
        orientation="h",
        x=0.5, xanchor="center",
        y=-0.05,
    ),
    height=420,
    margin=MARGIN_DEFAULT,
)

print("✅ All 3 Plotly Figures Created")

# ============================================================
# STEP 4 — HTML DASHBOARD ASSEMBLY
# ============================================================

fig_matrix_html   = fig_matrix.to_html(full_html=False, include_plotlyjs=False, config={"responsive": True})
fig_roi_html      = fig_roi.to_html(full_html=False, include_plotlyjs=False, config={"responsive": True})
fig_position_html = fig_position.to_html(full_html=False, include_plotlyjs=False, config={"responsive": True})

html_dashboard = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Football Analytics · Player Valuation Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Barlow+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:          #0f1117;
      --card:        #15181f;
      --card-border: #1e2330;
      --crimson:     #dc2626;
      --crimson-glow:#ef4444;
      --silver:      #e2e8f0;
      --muted:       #64748b;
      --fw:          #dc2626;
      --mid:         #f59e0b;
      --def:         #3b82f6;
    }}

    body {{
      background: var(--bg);
      color: var(--silver);
      font-family: 'Rajdhani', 'Barlow Condensed', Arial Narrow, Arial, sans-serif;
      min-height: 100vh;
      padding: 0;
      overflow-x: hidden;
    }}

    /* ── Noise texture overlay ── */
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 0;
      opacity: 0.4;
    }}

    /* ── Header ── */
    .header {{
      position: relative;
      z-index: 1;
      padding: 28px 36px 18px;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      gap: 20px;
      background: linear-gradient(135deg, #13161e 0%, #0f1117 100%);
    }}
    .header-badge {{
      width: 44px; height: 44px;
      background: var(--crimson);
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      box-shadow: 0 0 18px rgba(220,38,38,0.45);
      flex-shrink: 0;
    }}
    .header-text h1 {{
      font-size: 26px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      line-height: 1.1;
      color: var(--silver);
    }}
    .header-text h1 span {{ color: var(--crimson); }}
    .header-text p {{
      font-size: 13px;
      color: var(--muted);
      letter-spacing: 1px;
      margin-top: 3px;
    }}
    .header-tag {{
      margin-left: auto;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--muted);
      border: 1px solid var(--card-border);
      border-radius: 4px;
      padding: 5px 12px;
    }}

    /* ── Main Layout ── */
    .dashboard {{
      position: relative;
      z-index: 1;
      padding: 28px 36px 40px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}

    /* ── Section Labels ── */
    .section-label {{
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
      padding-left: 2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .section-label::before {{
      content: "";
      display: inline-block;
      width: 16px; height: 2px;
      background: var(--crimson);
      border-radius: 2px;
    }}

    /* ── KPI Cards ── */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }}
    .kpi-card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-top: 3px solid var(--crimson);
      border-radius: 10px;
      padding: 20px 22px 18px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .kpi-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 30px rgba(220,38,38,0.15);
    }}
    .kpi-card::after {{
      content: "";
      position: absolute;
      bottom: 0; right: 0;
      width: 80px; height: 80px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(220,38,38,0.06) 0%, transparent 70%);
    }}
    .kpi-icon {{
      font-size: 20px;
      margin-bottom: 8px;
    }}
    .kpi-label {{
      font-size: 10px;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .kpi-value {{
      font-size: 17px;
      font-weight: 700;
      color: var(--crimson-glow);
      letter-spacing: 0.5px;
      line-height: 1.3;
      word-break: break-word;
    }}
    .kpi-sub {{
      font-size: 11px;
      color: var(--muted);
      margin-top: 5px;
    }}

    /* ── Chart Cards ── */
    .chart-card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      overflow: hidden;
    }}
    .chart-card .chart-inner {{
      padding: 4px 8px 8px;
    }}

    .chart-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}

    /* ── Footer ── */
    .footer {{
      position: relative;
      z-index: 1;
      text-align: center;
      padding: 16px;
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 1.5px;
      border-top: 1px solid var(--card-border);
    }}
    .footer span {{ color: var(--crimson); }}

    @media (max-width: 900px) {{
      .kpi-row {{ grid-template-columns: 1fr; }}
      .chart-row {{ grid-template-columns: 1fr; }}
      .dashboard {{ padding: 20px 16px 32px; }}
      .header {{ padding: 20px 16px 14px; }}
    }}
  </style>
</head>
<body>

<!-- ── HEADER ── -->
<header class="header">
  <div class="header-badge">⚽</div>
  <div class="header-text">
    <h1>Football <span>Analytics</span> · Player Valuation</h1>
    <p>Performance Intelligence · 2 Seasons · 40 Players</p>
  </div>
  <div class="header-tag">Stadium Control Room</div>
</header>

<!-- ── DASHBOARD ── -->
<main class="dashboard">

  <!-- KPI ROW -->
  <div>
    <div class="section-label">Key Performance Indicators</div>
    <div class="kpi-row">

      <div class="kpi-card">
        <div class="kpi-icon">🥇</div>
        <div class="kpi-label">Top Goal Scorer</div>
        <div class="kpi-value">{kpi_top_scorer}</div>
        <div class="kpi-sub">Highest cumulative goals · All positions</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon">💎</div>
        <div class="kpi-label">Best Value Player</div>
        <div class="kpi-value">{kpi_best_value}</div>
        <div class="kpi-sub">G+A per million € spent</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Biggest Underperformer</div>
        <div class="kpi-value">{kpi_underperformer}</div>
        <div class="kpi-sub">Most negative Goals − xG delta</div>
      </div>

    </div>
  </div>

  <!-- MATRIX CHART — FULL WIDTH -->
  <div>
    <div class="section-label">Finishing Efficiency · All Players</div>
    <div class="chart-card">
      <div class="chart-inner">
        {fig_matrix_html}
      </div>
    </div>
  </div>

  <!-- BOTTOM ROW — ROI & DONUT -->
  <div>
    <div class="section-label">Squad ROI &amp; Position Breakdown</div>
    <div class="chart-row">

      <div class="chart-card">
        <div class="chart-inner">
          {fig_roi_html}
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-inner">
          {fig_position_html}
        </div>
      </div>

    </div>
  </div>

</main>

<!-- ── FOOTER ── -->
<footer class="footer">
  Powered by <span>Plotly · Python · Pandas</span> &nbsp;·&nbsp; Built with ❤ by Senior Sports Data Scientist
</footer>

</body>
</html>"""

# ============================================================
# STEP 5 — EXPORT & AUTO-DOWNLOAD
# ============================================================

output_filename = "Sports_Analytics_Dashboard.html"

with open(output_filename, "w", encoding="utf-8") as f:
    f.write(html_dashboard)

print(f"✅ Dashboard saved → {output_filename}")
print("🚀 Triggering download...")

files.download(output_filename)
