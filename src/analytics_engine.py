"""
Motor de Análises Financeiras
Dashboard Financeiro 2026
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import lru_cache
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CATEGORIAS_MAP


@dataclass
class MetricResult:
    """Resultado de uma métrica calculada."""
    valor: float
    variacao: Optional[float] = None
    variacao_pct: Optional[float] = None
    tendencia: Optional[str] = None
    cor: Optional[str] = None


class AnalyticsEngine:
    """
    Motor de análises financeiras avançadas.
    Calcula métricas, tendências, anomalias e previsões.
    """
    
    def __init__(self, df):
        self.df = df
        self._cache = {}
    
    def get_kpis(self) -> Dict[str, MetricResult]:
        """Calcula os KPIs principais do dashboard."""
        df = self.df
        
        total_receitas = df[df['Tipo'] == 'Entrada']['Valor'].sum()
        total_despesas = df[df['Tipo'].isin(['Saída'])]['Valor'].sum()
        total_dividas = df[df['Tipo'].isin(['Dívida', 'Dívida Parcial'])]['Valor'].sum()
        saldo = total_receitas - total_despesas
        dividas_pendentes = df[df['Pago_ou_nao_pago'] == 'Não Pago']['Valor'].sum()
        
        taxa_economia = ((total_receitas - total_despesas) / total_receitas * 100) if total_receitas > 0 else 0
        
        var_receitas = self._calcular_variacao_periodo(df, 'Entrada')
        var_despesas = self._calcular_variacao_periodo(df, 'Saída')
        
        return {
            'saldo_total': MetricResult(
                valor=saldo,
                variacao_pct=var_receitas.get('variacao_pct'),
                tendencia=self._determinar_tendencia(var_receitas.get('variacao_pct', 0)),
                cor='#10B981' if saldo >= 0 else '#EF4444'
            ),
            'receitas': MetricResult(
                valor=total_receitas,
                variacao_pct=var_receitas.get('variacao_pct'),
                tendencia=self._determinar_tendencia(var_receitas.get('variacao_pct', 0)),
                cor='#10B981'
            ),
            'despesas': MetricResult(
                valor=total_despesas,
                variacao_pct=var_despesas.get('variacao_pct'),
                tendencia=self._determinar_tendencia(-var_despesas.get('variacao_pct', 0)),
                cor='#EF4444'
            ),
            'balanco': MetricResult(
                valor=saldo,
                variacao_pct=((var_receitas.get('variacao_pct', 0) - var_despesas.get('variacao_pct', 0)) / 2),
                tendencia=self._determinar_tendencia(saldo),
                cor='#3B82F6'
            ),
            'dividas_pendentes': MetricResult(
                valor=dividas_pendentes,
                cor='#F59E0B' if dividas_pendentes > 0 else '#10B981'
            ),
            'taxa_economia': MetricResult(
                valor=taxa_economia,
                tendencia='alta' if taxa_economia >= 20 else 'baixa',
                cor='#10B981' if taxa_economia >= 20 else '#EF4444'
            ),
            'total_dividas': MetricResult(
                valor=total_dividas,
                cor='#F97316'
            )
        }
    
    def _calcular_variacao_periodo(self, df, tipo: str) -> Dict:
        """Calcula variação entre períodos."""
        if len(df) == 0:
            return {'variacao': 0, 'variacao_pct': 0}
        
        mid_date = df['Data'].min() + (df['Data'].max() - df['Data'].min()) / 2
        
        periodo_1 = df[(df['Data'] < mid_date) & (df['Tipo'] == tipo)]['Valor'].sum()
        periodo_2 = df[(df['Data'] >= mid_date) & (df['Tipo'] == tipo)]['Valor'].sum()
        
        variacao = periodo_2 - periodo_1
        variacao_pct = (variacao / periodo_1 * 100) if periodo_1 > 0 else 0
        
        return {'variacao': variacao, 'variacao_pct': variacao_pct}
    
    def _determinar_tendencia(self, valor: float) -> str:
        """Determina tendência baseada no valor."""
        if valor > 5:
            return 'alta'
        elif valor < -5:
            return 'baixa'
        return 'estavel'
    
    def get_analise_categorias(self):
        """Análise detalhada por categoria."""
        df = self.df
        
        analise = df.groupby('Categoria').agg({
            'Valor': ['sum', 'mean', 'count', 'std'],
            'ValorComSinal': 'sum'
        }).round(2)
        
        analise.columns = ['Total', 'Media', 'Quantidade', 'DesvPadrao', 'Fluxo']
        analise['Participacao'] = (analise['Total'] / analise['Total'].sum() * 100).round(2)
        analise['Cor'] = analise.index.map(
            lambda x: CATEGORIAS_MAP.get(
                df[df['Categoria'] == x]['Codigo'].iloc[0] if len(df[df['Categoria'] == x]) > 0 else 0,
                {}
            ).get('cor', '#6B7280')
        )
        
        return analise.sort_values('Total', ascending=False)
    
    def get_ranking_categorias(self, top_n: int = 10) -> List[Dict]:
        """Ranking das categorias por valor."""
        analise = self.get_analise_categorias()
        
        ranking = []
        for i, (cat, row) in enumerate(analise.head(top_n).iterrows(), 1):
            ranking.append({
                'posicao': i,
                'categoria': cat,
                'total': row['Total'],
                'participacao': row['Participacao'],
                'quantidade': row['Quantidade'],
                'cor': row['Cor']
            })
        
        return ranking
    
    def get_serie_temporal(self, freq: str = 'D'):
        """Gera série temporal agregada."""
        df = self.df
        
        ts = df.set_index('Data').resample(freq).agg({
            'Valor': 'sum',
            'ValorComSinal': 'sum',
            'Codigo': 'count'
        }).rename(columns={
            'Valor': 'Total',
            'ValorComSinal': 'Fluxo',
            'Codigo': 'Transacoes'
        })
        
        receitas = df[df['Tipo'] == 'Entrada'].set_index('Data').resample(freq)['Valor'].sum()
        despesas = df[df['Tipo'] == 'Saída'].set_index('Data').resample(freq)['Valor'].sum()
        
        ts['Receitas'] = receitas
        ts['Despesas'] = despesas
        ts = ts.fillna(0)
        ts['SaldoAcumulado'] = ts['Fluxo'].cumsum()
        ts['MediaMovel7'] = ts['Fluxo'].rolling(window=7, min_periods=1).mean()
        ts['MediaMovel30'] = ts['Fluxo'].rolling(window=30, min_periods=1).mean()
        
        return ts
    
    def get_tendencia(self) -> Dict:
        """Calcula tendência geral dos dados."""
        ts = self.get_serie_temporal('D')
        
        if len(ts) < 2:
            return {'direcao': 'insuficiente', 'forca': 0}
        
        x = np.arange(len(ts))
        y = ts['Fluxo'].values
        
        coef = np.polyfit(x, y, 1)
        slope = coef[0]
        
        if slope > 10:
            direcao = 'alta_forte'
        elif slope > 0:
            direcao = 'alta_leve'
        elif slope > -10:
            direcao = 'baixa_leve'
        else:
            direcao = 'baixa_forte'
        
        return {
            'direcao': direcao,
            'slope': slope,
            'forca': abs(slope),
            'previsao_proximos_dias': slope * 30
        }
    
    def detectar_anomalias(self, threshold: float = 2.0):
        """Detecta transações anômalas usando Z-score."""
        df = self.df.copy()
        anomalias = []
        
        for categoria in df['Categoria'].unique():
            cat_df = df[df['Categoria'] == categoria]
            if len(cat_df) < 3:
                continue
            
            media = cat_df['Valor'].mean()
            std = cat_df['Valor'].std()
            
            if std > 0:
                cat_df = cat_df.copy()
                cat_df['zscore'] = (cat_df['Valor'] - media) / std
                anomalias_cat = cat_df[abs(cat_df['zscore']) > threshold]
                anomalias.append(anomalias_cat)
        
        if anomalias:
            return pd.concat(anomalias).sort_values('zscore', ascending=False)
        return pd.DataFrame()
    
    def get_alertas(self) -> List[Dict]:
        """Gera alertas baseados em regras."""
        alertas = []
        df = self.df
        kpis = self.get_kpis()
        
        if kpis['dividas_pendentes'].valor > 0:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Dívidas Pendentes',
                'mensagem': f"Você possui R$ {kpis['dividas_pendentes'].valor:,.2f} em dívidas não pagas.",
                'prioridade': 'alta',
                'icone': '⚠️'
            })
        
        if kpis['taxa_economia'].valor < 20:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Taxa de Economia Baixa',
                'mensagem': f"Sua taxa de economia é de {kpis['taxa_economia'].valor:.1f}%. O ideal é acima de 20%.",
                'prioridade': 'media',
                'icone': '📉'
            })
        
        if kpis['saldo_total'].valor < 0:
            alertas.append({
                'tipo': 'danger',
                'titulo': 'Saldo Negativo',
                'mensagem': f"Seu saldo está negativo em R$ {abs(kpis['saldo_total'].valor):,.2f}.",
                'prioridade': 'alta',
                'icone': '🚨'
            })
        
        anomalias = self.detectar_anomalias()
        if len(anomalias) > 0:
            alertas.append({
                'tipo': 'info',
                'titulo': f'{len(anomalias)} Transações Atípicas',
                'mensagem': 'Algumas transações estão fora do padrão usual.',
                'prioridade': 'baixa',
                'icone': '🔍'
            })
        
        gastos_gasolina = df[(df['Categoria'] == 'Gasolina') & (df['Tipo'] == 'Saída')]['Valor'].sum()
        total_gastos = df[df['Tipo'] == 'Saída']['Valor'].sum()
        if total_gastos > 0 and (gastos_gasolina / total_gastos) > 0.3:
            pct = (gastos_gasolina / total_gastos) * 100
            alertas.append({
                'tipo': 'info',
                'titulo': 'Alto Gasto com Combustível',
                'mensagem': f"Gastos com gasolina representam {pct:.1f}% das despesas.",
                'prioridade': 'media',
                'icone': '⛽'
            })
        
        return sorted(alertas, key=lambda x: {'alta': 0, 'media': 1, 'baixa': 2}.get(x['prioridade'], 3))
    
    def prever_proximos_dias(self, dias: int = 30) -> Dict:
        """Faz previsão simples para os próximos dias."""
        ts = self.get_serie_temporal('D')
        
        if len(ts) < 7:
            return {'erro': 'Dados insuficientes para previsão'}
        
        media_recente = ts['Fluxo'].tail(30).mean()
        std_recente = ts['Fluxo'].tail(30).std()
        
        ultimo_dia = ts.index[-1]
        datas_futuras = pd.date_range(start=ultimo_dia + timedelta(days=1), periods=dias)
        
        previsao = pd.DataFrame({
            'Data': datas_futuras,
            'Previsto': media_recente,
            'LimiteInferior': media_recente - 1.96 * std_recente,
            'LimiteSuperior': media_recente + 1.96 * std_recente
        })
        
        saldo_atual = ts['SaldoAcumulado'].iloc[-1]
        saldo_previsto = saldo_atual + (media_recente * dias)
        
        return {
            'previsao_diaria': previsao.to_dict('records'),
            'media_diaria_prevista': media_recente,
            'saldo_previsto_final': saldo_previsto,
            'intervalo_confianca': {
                'inferior': media_recente - 1.96 * std_recente,
                'superior': media_recente + 1.96 * std_recente
            },
            'confianca': 95
        }
    
    def generate_insights(self) -> List[Dict]:
        """Gera insights baseados em regras (substituindo IA)."""
        insights = []
        df = self.df
        kpis = self.get_kpis()
        ranking = self.get_ranking_categorias(3)
        trends = self.get_tendencia()
        
        # Insight 1: Maior Gasto
        if ranking:
            top_cat = ranking[0]
            insights.append({
                'icone': '💸',
                'titulo': 'Maior Despesa',
                'descricao': f"Sua maior categoria de gastos é {top_cat['categoria']} com R$ {top_cat['total']:,.2f} ({top_cat['participacao']}% do total).",
                'acao': 'Revise estes gastos',
                'prioridade': 'Alta'
            })
            
        # Insight 2: Economia
        taxa = kpis['taxa_economia'].valor
        if taxa < 10:
            insights.append({
                'icone': '📉',
                'titulo': 'Economia Crítica',
                'descricao': f"Sua taxa de economia está muito baixa ({taxa:.1f}%). Tente reduzir desperdícios.",
                'acao': 'Corte gastos supérfluos',
                'prioridade': 'Alta'
            })
        elif taxa > 30:
            insights.append({
                'icone': '💰',
                'titulo': 'Ótima Economia',
                'descricao': f"Parabéns! Você está economizando {taxa:.1f}% da sua renda.",
                'acao': 'Invista o excedente',
                'prioridade': 'Baixa'
            })
            
        # Insight 3: Tendência
        trend_map = {
            'alta_forte': 'Ganhos aumentando rapidamente',
            'alta_leve': 'Ganhos em leve alta',
            'baixa_leve': 'Gastos superando ganhos levemente',
            'baixa_forte': 'Alerta: Tendência de queda no saldo',
            'estavel': 'Finanças estáveis',
            'insuficiente': 'Poucos dados para tendência'
        }
        insights.append({
            'icone': '📈' if 'alta' in trends['direcao'] else '📉',
            'titulo': 'Tendência Financeira',
            'descricao': trend_map.get(trends['direcao'], 'Analisando tendência...'),
            'acao': 'Acompanhe diariamente',
            'prioridade': 'Media'
        })
        
        # Insight 4: Dívidas
        dividas = kpis['dividas_pendentes'].valor
        if dividas > 0:
             insights.append({
                'icone': '⚠️',
                'titulo': 'Dívidas em Aberto',
                'descricao': f"Existem R$ {dividas:,.2f} em contas não pagas vencendo.",
                'acao': 'Priorize quitação',
                'prioridade': 'Alta'
            })
            
        return insights[:4]
    
    def get_resumo_completo(self) -> Dict:
        """Gera resumo completo de todas as análises."""
        return {
            'kpis': self.get_kpis(),
            'categorias': self.get_ranking_categorias(),
            'tendencia': self.get_tendencia(),
            'alertas': self.get_alertas(),
            'previsao': self.prever_proximos_dias(30)
        }
