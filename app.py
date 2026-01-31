"""
Dashboard Financeiro Interativo 2026
Aplicação principal Dash com visualizações e análise IA

Autor: Dashboard Financeiro 2026
Versão: 1.0.0
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adiciona diretórios ao path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'src'))
sys.path.insert(0, str(BASE_DIR / 'components'))

from config import DASHBOARD_CONFIG, COLORS, CATEGORIAS_MAP, CHART_CONFIG
from src.data_loader import DataLoader, load_data
from src.analytics_engine import AnalyticsEngine
from components.charts import (
    create_line_chart,
    create_pie_chart,
    create_bar_chart,
    create_treemap,
    create_gauge_chart,
    create_waterfall_chart,
    create_heatmap,
    create_sunburst,
    create_scatter_chart,
    create_forecast_chart
)

# ==================== INICIALIZAÇÃO ====================

# Carrega dados
data_loader = DataLoader()
df = data_loader.load()

# Motor de análises
analytics = AnalyticsEngine(df)

# Inicializa app Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    title=DASHBOARD_CONFIG['title'],
    suppress_callback_exceptions=True
)

server = app.server

# ==================== COMPONENTES AUXILIARES ====================

def create_kpi_card(titulo, valor, icone, variacao=None, cor_classe=""):
    """Cria um card de KPI."""
    variacao_html = ""
    if variacao is not None:
        sinal = "+" if variacao >= 0 else ""
        classe = "up" if variacao >= 0 else "down"
        icone_var = "↑" if variacao >= 0 else "↓"
        variacao_html = html.Span(
            f"{sinal}{variacao:.1f}% {icone_var}",
            className=f"kpi-trend {classe}"
        )
    
    return html.Div([
        html.Div(icone, className="kpi-icon"),
        html.Div(titulo, className="kpi-title"),
        html.Div(f"R$ {valor:,.2f}", className="kpi-value"),
        variacao_html
    ], className=f"kpi-card {cor_classe}")


def create_alert(tipo, icone, titulo, mensagem):
    """Cria um alerta."""
    return html.Div([
        html.Span(icone, className="alert-icon"),
        html.Div([
            html.Div(titulo, className="alert-title"),
            html.Div(mensagem, className="alert-message")
        ], className="alert-content")
    ], className=f"alert {tipo}")


def create_insight_card(insight):
    """Cria um card de insight."""
    return html.Div([
        html.Div(insight.get('icone', '💡'), className="insight-icon"),
        html.Div([
            html.Span(insight.get('prioridade', 'Média'), 
                     className=f"insight-priority {insight.get('prioridade', 'media').lower()}")
        ]),
        html.Div(insight.get('titulo', 'Insight'), className="insight-title"),
        html.Div(insight.get('descricao', ''), className="insight-description"),
        html.Div([
            html.Span("💡 "),
            html.Span(insight.get('acao', ''))
        ], className="insight-action")
    ], className="insight-card")


# ==================== LAYOUT ====================

app.layout = html.Div([
    # Store para dados filtrados
    dcc.Store(id='filtered-data-store'),
    dcc.Store(id='chat-history-store', data=[]),
    
    # Intervalo para atualização
    dcc.Interval(id='interval-update', interval=60000, n_intervals=0),
    
    # Container principal
    html.Div([
        # ===== HEADER =====
        html.Div([
            html.Div([
                html.H1("🚀 Dashboard Financeiro 2026", className="dashboard-title"),
                html.P(f"Análise inteligente com IA | Dados: {df['Data'].min().strftime('%d/%m/%Y')} - {df['Data'].max().strftime('%d/%m/%Y')}", 
                       className="dashboard-subtitle")
            ]),

        ], className="dashboard-header"),
        
        # ===== FILTROS =====
        html.Div([
            html.Div([
                html.Label("📅 Período", className="filter-label"),
                dcc.DatePickerRange(
                    id='date-filter',
                    start_date=df['Data'].min(),
                    end_date=df['Data'].max(),
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], className="filter-group", style={'flex': '2'}),
            
            html.Div([
                html.Label("🏷️ Categoria", className="filter-label"),
                dcc.Dropdown(
                    id='category-filter',
                    options=[{'label': '📌 Todas', 'value': 'all'}] + 
                            [{'label': f"{CATEGORIAS_MAP.get(df[df['Categoria']==cat]['Codigo'].iloc[0], {}).get('icone', '📌')} {cat}", 
                              'value': cat} 
                             for cat in df['Categoria'].unique()],
                    value='all',
                    multi=True,
                    placeholder="Selecione categorias...",
                    style={'backgroundColor': COLORS['bg_tertiary']}
                )
            ], className="filter-group", style={'flex': '2'}),
            
            html.Div([
                html.Label("📋 Tipo", className="filter-label"),
                dcc.Dropdown(
                    id='type-filter',
                    options=[{'label': '📌 Todos', 'value': 'all'}] + 
                            [{'label': t, 'value': t} for t in df['Tipo'].unique()],
                    value='all',
                    multi=True,
                    placeholder="Selecione tipos...",
                    style={'backgroundColor': COLORS['bg_tertiary']}
                )
            ], className="filter-group", style={'flex': '1'}),
            
            html.Div([
                html.Label("💳 Status", className="filter-label"),
                dcc.Dropdown(
                    id='status-filter',
                    options=[
                        {'label': '📌 Todos', 'value': 'all'},
                        {'label': '✅ Pago', 'value': 'Pago'},
                        {'label': '❌ Não Pago', 'value': 'Não Pago'}
                    ],
                    value='all',
                    style={'backgroundColor': COLORS['bg_tertiary']}
                )
            ], className="filter-group", style={'flex': '1'}),
            
            html.Div([
                html.Label("🔍 Buscar", className="filter-label"),
                dcc.Input(
                    id='search-filter',
                    type='text',
                    placeholder="Buscar transação...",
                    className="chat-input",
                    style={'width': '100%'}
                )
            ], className="filter-group", style={'flex': '1'})
        ], className="filters-container"),
        
        # ===== KPIs =====
        html.Div(id='kpi-container', className="kpi-container"),
        
        # ===== ALERTAS =====
        html.Div(id='alerts-container', style={'marginBottom': '24px'}),
        
        # ===== GRÁFICOS LINHA 1 =====
        html.Div([
            html.Div([
                html.H3("📈 Fluxo de Caixa", className="chart-title"),
                dcc.Graph(id='line-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'}),
            
            html.Div([
                html.H3("🍩 Distribuição por Categoria", className="chart-title"),
                dcc.Graph(id='pie-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'})
        ], className="charts-grid"),
        
        # ===== GRÁFICOS LINHA 2 =====
        html.Div([
            html.Div([
                html.H3("📊 Comparativo Mensal", className="chart-title"),
                dcc.Graph(id='bar-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'}),
            
            html.Div([
                html.H3("🌳 Hierarquia de Gastos", className="chart-title"),
                dcc.Graph(id='treemap-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'})
        ], className="charts-grid"),
        
        # ===== GRÁFICOS LINHA 3 =====
        html.Div([
            html.Div([
                html.H3("🔥 Padrão de Gastos por Dia", className="chart-title"),
                dcc.Graph(id='heatmap-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'}),
            
            html.Div([
                html.H3("💧 Evolução do Saldo (Waterfall)", className="chart-title"),
                dcc.Graph(id='waterfall-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'})
        ], className="charts-grid"),
        
        # ===== GRÁFICOS LINHA 4 =====
        html.Div([
            html.Div([
                html.H3("☀️ Visão Hierárquica (Sunburst)", className="chart-title"),
                dcc.Graph(id='sunburst-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'}),
            
            html.Div([
                html.H3("🔮 Previsão de Saldo", className="chart-title"),
                dcc.Graph(id='forecast-chart', config=CHART_CONFIG)
            ], className="chart-container", style={'flex': '1'})
        ], className="charts-grid"),
        
        # ===== GAUGES =====
        html.Div([
            html.Div([
                html.H3("📊 Indicadores de Performance", className="chart-title"),
                html.Div([
                    html.Div([dcc.Graph(id='gauge-economia', config=CHART_CONFIG)], style={'flex': '1'}),
                    html.Div([dcc.Graph(id='gauge-dividas', config=CHART_CONFIG)], style={'flex': '1'}),
                    html.Div([dcc.Graph(id='gauge-meta', config=CHART_CONFIG)], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '16px'})
            ], className="chart-container")
        ]),
        
        # ===== TABELA DE TRANSAÇÕES =====
        html.Div([
            html.Div([
                html.H3("📋 Detalhes de Transações", className="chart-title"),
                html.Div([
                    html.Span(id='table-count', style={'color': COLORS['text_secondary'], 'fontSize': '0.875rem'})
                ], style={'marginBottom': '16px'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
            
            html.Div(id='transactions-table')
        ], className="table-container"),
        
        # ===== INSIGHTS IA =====
        html.Div([
            html.H3("💡 Insights Automáticos", className="chart-title"),
            html.Div(id='insights-container', className="insights-grid")
        ], className="card", style={'marginBottom': '24px'}),
        

        
        # ===== FOOTER =====
        html.Div([
            html.P([
                "Dashboard Financeiro 2026 | ",
                html.Span("Desenvolvido com ", style={'color': COLORS['text_muted']}),
                html.Span("❤️", style={'color': COLORS['danger']}),
                html.Span(" usando Dash, Plotly", style={'color': COLORS['text_muted']})
            ], style={'textAlign': 'center', 'color': COLORS['text_secondary'], 'padding': '24px'})
        ])
        
    ], className="dashboard-container")
])


# ==================== CALLBACKS ====================

@callback(
    [Output('kpi-container', 'children'),
     Output('alerts-container', 'children'),
     Output('line-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('treemap-chart', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('waterfall-chart', 'figure'),
     Output('sunburst-chart', 'figure'),
     Output('forecast-chart', 'figure'),
     Output('gauge-economia', 'figure'),
     Output('gauge-dividas', 'figure'),
     Output('gauge-meta', 'figure'),
     Output('transactions-table', 'children'),
     Output('table-count', 'children'),
     Output('insights-container', 'children')],
    [Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('category-filter', 'value'),
     Input('type-filter', 'value'),
     Input('status-filter', 'value'),
     Input('search-filter', 'value')]
)
def update_dashboard(start_date, end_date, categories, types, status, search):
    """Callback principal que atualiza todos os componentes."""
    
    # Filtra dados
    filtered_df = df.copy()
    
    if start_date:
        filtered_df = filtered_df[filtered_df['Data'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Data'] <= pd.to_datetime(end_date)]
    
    if categories and 'all' not in categories:
        if isinstance(categories, list):
            filtered_df = filtered_df[filtered_df['Categoria'].isin(categories)]
    
    if types and 'all' not in types:
        if isinstance(types, list):
            filtered_df = filtered_df[filtered_df['Tipo'].isin(types)]
    
    if status and status != 'all':
        filtered_df = filtered_df[filtered_df['Pago_ou_nao_pago'] == status]
    
    if search:
        filtered_df = filtered_df[filtered_df['Nome'].str.contains(search, case=False, na=False)]
    
    # Recalcula analytics
    analytics_filtered = AnalyticsEngine(filtered_df)
    kpis = analytics_filtered.get_kpis()
    alertas = analytics_filtered.get_alertas()
    
    # ===== KPIs =====
    kpi_cards = [
        create_kpi_card(
            "💰 Saldo Total",
            kpis['saldo_total'].valor,
            "💰",
            kpis['saldo_total'].variacao_pct,
            "success" if kpis['saldo_total'].valor >= 0 else "danger"
        ),
        create_kpi_card(
            "📈 Receitas",
            kpis['receitas'].valor,
            "📈",
            kpis['receitas'].variacao_pct,
            "success"
        ),
        create_kpi_card(
            "📉 Despesas",
            kpis['despesas'].valor,
            "📉",
            kpis['despesas'].variacao_pct,
            "danger"
        ),
        create_kpi_card(
            "⚖️ Balanço",
            kpis['balanco'].valor,
            "⚖️",
            kpis['balanco'].variacao_pct,
            "success" if kpis['balanco'].valor >= 0 else "danger"
        ),
        create_kpi_card(
            "⚠️ Dívidas Pendentes",
            kpis['dividas_pendentes'].valor,
            "⚠️",
            cor_classe="warning" if kpis['dividas_pendentes'].valor > 0 else "success"
        ),
        create_kpi_card(
            "📊 Taxa de Economia",
            kpis['taxa_economia'].valor,
            "📊",
            cor_classe="success" if kpis['taxa_economia'].valor >= 20 else "warning"
        )
    ]
    
    # ===== ALERTAS =====
    alert_cards = [
        create_alert(a['tipo'], a['icone'], a['titulo'], a['mensagem'])
        for a in alertas[:3]  # Limita a 3 alertas
    ]
    
    # ===== GRÁFICOS =====
    if len(filtered_df) == 0:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Sem dados para exibir", x=0.5, y=0.5, 
                                  font=dict(size=16, color=COLORS['text_muted']),
                                  showarrow=False)
        empty_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        return (kpi_cards, alert_cards, empty_fig, empty_fig, empty_fig, empty_fig,
                empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                empty_fig, html.Div("Sem dados"), "0 transações", [])
    
    line_fig = create_line_chart(filtered_df)
    pie_fig = create_pie_chart(filtered_df)
    bar_fig = create_bar_chart(filtered_df)
    treemap_fig = create_treemap(filtered_df)
    heatmap_fig = create_heatmap(filtered_df)
    waterfall_fig = create_waterfall_chart(filtered_df)
    sunburst_fig = create_sunburst(filtered_df)
    
    # Previsão
    forecast_data = analytics_filtered.prever_proximos_dias(30)
    forecast_fig = create_forecast_chart(filtered_df, forecast_data)
    
    # Gauges
    gauge_economia = create_gauge_chart(
        kpis['taxa_economia'].valor, 20,
        "Taxa de Economia", "%"
    )
    
    dividas_pct = (kpis['dividas_pendentes'].valor / kpis['receitas'].valor * 100) if kpis['receitas'].valor > 0 else 0
    gauge_dividas = create_gauge_chart(
        100 - dividas_pct, 80,
        "Saúde Financeira", "%"
    )
    
    gauge_meta = create_gauge_chart(
        min(kpis['saldo_total'].valor / 5000 * 100, 150), 100,
        "Meta de Saldo (R$5.000)", "%"
    )
    
    # ===== TABELA =====
    table_df = filtered_df[['Data', 'Nome', 'Categoria', 'Tipo', 'Pago_ou_nao_pago', 'Valor', 'Saldo']].copy()
    table_df['Data'] = table_df['Data'].dt.strftime('%d/%m/%Y')
    table_df = table_df.sort_values('Data', ascending=False).head(50)
    
    table_rows = []
    for _, row in table_df.iterrows():
        valor_class = 'valor-positivo' if row['Tipo'] == 'Entrada' else 'valor-negativo'
        table_rows.append(html.Tr([
            html.Td(row['Data']),
            html.Td(row['Nome']),
            html.Td(row['Categoria']),
            html.Td(row['Tipo']),
            html.Td('✅' if row['Pago_ou_nao_pago'] == 'Pago' else '❌'),
            html.Td(f"R$ {row['Valor']:,.2f}", className=valor_class),
            html.Td(f"R$ {row['Saldo']:,.2f}")
        ]))
    
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Data"),
            html.Th("Descrição"),
            html.Th("Categoria"),
            html.Th("Tipo"),
            html.Th("Status"),
            html.Th("Valor"),
            html.Th("Saldo")
        ])),
        html.Tbody(table_rows)
    ], className="data-table")
    
    table_count = f"Mostrando {len(table_df)} de {len(filtered_df)} transações"
    
    # ===== INSIGHTS =====
    insights = analytics_filtered.generate_insights()

    if not insights:
        insights = [
            {'icone': '📊', 'titulo': 'Análise Padrão', 
             'descricao': 'Sem insights automáticos no momento.',
             'acao': 'Verifique os gráficos', 'prioridade': 'Baixa'}
        ]
    
    insight_cards = [create_insight_card(i) for i in insights[:4]]
    
    return (kpi_cards, alert_cards, line_fig, pie_fig, bar_fig, treemap_fig,
            heatmap_fig, waterfall_fig, sunburst_fig, forecast_fig,
            gauge_economia, gauge_dividas, gauge_meta,
            table, table_count, insight_cards)





# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Dashboard Financeiro 2026")
    print("="*60)
    print(f"📊 Dados carregados: {len(df)} transações")
    print(f"📅 Período: {df['Data'].min().strftime('%d/%m/%Y')} - {df['Data'].max().strftime('%d/%m/%Y')}")
    print(f"🌐 Acessar: http://{DASHBOARD_CONFIG['host']}:{DASHBOARD_CONFIG['port']}")
    print("="*60 + "\n")
    
    app.run(
        host=DASHBOARD_CONFIG['host'],
        port=DASHBOARD_CONFIG['port'],
        debug=DASHBOARD_CONFIG['debug']
    )
