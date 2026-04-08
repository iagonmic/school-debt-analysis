import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# ─── Dados ────────────────────────────────────────────────────────────────────
df = pd.read_parquet("processed/fato_pagamento.parquet")
df["dt_vencimento"] = pd.to_datetime(df["dt_vencimento"], errors="coerce")
df["ano"] = df["dt_vencimento"].dt.year.astype("Int64")
df["mes_num"] = df["dt_vencimento"].dt.month

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março",    4: "Abril",
    5: "Maio",    6: "Junho",    7: "Julho",      8: "Agosto",
    9: "Setembro",10: "Outubro", 11: "Novembro",  12: "Dezembro",
}
df["mes_nome"] = df["mes_num"].map(MESES_PT)

TURMAS = sorted(df["turma"].dropna().unique().tolist())

# ─── Paleta ───────────────────────────────────────────────────────────────────
BG       = "#0d1f1a"
SURFACE  = "#142920"
SURFACE2 = "#1c3529"
BORDER   = "#243d33"
GREEN    = "#3dba7f"
GREEN_LT = "#5dd49a"
AMBER    = "#f5c842"
RED      = "#e05252"
TEXT     = "#d4ede5"
MUTED    = "#6b8f7e"


# ─── Layout base para gráficos (fundo escuro explícito) ───────────────────────
def base_layout(legend=False):
    layout = dict(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(color=MUTED, size=11),
        margin=dict(l=50, r=20, t=38, b=40),
        showlegend=legend,
        xaxis=dict(
            showgrid=True, gridcolor=BORDER, gridwidth=1,
            zeroline=False, tickfont=dict(color=MUTED, size=10),
            linecolor=BORDER, showline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=BORDER, gridwidth=1,
            zeroline=False, tickfont=dict(color=MUTED, size=10),
            linecolor=BORDER, showline=False,
        ),
        hoverlabel=dict(
            bgcolor=SURFACE2, bordercolor=BORDER,
            font=dict(color=TEXT, size=12),
        ),
        title=dict(
            font=dict(color=TEXT, size=12),
            x=0.5, xanchor="center", y=0.97,
        ),
    )
    if legend:
        layout["legend"] = dict(
            font=dict(color=TEXT, size=11),
            bgcolor="rgba(0,0,0,0)",
            x=1.0, y=0.5, xanchor="left",
        )
    return layout


# ─── Formatação ───────────────────────────────────────────────────────────────
def fmt_mil(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f} Mi"
    if v >= 1_000:
        return f"{v/1_000:.2f} Mil".replace(".", ",")
    return f"{v:.2f}".replace(".", ",")


# ─── Filtro ───────────────────────────────────────────────────────────────────
def apply_filter(ano, turma):
    d = df.copy()
    if ano and ano != "todos":
        d = d[d["ano"] == int(ano)]
    if turma and turma != "todos":
        d = d[d["turma"] == turma]
    return d


# ─── Componentes ─────────────────────────────────────────────────────────────
def kpi_card(title, value, subtitle=None):
    children = [
        html.P(title, style={
            "fontFamily": "monospace", "fontSize": "10px", "fontWeight": "600",
            "letterSpacing": "0.1em", "textTransform": "uppercase",
            "color": MUTED, "marginBottom": "8px", "margin": "0 0 8px 0",
        }),
        html.P(value, style={
            "fontFamily": "monospace", "fontSize": "20px", "fontWeight": "700",
            "color": TEXT, "margin": "0",
        }),
    ]
    if subtitle:
        children.append(html.P(subtitle, style={
            "fontFamily": "monospace", "fontSize": "9px",
            "color": MUTED, "marginTop": "4px",
        }))
    return html.Div(children, style={
        "background": SURFACE,
        "border": f"1px solid {BORDER}",
        "borderRadius": "8px",
        "padding": "16px 20px",
        "borderTop": f"2px solid {GREEN}",
        "flex": "1",
        "minWidth": "0",
    })


