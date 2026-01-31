"""
Módulo de carregamento e processamento de dados
Dashboard Financeiro 2026
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path
from functools import lru_cache
import sys

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DATA_FILE, CATEGORIAS_MAP, TIPOS_TRANSACAO


class DataLoader:
    """
    Classe responsável pelo carregamento e processamento inicial dos dados.
    Suporta GPU (cuDF) quando disponível, fallback para Pandas.
    """
    
    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or DATA_FILE
        self.gpu_available = self._check_gpu()
        self._df = None
        
        # Define a biblioteca a ser usada (cudf ou pandas)
        if self.gpu_available:
            import cudf
            self.lib = cudf
        else:
            self.lib = pd
        
    def _check_gpu(self) -> bool:
        """Verifica disponibilidade de GPU com cuDF."""
        try:
            import cudf
            print("🚀 GPU detectada! Usando cuDF para processamento acelerado.")
            return True
        except ImportError:
            print("💻 Usando Pandas (CPU). Para GPU, instale cuDF.")
            return False
    
    def load(self, force_reload: bool = False):
        """
        Carrega os dados do arquivo CSV.
        
        Args:
            force_reload: Se True, recarrega mesmo se já estiver em cache
            
        Returns:
            DataFrame com os dados processados
        """
        if self._df is not None and not force_reload:
            return self._df
        
        try:
            # Carrega com Pandas primeiro para garantir parsing correto de datas e compatibilidade
            # cuDF tem algumas diferenças no read_csv que podem causar problemas com formatos específicos
            df_pd = pd.read_csv(
                self.filepath,
                encoding='utf-8',
                parse_dates=['Data'],
                dayfirst=True
            )
            
            # Se tiver GPU, converte para cuDF
            if self.gpu_available:
                df = self.lib.DataFrame.from_pandas(df_pd)
            else:
                df = df_pd
            
            # Processamento inicial
            df = self._clean_data(df)
            df = self._add_calculated_columns(df)
            
            self._df = df
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.filepath}")
        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {str(e)}")
    
    def _clean_data(self, df):
        """Limpa e valida os dados."""
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Preenche valores nulos em colunas numéricas
        numeric_cols = ['Valor', 'Lucro', 'Saldo']
        for col in numeric_cols:
            # Em cuDF/Pandas modernos, alteração direta em slice pode dar warning/erro
            # Garantimos conversão segura
            if self.gpu_available:
                df[col] = self.lib.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Preenche valores nulos em colunas de texto
        text_cols = ['Nome', 'Categoria', 'Tipo', 'Pago_ou_nao_pago', 'Custo_Fixo_x_Variavel']
        for col in text_cols:
            df[col] = df[col].fillna('Não Informado')
        
        # Garante que Codigo é inteiro
        df['Codigo'] = df['Codigo'].astype(int)
        
        # Ordena por data
        df = df.sort_values('Data').reset_index(drop=True)
        
        return df
    
    def _add_calculated_columns(self, df):
        """Adiciona colunas calculadas para análises."""
        
        # Colunas de data
        # Nota: cuDF tem suporte limitado a dt acessor em comparação ao pandas
        # Se for cuDF, algumas operações podem precisar de workaround ou serem feitas no pandas antes
        
        if self.gpu_available:
             # Para simplificar e garantir compatibilidade total com datas (que é complexo em GPU)
             # fazemos operações de data complexas, se necessário, ou usamos as nativas.
             # cuDF suporta dt.year, dt.month, etc.
             pass

        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['MesNome'] = df['Data'].dt.strftime('%b/%Y')
        
        # isocalendar pode não estar disponível em versões antigas do cuDF
        # mas vamos assumir suporte básico ou fallback se der erro
        try:
            df['Semana'] = df['Data'].dt.isocalendar().week.astype(int)
        except:
             # Fallback simples se isocalendar falhar no cuDF
             df['Semana'] = df['Data'].dt.weekofyear

        df['DiaSemana'] = df['Data'].dt.day_name()
        df['DiaMes'] = df['Data'].dt.day
        # quarter suporte no cuDF
        try:
            df['Trimestre'] = df['Data'].dt.quarter
        except:
             df['Trimestre'] = ((df['Mes'] - 1) // 3) + 1
        
        # Indicadores booleanos
        df['EhReceita'] = df['Tipo'] == 'Entrada'
        
        # isin funciona em ambos
        df['EhDespesa'] = df['Tipo'].isin(['Saída', 'Dívida', 'Dívida Parcial'])
        df['EhPago'] = df['Pago_ou_nao_pago'] == 'Pago'
        df['EhFixo'] = df['Custo_Fixo_x_Variavel'] == 'Fixo'
        
        # Valor com sinal (positivo para entrada, negativo para saída)
        # apply com lambda em cuDF é lento ou não suportado para strings complexas.
        # Melhor usar vetorização numpy/cudf
        
        # Implementação vetorizada (funciona em ambos cudf e pandas melhor que apply)
        df['ValorComSinal'] = df['Valor'] * -1
        mask_entrada = df['Tipo'] == 'Entrada'
        df.loc[mask_entrada, 'ValorComSinal'] = df.loc[mask_entrada, 'Valor']
        
        # Valor absoluto para cálculos
        df['ValorAbsoluto'] = df['Valor'].abs()
        
        # Categoria formatada com ícone e Cor
        # Map/apply com dicionário externo é complexo em GPU. 
        # Vamos fazer isso convertendo para pandas temporariamente se for muito complexo,
        # MAS para manter performance, se for apenas display, podemos fazer na hora da exibição (前端)
        # ou manter como está, sabendo que apply em cuDF usa JIT e pode falhar com dicts globais.
        
        # Workaround seguro: Traz para host (CPU) para operações de string complexas baseadas em dicionário
        # Se o dataset for gigante, isso é um gargalo, mas para dashboard pessoal é ok.
        
        if self.gpu_available:
            # Operações de string complexas melhor fazer no pandas ou usar merge
            # Vamos converter colunas específicas para pandas, processar e voltar, ou usar merge
            
            # Criar dataframe de mapeamento
            cats_data = []
            for k, v in CATEGORIAS_MAP.items():
                cats_data.append({
                    'Codigo': k, 
                    'CategoriaDisplay': f"{v.get('icone', '📌')} {v.get('nome', 'Outros')}",
                    'CategoriaCor': v.get('cor', '#6B7280')
                })
            
            map_df = self.lib.DataFrame(cats_data)
            df = df.merge(map_df, on='Codigo', how='left')
            
            # Preenche nulos resultantes do merge
            df['CategoriaDisplay'] = df['CategoriaDisplay'].fillna('📌 Outros')
            df['CategoriaCor'] = df['CategoriaCor'].fillna('#6B7280')
            
        else:
            # Pandas normal
            df['CategoriaDisplay'] = df['Codigo'].apply(
                lambda x: f"{CATEGORIAS_MAP.get(x, {}).get('icone', '📌')} {CATEGORIAS_MAP.get(x, {}).get('nome', 'Outros')}"
            )
            df['CategoriaCor'] = df['Codigo'].apply(
                lambda x: CATEGORIAS_MAP.get(x, {}).get('cor', '#6B7280')
            )
        
        # Saldo acumulado
        df['SaldoAcumulado'] = df['ValorComSinal'].cumsum()
        
        return df
    
    def get_summary(self) -> Dict:
        """Retorna resumo estatístico dos dados."""
        df = self.load()
        
        # Para agregeações que retornam escalar, o comportamento é similar
        # Mas para retornar dict python nativo, valores cuDF precisam ser convertidos (.iloc[0] ou to_numpy)
        
        def to_scalar(val):
            if hasattr(val, 'item'):
                return val.item()
            return val

        return {
            'total_transacoes': len(df),
            'periodo_inicio': df['Data'].min().strftime('%d/%m/%Y'),
            'periodo_fim': df['Data'].max().strftime('%d/%m/%Y'),
            'total_receitas': to_scalar(df[df['EhReceita']]['Valor'].sum()),
            'total_despesas': to_scalar(df[df['EhDespesa']]['Valor'].sum()),
            'saldo_atual': to_scalar(df['ValorComSinal'].sum()),
            'total_dividas': to_scalar(df[df['Tipo'].isin(['Dívida', 'Dívida Parcial'])]['Valor'].sum()),
            'total_pago': to_scalar(df[df['EhPago']]['Valor'].sum()),
            'total_nao_pago': to_scalar(df[~df['EhPago']]['Valor'].sum()),
            'categorias': len(df['Categoria'].unique()),
            'media_diaria': to_scalar(df.groupby('Data')['ValorComSinal'].sum().mean())
        }
    
    def filter_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        categorias: Optional[List[str]] = None,
        tipos: Optional[List[str]] = None,
        status_pago: Optional[str] = None,
        custo_tipo: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None,
        busca: Optional[str] = None
    ):
        """Filtra os dados com base nos parâmetros fornecidos e retorna PANDAS DataFrame para o front-end."""
        df = self.load()
        
        if start_date:
            df = df[df['Data'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['Data'] <= pd.to_datetime(end_date)]
        
        if categorias and len(categorias) > 0:
            df = df[df['Categoria'].isin(categorias)]
        
        if tipos and len(tipos) > 0:
            df = df[df['Tipo'].isin(tipos)]
        
        if status_pago:
            df = df[df['Pago_ou_nao_pago'] == status_pago]
        
        if custo_tipo:
            df = df[df['Custo_Fixo_x_Variavel'] == custo_tipo]
        
        if valor_min is not None:
            df = df[df['Valor'] >= valor_min]
        if valor_max is not None:
            df = df[df['Valor'] <= valor_max]
        
        if busca:
            # str.contains no cuDF suporta regex, mas case=False pode variar
            # Para garantir, convertemos para lower antes
            if self.gpu_available:
                df = df[df['Nome'].str.lower().str.contains(busca.lower())]
            else:
                df = df[df['Nome'].str.contains(busca, case=False, na=False)]
        
        # IMPORTANTE: Dash/Plotly espera Pandas DataFrame ou dicts nativos, não cuDF
        if self.gpu_available and hasattr(df, 'to_pandas'):
            return df.to_pandas()
            
        return df

    def get_raw_data(self):
        """Retorna o dataframe interno (pode ser cudf ou pandas)"""
        return self._df

# Singleton para acesso global
_data_loader: Optional[DataLoader] = None

def get_data_loader() -> DataLoader:
    """Retorna instância singleton do DataLoader."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader


def load_data():
    """Função utilitária para carregar dados."""
    return get_data_loader().load()


def get_summary() -> Dict:
    """Função utilitária para obter resumo."""
    return get_data_loader().get_summary()
