"""
Componentes de gráficos para o Dashboard
Dashboard Financeiro 2026
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COLORS, CHART_LAYOUT, CHART_CONFIG, CATEGORIAS_MAP


def create_line_chart(
    df: pd.DataFrame,
    title: str = "Fluxo de Caixa"
) -> go.Figure:
    """
    Cria gráfico de linhas para fluxo de caixa ao longo do tempo.
    
    Args:
        df: DataFrame com série temporal
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    fig = go.Figure()
    
    # Agrupa por data
    ts = df.groupby('Data').agg({
        'ValorComSinal': 'sum',
        'Valor': 'sum'
    }).reset_index()
    
    # Receitas
    receitas = df[df['Tipo'] == 'Entrada'].groupby('Data')['Valor'].sum().reset_index()
    receitas.columns = ['Data', 'Receitas']
    
    # Despesas
    despesas = df[df['Tipo'] == 'Saída'].groupby('Data')['Valor'].sum().reset_index()
    despesas.columns = ['Data', 'Despesas']
    
    # Merge
    ts = ts.merge(receitas, on='Data', how='left').merge(despesas, on='Data', how='left')
    ts = ts.fillna(0)
    ts['SaldoAcumulado'] = ts['ValorComSinal'].cumsum()
    
    # Área de Receitas
    fig.add_trace(go.Scatter(
        x=ts['Data'],
        y=ts['Receitas'],
        name='Receitas',
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(color=COLORS['success'], width=2),
        mode='lines',
        hovertemplate='<b>Receitas</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Área de Despesas
    fig.add_trace(go.Scatter(
        x=ts['Data'],
        y=ts['Despesas'],
        name='Despesas',
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(color=COLORS['danger'], width=2),
        mode='lines',
        hovertemplate='<b>Despesas</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Linha de Saldo Acumulado
    fig.add_trace(go.Scatter(
        x=ts['Data'],
        y=ts['SaldoAcumulado'],
        name='Saldo Acumulado',
        line=dict(color=COLORS['info'], width=3, dash='dot'),
        mode='lines+markers',
        marker=dict(size=6),
        hovertemplate='<b>Saldo</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Aplicar layout base
    layout = dict(**CHART_LAYOUT)
    layout['title'] = dict(text=f"📈 {title}", font=dict(size=16))
    layout['hovermode'] = 'x unified'
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1,
        bgcolor='rgba(0,0,0,0)',
        font={'color': '#CBD5E1'}
    )
    fig.update_layout(**layout)
    
    return fig


def create_pie_chart(
    df: pd.DataFrame,
    title: str = "Distribuição por Categoria"
) -> go.Figure:
    """
    Cria gráfico de pizza/donut para distribuição por categoria.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Agrupa por categoria
    cat_data = df.groupby('Categoria')['Valor'].sum().reset_index()
    cat_data = cat_data.sort_values('Valor', ascending=False)
    
    # Cores por categoria
    colors = [CATEGORIAS_MAP.get(
        df[df['Categoria'] == cat]['Codigo'].iloc[0] if len(df[df['Categoria'] == cat]) > 0 else 0,
        {}
    ).get('cor', '#6B7280') for cat in cat_data['Categoria']]
    
    fig = go.Figure(data=[go.Pie(
        labels=cat_data['Categoria'],
        values=cat_data['Valor'],
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='rgba(0,0,0,0.3)', width=2)),
        textinfo='percent+label',
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    # Adiciona texto central
    fig.add_annotation(
        text=f"<b>R$ {cat_data['Valor'].sum():,.0f}</b><br><span style='font-size:10px'>Total</span>",
        x=0.5, y=0.5,
        font=dict(size=16, color=COLORS['text_primary']),
        showarrow=False
    )
    
    layout = dict(**CHART_LAYOUT)
    layout['title'] = dict(text=f"🍩 {title}", font=dict(size=16))
    layout['showlegend'] = True
    layout['legend'] = dict(
        orientation='v',
        yanchor='middle',
        y=0.5,
        xanchor='left',
        x=1.05,
        bgcolor='rgba(0,0,0,0)',
        font={'color': '#CBD5E1'}
    )
    fig.update_layout(**layout)
    
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    title: str = "Comparativo Mensal"
) -> go.Figure:
    """
    Cria gráfico de barras empilhadas por mês.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Agrupa por mês e categoria
    df['MesAno'] = df['Data'].dt.strftime('%Y-%m')
    monthly = df.groupby(['MesAno', 'Categoria'])['Valor'].sum().reset_index()
    
    fig = go.Figure()
    
    categorias = monthly['Categoria'].unique()
    
    for cat in categorias:
        cat_data = monthly[monthly['Categoria'] == cat]
        cor = CATEGORIAS_MAP.get(
            df[df['Categoria'] == cat]['Codigo'].iloc[0] if len(df[df['Categoria'] == cat]) > 0 else 0,
            {}
        ).get('cor', '#6B7280')
        
        fig.add_trace(go.Bar(
            x=cat_data['MesAno'],
            y=cat_data['Valor'],
            name=cat,
            marker_color=cor,
            hovertemplate=f'<b>{cat}</b><br>Mês: %{{x}}<br>Valor: R$ %{{y:,.2f}}<extra></extra>'
        ))
    
    layout = dict(**CHART_LAYOUT)
    layout['title'] = dict(text=f"📊 {title}", font=dict(size=16))
    layout['barmode'] = 'stack'
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1,
        bgcolor='rgba(0,0,0,0)',
        font={'color': '#CBD5E1'}
    )
    fig.update_layout(**layout)
    
    return fig


def create_treemap(
    df: pd.DataFrame,
    title: str = "Hierarquia de Gastos"
) -> go.Figure:
    """
    Cria treemap para visualização hierárquica.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Filtra apenas gastos
    gastos = df[df['Tipo'].isin(['Saída', 'Dívida', 'Dívida Parcial'])]
    
    fig = px.treemap(
        gastos,
        path=['Tipo', 'Categoria', 'Nome'],
        values='Valor',
        color='Categoria',
        color_discrete_map={cat: CATEGORIAS_MAP.get(
            gastos[gastos['Categoria'] == cat]['Codigo'].iloc[0] if len(gastos[gastos['Categoria'] == cat]) > 0 else 0,
            {}
        ).get('cor', '#6B7280') for cat in gastos['Categoria'].unique()}
    )
    
    fig.update_layout(
        title=dict(text=f"🌳 {title}", font=dict(size=16)),
        **CHART_LAYOUT
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percentRoot:.1%}<extra></extra>'
    )
    
    return fig


def create_gauge_chart(
    valor: float,
    meta: float,
    titulo: str,
    unidade: str = "%"
) -> go.Figure:
    """
    Cria gráfico de gauge/velocímetro.
    
    Args:
        valor: Valor atual
        meta: Meta a atingir
        titulo: Título do gauge
        unidade: Unidade de medida
        
    Returns:
        Figura Plotly
    """
    # Determina cor baseada no progresso
    if valor >= meta:
        cor = COLORS['success']
    elif valor >= meta * 0.7:
        cor = COLORS['warning']
    else:
        cor = COLORS['danger']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        delta={'reference': meta, 'relative': True},
        number={'suffix': unidade, 'font': {'size': 24}},
        title={'text': titulo, 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, max(meta * 1.5, valor * 1.2)]},
            'bar': {'color': cor},
            'steps': [
                {'range': [0, meta * 0.5], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [meta * 0.5, meta * 0.8], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [meta * 0.8, meta * 1.5], 'color': 'rgba(16, 185, 129, 0.2)'}
            ],
            'threshold': {
                'line': {'color': COLORS['text_primary'], 'width': 2},
                'thickness': 0.75,
                'value': meta
            }
        }
    ))
    
    fig.update_layout(
        **CHART_LAYOUT,
        height=250
    )
    
    return fig


def create_waterfall_chart(
    df: pd.DataFrame,
    title: str = "Evolução do Saldo"
) -> go.Figure:
    """
    Cria gráfico waterfall para evolução do saldo.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Agrupa por semana
    df['Semana'] = df['Data'].dt.strftime('%d/%m')
    weekly = df.groupby('Semana')['ValorComSinal'].sum().reset_index()
    
    # Prepara dados para waterfall
    measures = ['absolute'] + ['relative'] * (len(weekly) - 1) + ['total']
    
    x_values = ['Início'] + weekly['Semana'].tolist() + ['Final']
    y_values = [0] + weekly['ValorComSinal'].tolist() + [weekly['ValorComSinal'].sum()]
    
    fig = go.Figure(go.Waterfall(
        x=x_values,
        y=y_values,
        measure=['absolute'] + ['relative'] * len(weekly) + ['total'],
        increasing={'marker': {'color': COLORS['success']}},
        decreasing={'marker': {'color': COLORS['danger']}},
        totals={'marker': {'color': COLORS['info']}},
        connector={'line': {'color': COLORS['text_muted']}},
        hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=f"💧 {title}", font=dict(size=16)),
        **CHART_LAYOUT,
        showlegend=False
    )
    
    return fig


def create_heatmap(
    df: pd.DataFrame,
    title: str = "Padrão de Gastos"
) -> go.Figure:
    """
    Cria heatmap de gastos por dia da semana e hora.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Prepara dados
    df = df.copy()
    df['DiaSemana'] = df['Data'].dt.day_name()
    df['SemanaDoMes'] = ((df['Data'].dt.day - 1) // 7) + 1
    
    # Ordena dias da semana
    dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Pivot para heatmap
    heatmap_data = df.pivot_table(
        values='Valor',
        index='SemanaDoMes',
        columns='DiaSemana',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reordena colunas
    heatmap_data = heatmap_data.reindex(columns=[d for d in dias_ordem if d in heatmap_data.columns])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=dias_pt[:len(heatmap_data.columns)],
        y=[f'Semana {i}' for i in heatmap_data.index],
        colorscale=[
            [0, 'rgba(16, 185, 129, 0.1)'],
            [0.5, 'rgba(245, 158, 11, 0.5)'],
            [1, 'rgba(239, 68, 68, 0.8)']
        ],
        hovertemplate='<b>%{x}</b> - %{y}<br>Total: R$ %{z:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=f"🔥 {title}", font=dict(size=16)),
        **CHART_LAYOUT
    )
    
    return fig


def create_sunburst(
    df: pd.DataFrame,
    title: str = "Visão Hierárquica"
) -> go.Figure:
    """
    Cria gráfico sunburst para drill-down hierárquico.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    fig = px.sunburst(
        df,
        path=['Tipo', 'Categoria', 'Nome'],
        values='Valor',
        color='Categoria',
        color_discrete_map={cat: CATEGORIAS_MAP.get(
            df[df['Categoria'] == cat]['Codigo'].iloc[0] if len(df[df['Categoria'] == cat]) > 0 else 0,
            {}
        ).get('cor', '#6B7280') for cat in df['Categoria'].unique()}
    )
    
    fig.update_layout(
        title=dict(text=f"☀️ {title}", font=dict(size=16)),
        **CHART_LAYOUT
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>'
    )
    
    return fig


def create_scatter_chart(
    df: pd.DataFrame,
    title: str = "Correlação Valor x Frequência"
) -> go.Figure:
    """
    Cria gráfico de dispersão para análise de correlação.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    # Agrupa por categoria
    cat_stats = df.groupby('Categoria').agg({
        'Valor': ['sum', 'mean', 'count']
    }).reset_index()
    cat_stats.columns = ['Categoria', 'Total', 'Media', 'Quantidade']
    
    # Cores
    cat_stats['Cor'] = cat_stats['Categoria'].apply(
        lambda x: CATEGORIAS_MAP.get(
            df[df['Categoria'] == x]['Codigo'].iloc[0] if len(df[df['Categoria'] == x]) > 0 else 0,
            {}
        ).get('cor', '#6B7280')
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cat_stats['Quantidade'],
        y=cat_stats['Media'],
        mode='markers+text',
        text=cat_stats['Categoria'],
        textposition='top center',
        marker=dict(
            size=cat_stats['Total'] / cat_stats['Total'].max() * 50 + 10,
            color=cat_stats['Cor'],
            line=dict(width=2, color='rgba(255,255,255,0.3)')
        ),
        hovertemplate='<b>%{text}</b><br>Quantidade: %{x}<br>Média: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=f"🎯 {title}", font=dict(size=16)),
        xaxis_title='Quantidade de Transações',
        yaxis_title='Valor Médio (R$)',
        **CHART_LAYOUT
    )
    
    return fig


def create_forecast_chart(
    df: pd.DataFrame,
    forecast_data: Dict,
    title: str = "Previsão de Saldo"
) -> go.Figure:
    """
    Cria gráfico com dados históricos e previsão.
    
    Args:
        df: DataFrame com dados históricos
        forecast_data: Dicionário com dados de previsão
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    fig = go.Figure()
    
    # Dados históricos
    ts = df.groupby('Data')['ValorComSinal'].sum().cumsum().reset_index()
    ts.columns = ['Data', 'Saldo']
    
    fig.add_trace(go.Scatter(
        x=ts['Data'],
        y=ts['Saldo'],
        name='Histórico',
        line=dict(color=COLORS['info'], width=2),
        mode='lines',
        hovertemplate='<b>Histórico</b><br>Data: %{x|%d/%m/%Y}<br>Saldo: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Previsão
    if 'previsao_diaria' in forecast_data and len(forecast_data['previsao_diaria']) > 0:
        prev_df = pd.DataFrame(forecast_data['previsao_diaria'])
        prev_df['Data'] = pd.to_datetime(prev_df['Data'])
        
        # Calcula saldo previsto
        ultimo_saldo = ts['Saldo'].iloc[-1]
        prev_df['Saldo'] = ultimo_saldo + prev_df['Previsto'].cumsum()
        prev_df['LimiteInf'] = ultimo_saldo + prev_df['LimiteInferior'].cumsum()
        prev_df['LimiteSup'] = ultimo_saldo + prev_df['LimiteSuperior'].cumsum()
        
        # Linha de previsão
        fig.add_trace(go.Scatter(
            x=prev_df['Data'],
            y=prev_df['Saldo'],
            name='Previsão',
            line=dict(color=COLORS['primary'], width=2, dash='dash'),
            mode='lines',
            hovertemplate='<b>Previsão</b><br>Data: %{x|%d/%m/%Y}<br>Saldo: R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Intervalo de confiança
        fig.add_trace(go.Scatter(
            x=pd.concat([prev_df['Data'], prev_df['Data'][::-1]]),
            y=pd.concat([prev_df['LimiteSup'], prev_df['LimiteInf'][::-1]]),
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=True,
            name='Intervalo 95%'
        ))
    
    layout = dict(**CHART_LAYOUT)
    layout['title'] = dict(text=f"🔮 {title}", font=dict(size=16))
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1,
        bgcolor='rgba(0,0,0,0)',
        font={'color': '#CBD5E1'}
    )
    fig.update_layout(**layout)
    
    return fig