def chart_card(chart_id, height=None):
    graph_style = {"height": f"{height}px"} if height else {"height": "100%", "minHeight": "220px"}
    return html.Div([
        dcc.Graph(
            id=chart_id,
            config={"displayModeBar": False},
            style=graph_style,
        ),
    ], style={
        "background": SURFACE,
        "border": f"1px solid {BORDER}",
        "borderRadius": "8px",
        "overflow": "hidden",
        "flex": "1",
        "minWidth": "0",
        "display": "flex",
        "flexDirection": "column",
    })


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def make_sidebar(active="dashboard"):
    DD = {
        "backgroundColor": SURFACE2,
        "border": f"1px solid {BORDER}",
        "borderRadius": "6px",
        "color": TEXT,
        "fontFamily": "monospace",
        "fontSize": "13px",
    }
    return html.Div([
        html.Div([
            html.P("Ano", style={
                "fontFamily": "monospace", "fontSize": "12px", "fontWeight": "600",
                "color": MUTED, "marginBottom": "6px",
            }),
            dcc.Dropdown(
                id="filter-ano",
                options=[
                    {"label": "Todos", "value": "todos"},
                    {"label": "2023",  "value": "2023"},
                    {"label": "2024",  "value": "2024"},
                    {"label": "2025",  "value": "2025"},
                ],
                value="todos", clearable=False, style=DD,
            ),
        ], style={"marginBottom": "20px"}),

        html.Div([
            html.P("Turma", style={
                "fontFamily": "monospace", "fontSize": "12px", "fontWeight": "600",
                "color": MUTED, "marginBottom": "6px",
            }),
            dcc.Dropdown(
                id="filter-turma",
                options=[{"label": "Todos", "value": "todos"}] +
                        [{"label": t, "value": t} for t in TURMAS],
                value="todos", clearable=False, style=DD,
            ),
        ], style={"marginBottom": "24px"}),

        html.Hr(style={"borderColor": BORDER, "margin": "0 0 16px 0"}),

        html.A("● Dashboard", href="/", style={
            "display": "block", "fontFamily": "monospace", "fontSize": "12px",
            "fontWeight": "600",
            "color": GREEN if active == "dashboard" else MUTED,
            "textDecoration": "none", "padding": "8px 10px", "borderRadius": "6px",
            "background": SURFACE2 if active == "dashboard" else "transparent",
            "borderLeft": f"2px solid {GREEN}" if active == "dashboard" else "2px solid transparent",
            "marginBottom": "4px",
        }),
        html.A("◐ Simulação", href="/simulacao", style={
            "display": "block", "fontFamily": "monospace", "fontSize": "12px",
            "fontWeight": "600",
            "color": GREEN if active == "simulacao" else MUTED,
            "textDecoration": "none", "padding": "8px 10px", "borderRadius": "6px",
            "background": SURFACE2 if active == "simulacao" else "transparent",
            "borderLeft": f"2px solid {GREEN}" if active == "simulacao" else "2px solid transparent",
        }),
    ], style={
        "width": "185px", "minWidth": "185px", "height": "100%",
        "background": "#0a1914", "borderRight": f"1px solid {BORDER}",
        "padding": "24px 16px", "boxSizing": "border-box",
        "overflowY": "auto",
    })


# ─── Páginas ──────────────────────────────────────────────────────────────────
def dashboard_page():
    return html.Div([
        make_sidebar("dashboard"),
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.Div("Dashboard", style={
                        "fontFamily": "monospace", "fontSize": "22px",
                        "fontWeight": "700", "color": TEXT,
                    }),
                    html.Div("Análise de Inadimplência Escolar", style={
                        "fontFamily": "monospace", "fontSize": "11px",
                        "color": MUTED, "marginTop": "2px",
                    }),
                ]),
                html.A("≡ Simulação →", href="/simulacao", style={
                    "background": GREEN, "color": "#0a1914",
                    "fontFamily": "monospace", "fontWeight": "700",
                    "fontSize": "12px", "letterSpacing": "0.05em",
                    "padding": "9px 18px", "borderRadius": "7px",
                    "textDecoration": "none",
                }),
            ], style={
                "display": "flex", "justifyContent": "space-between",
                "alignItems": "flex-end", "paddingBottom": "18px",
                "borderBottom": f"1px solid {BORDER}", "marginBottom": "18px",
            }),

            # KPIs
            html.Div(id="kpi-row", style={"display": "flex", "gap": "10px", "marginBottom": "14px"}),

            # Gráficos linha 1
            html.Div([
                chart_card("chart-mes"),
                chart_card("chart-evolucao"),
                chart_card("chart-turma"),
            ], style={"display": "flex", "gap": "10px", "marginBottom": "10px", "flex": "1", "minHeight": "0"}),

            # Gráficos linha 2
            html.Div([
                chart_card("chart-relacao"),
                chart_card("chart-alunos"),
                chart_card("chart-turno"),
            ], style={"display": "flex", "gap": "10px", "flex": "1", "minHeight": "0"}),

        ], style={
            "flex": "1", "padding": "24px 28px", "minWidth": "0", "overflowX": "hidden",
            "display": "flex", "flexDirection": "column",
        }),
    ], style={"display": "flex", "height": "100vh", "background": BG, "overflow": "hidden"})


def simulation_page():
    return html.Div([
        html.Div([
            # Header
            html.Div([
                html.A("← Voltar ao Dashboard", href="/", style={
                    "fontFamily": "monospace", "fontSize": "12px", "fontWeight": "600",
                    "color": MUTED, "textDecoration": "none",
                    "background": SURFACE2, "border": f"1px solid {BORDER}",
                    "padding": "8px 14px", "borderRadius": "7px",
                }),
                html.Div([
                    html.Span("◐ ", style={"color": GREEN, "fontSize": "20px"}),
                    html.Span("Simulação", style={
                        "fontFamily": "monospace", "fontSize": "22px",
                        "fontWeight": "700", "color": TEXT,
                    }),
                ], style={"display": "flex", "alignItems": "center", "gap": "4px"}),
            ], style={
                "display": "flex", "justifyContent": "space-between",
                "alignItems": "center", "paddingBottom": "18px",
                "borderBottom": f"1px solid {BORDER}", "marginBottom": "18px",
            }),

            # Slider
            html.Div([
                html.Div([
                    html.Label("Fator de Simulação", style={
                        "fontFamily": "monospace", "fontSize": "12px",
                        "fontWeight": "600", "color": TEXT,
                        "whiteSpace": "nowrap", "marginRight": "20px",
                    }),
                    html.Div(
                        dcc.Slider(
                            id="sim-slider", min=10, max=200, step=5, value=100,
                            marks={10: "10%", 50: "50%", 100: "100%", 150: "150%", 200: "200%"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                        style={"flex": "1"},
                    ),
                    html.Span(id="sim-pct-label", style={
                        "fontFamily": "monospace", "fontSize": "22px",
                        "fontWeight": "700", "color": GREEN,
                        "minWidth": "70px", "textAlign": "right",
                        "marginLeft": "20px",
                    }),
                ], style={"display": "flex", "alignItems": "center"}),
            ], style={
                "background": SURFACE, "border": f"1px solid {BORDER}",
                "borderRadius": "8px", "padding": "20px 24px", "marginBottom": "14px",
            }),

            # KPIs simulação
            html.Div(id="sim-kpi-row", style={"display": "flex", "gap": "10px", "marginBottom": "14px"}),

            # Gráficos 2 colunas
            html.Div([
                chart_card("sim-chart-mes",     height=300),
                chart_card("sim-chart-evolucao", height=300),
            ], style={"display": "flex", "gap": "10px", "marginBottom": "10px"}),

            html.Div([
                chart_card("sim-chart-turma",  height=300),
                chart_card("sim-chart-alunos", height=300),
            ], style={"display": "flex", "gap": "10px"}),

        ], style={"flex": "1", "padding": "24px 28px", "minWidth": "0"}),
    ], style={"display": "flex", "minHeight": "100vh", "background": BG})


# ─── App root ─────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
)
app.title = "Dashboard Inadimplência"
server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content", style={"height": "100vh", "overflow": "hidden"}),
], style={"background": BG, "height": "100vh", "overflow": "hidden"})


# ─── Roteamento ───────────────────────────────────────────────────────────────
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname and "/simulacao" in pathname:
        return simulation_page()
    return dashboard_page()


# ─── Callbacks Dashboard ──────────────────────────────────────────────────────
@app.callback(
    Output("kpi-row",        "children"),
    Output("chart-mes",      "figure"),
    Output("chart-evolucao", "figure"),
    Output("chart-turma",    "figure"),
    Output("chart-relacao",  "figure"),
    Output("chart-alunos",   "figure"),
    Output("chart-turno",    "figure"),
    Input("filter-ano",   "value"),
    Input("filter-turma", "value"),
)
def update_dashboard(ano, turma):
    d       = apply_filter(ano, turma)
    inadimp = d[d["status"] == "Pendente"]
    pago    = d[d["status"] == "Pago"]

    # KPIs
    total_inadimp = inadimp["valor_atual"].sum()
    ticket_medio  = inadimp.groupby("matricula")["valor_atual"].sum().mean() if len(inadimp) else 0
    arrecadado    = pago["vlr_pago"].sum()
    taxa          = len(inadimp) / len(d) * 100 if len(d) else 0
    mes_pior      = inadimp.groupby("mes_nome")["valor_atual"].sum().idxmax() if len(inadimp) else "—"

    kpis = [
        kpi_card("Total Inadimplência",    fmt_mil(total_inadimp)),
        kpi_card("Ticket Médio",           fmt_mil(ticket_medio) if ticket_medio else "—"),
        kpi_card("Taxa Inadimplência",     f"{taxa:.2f}%".replace(".", ",")),
        kpi_card("Valor Arrecadado",       fmt_mil(arrecadado)),
        kpi_card("Mês Maior Inadimplente", mes_pior),
    ]

    # Chart 1 — Inadimplência por Mês (barra H)
    mes_df = (
        inadimp.groupby(["mes_num", "mes_nome"])["valor_atual"]
        .sum().reset_index().sort_values("valor_atual", ascending=True)
    )
    l1 = base_layout()
    l1["title"]["text"] = "Inadimplência por Mês"
    l1["xaxis"]["tickformat"] = ".2s"
    l1["yaxis"]["showgrid"] = False
    l1["margin"] = dict(l=75, r=20, t=38, b=30)
    fig_mes = go.Figure(go.Bar(
        x=mes_df["valor_atual"], y=mes_df["mes_nome"], orientation="h",
        marker=dict(color=GREEN, line=dict(width=0)),
        hovertemplate="%{y}: R$ %{x:,.0f}<extra></extra>",
    ))
    fig_mes.update_layout(**l1)

    # Chart 2 — Evolução (linha + área)
    evo_df = inadimp.groupby("ano")["valor_atual"].sum().reset_index()
    evo_df["ano"] = evo_df["ano"].astype(str)
    l2 = base_layout()
    l2["title"]["text"] = "Evolução Inadimplência"
    l2["yaxis"]["tickformat"] = ".2s"
    l2["margin"] = dict(l=55, r=20, t=38, b=30)
    fig_evo = go.Figure(go.Scatter(
        x=evo_df["ano"], y=evo_df["valor_atual"],
        mode="lines+markers",
        line=dict(color=GREEN, width=3),
        marker=dict(color=GREEN, size=9, line=dict(color=BG, width=2)),
        fill="tozeroy", fillcolor="rgba(61,186,127,0.13)",
        hovertemplate="%{x}: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_evo.update_layout(**l2)

    # Chart 3 — Por Turma (barra V)
    turma_df = (
        inadimp.groupby("turma")["valor_atual"]
        .sum().reset_index().sort_values("valor_atual", ascending=False).head(8)
    )
    turma_df["label"] = turma_df["turma"].str.replace("INFANTIL", "Inf.", regex=False)
    l3 = base_layout()
    l3["title"]["text"] = "Total Inadimplente por Turma"
    l3["yaxis"]["tickformat"] = ".2s"
    l3["xaxis"]["showgrid"] = False
    l3["margin"] = dict(l=55, r=10, t=38, b=55)
    fig_turma = go.Figure(go.Bar(
        x=turma_df["label"], y=turma_df["valor_atual"],
        marker=dict(
            color=turma_df["valor_atual"],
            colorscale=[[0, GREEN], [1, GREEN_LT]], line=dict(width=0),
        ),
        hovertemplate="%{x}: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_turma.update_layout(**l3)
    fig_turma.update_xaxes(tickfont=dict(size=9))

    # Chart 4 — Pie pago/pendente
    rel = d.groupby("status")["matricula"].count().reset_index()
    rel.columns = ["status", "qtd"]
    l4 = base_layout(legend=True)
    l4["title"]["text"] = "Relação Adimp/Inadimp"
    l4["margin"] = dict(l=10, r=90, t=38, b=10)
    del l4["xaxis"]; del l4["yaxis"]
    fig_rel = go.Figure(go.Pie(
        labels=rel["status"], values=rel["qtd"], hole=0,
        marker=dict(colors=[GREEN, RED], line=dict(color=BG, width=2)),
        textfont=dict(color=TEXT, size=11), textinfo="percent",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig_rel.update_layout(**l4)

    # Chart 5 — Alunos inadimplentes (barra H)
    alunos_df = (
        inadimp.groupby("matricula")["valor_atual"]
        .sum().reset_index().sort_values("valor_atual", ascending=True).tail(10)
    )
    alunos_df["matricula"] = alunos_df["matricula"].astype(str)
    l5 = base_layout()
    l5["title"]["text"] = "Alunos mais inadimplentes"
    l5["xaxis"]["tickformat"] = ".2s"
    l5["yaxis"]["showgrid"] = False
    l5["margin"] = dict(l=45, r=20, t=38, b=30)
    fig_alunos = go.Figure(go.Bar(
        x=alunos_df["valor_atual"], y=alunos_df["matricula"], orientation="h",
        marker=dict(color=GREEN_LT, line=dict(width=0)),
        hovertemplate="Aluno %{y}: R$ %{x:,.0f}<extra></extra>",
    ))
    fig_alunos.update_layout(**l5)

    # Chart 6 — Donut turno
    turno_df = inadimp.groupby("turno")["valor_atual"].sum().reset_index()
    l6 = base_layout(legend=True)
    l6["title"]["text"] = "Inadimplência por Turno"
    l6["margin"] = dict(l=10, r=90, t=38, b=10)
    del l6["xaxis"]; del l6["yaxis"]
    fig_turno = go.Figure(go.Pie(
        labels=turno_df["turno"], values=turno_df["valor_atual"], hole=0.45,
        marker=dict(colors=[GREEN, AMBER], line=dict(color=BG, width=2)),
        textfont=dict(color=TEXT, size=11), textinfo="percent",
        hovertemplate="%{label}: R$ %{value:,.0f}<extra></extra>",
    ))
    fig_turno.update_layout(**l6)

    return kpis, fig_mes, fig_evo, fig_turma, fig_rel, fig_alunos, fig_turno


# ─── Callbacks Simulação ──────────────────────────────────────────────────────
BASE_MES    = [("Julho",18000),("Outubro",25000),("Setembro",32000),("Dezembro",122000)]
BASE_EVO    = [("2023",20000),("2024",95000),("2025",197000)]
BASE_TURMA  = [("1º Ano",22000),("2º Ano",18000),("Inf. II(B)",15000),("4º Ano",8000),("3º Ano",5000)]
BASE_ALUNOS = [("820",7440),("982",6200),("805",5800),("882",4880),("903",4880),
               ("1033",4680),("981",4680),("698",4600),("969",4600),("132",4600)]
BASE_TOT = 197220; BASE_TKT = 512.25; BASE_ARR = 16740


@app.callback(
    Output("sim-pct-label",     "children"),
    Output("sim-kpi-row",       "children"),
    Output("sim-chart-mes",     "figure"),
    Output("sim-chart-evolucao","figure"),
    Output("sim-chart-turma",   "figure"),
    Output("sim-chart-alunos",  "figure"),
    Input("sim-slider", "value"),
)
def update_simulation(factor):
    factor = factor or 100
    m = factor / 100

    kpis = [
        kpi_card("Total Inadimplência", fmt_mil(BASE_TOT * m), f"Fator: {factor}%"),
        kpi_card("Ticket Médio",        fmt_mil(BASE_TKT * m)),
        kpi_card("Valor Arrecadado",    fmt_mil(BASE_ARR * m)),
    ]

    # Mês
    mes_s = sorted(BASE_MES, key=lambda x: x[1])
    lm = base_layout()
    lm["title"]["text"] = "Inadimplência por Mês"
    lm["xaxis"]["tickformat"] = ".2s"
    lm["yaxis"]["showgrid"] = False
    lm["margin"] = dict(l=75, r=20, t=38, b=30)
    fig_mes = go.Figure(go.Bar(
        x=[round(v*m) for _,v in mes_s], y=[n for n,_ in mes_s], orientation="h",
        marker=dict(color=GREEN, line=dict(width=0)),
        hovertemplate="%{y}: R$ %{x:,.0f}<extra></extra>",
    ))
    fig_mes.update_layout(**lm)

    # Evolução
    le = base_layout()
    le["title"]["text"] = "Evolução Inadimplência"
    le["yaxis"]["tickformat"] = ".2s"
    le["margin"] = dict(l=55, r=20, t=38, b=30)
    fig_evo = go.Figure(go.Scatter(
        x=[a for a,_ in BASE_EVO], y=[round(v*m) for _,v in BASE_EVO],
        mode="lines+markers",
        line=dict(color=GREEN, width=3),
        marker=dict(color=GREEN, size=9, line=dict(color=BG, width=2)),
        fill="tozeroy", fillcolor="rgba(61,186,127,0.13)",
        hovertemplate="%{x}: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_evo.update_layout(**le)

    # Turma
    turma_s = sorted(BASE_TURMA, key=lambda x: x[1], reverse=True)
    vals_t = [round(v*m) for _,v in turma_s]
    lt = base_layout()
    lt["title"]["text"] = "Total Inadimplente por Turma"
    lt["yaxis"]["tickformat"] = ".2s"
    lt["xaxis"]["showgrid"] = False
    lt["margin"] = dict(l=30, r=10, t=38, b=55)
    fig_turma = go.Figure(go.Bar(
        x=[n for n,_ in turma_s], y=vals_t,
        marker=dict(color=vals_t, colorscale=[[0,GREEN],[1,GREEN_LT]], line=dict(width=0)),
        hovertemplate="%{x}: R$ %{y:,.0f}<extra></extra>",
    ))
    fig_turma.update_layout(**lt)

    # Alunos
    alunos_s = sorted(BASE_ALUNOS, key=lambda x: x[1])
    la = base_layout()
    la["title"]["text"] = "Alunos mais inadimplentes"
    la["xaxis"]["tickformat"] = ".2s"
    la["yaxis"]["showgrid"] = False
    la["margin"] = dict(l=45, r=20, t=38, b=30)
    fig_alunos = go.Figure(go.Bar(
        x=[round(v*m) for _,v in alunos_s], y=[n for n,_ in alunos_s], orientation="h",
        marker=dict(color=GREEN_LT, line=dict(width=0)),
        hovertemplate="Aluno %{y}: R$ %{x:,.0f}<extra></extra>",
    ))
    fig_alunos.update_layout(**la)

    return f"{factor}%", kpis, fig_mes, fig_evo, fig_turma, fig_alunos


if __name__ == "__main__":
    app.run(debug=False, port=8050)