"""
Configurações centralizadas do Dashboard Financeiro 2026
"""
import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Arquivo de dados
DATA_FILE = DATA_DIR / "dados_financeiros.csv"

# Configurações do Ollama
OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "qwen2.5-large:7b",
    "timeout": 120,
    "max_tokens": 2048,
    "temperature": 0.7
}

# Configurações do Dashboard
DASHBOARD_CONFIG = {
    "title": "🚀 Dashboard Financeiro 2026",
    "host": "127.0.0.1",
    "port": 8050,
    "debug": True,
    "theme": "dark"
}

# Mapeamento de categorias por código
CATEGORIAS_MAP = {
    8888: {"nome": "Gasolina", "cor": "#F59E0B", "icone": "⛽"},
    2222: {"nome": "Gasto Pessoal", "cor": "#EF4444", "icone": "🛒"},
    9999: {"nome": "Investimento", "cor": "#10B981", "icone": "💰"},
    3333: {"nome": "Salário", "cor": "#3B82F6", "icone": "💼"},
    4444: {"nome": "Uber Driver", "cor": "#8B5CF6", "icone": "🚗"},
    1211: {"nome": "Pedágio", "cor": "#EC4899", "icone": "🛣️"},
    1411: {"nome": "Manutenção", "cor": "#F97316", "icone": "🔧"},
    5555: {"nome": "Imposto", "cor": "#DC2626", "icone": "📋"},
    1311: {"nome": "Lalamove", "cor": "#14B8A6", "icone": "📦"}
}

# Cores do tema dark
COLORS = {
    # Background
    "bg_primary": "#0F172A",
    "bg_secondary": "#1E293B",
    "bg_tertiary": "#334155",
    
    # Texto
    "text_primary": "#F8FAFC",
    "text_secondary": "#CBD5E1",
    "text_muted": "#64748B",
    
    # Status
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "info": "#3B82F6",
    
    # Primárias
    "primary": "#6366F1",
    "primary_light": "#818CF8",
    "primary_dark": "#4F46E5",
    
    # Gradientes
    "gradient_primary": "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)",
    "gradient_success": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
    "gradient_danger": "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)"
}

# Configurações de gráficos
CHART_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "grafico_dashboard",
        "height": 600,
        "width": 1200,
        "scale": 2
    }
}

# Layout padrão dos gráficos
CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": COLORS["text_primary"], "family": "Inter, sans-serif"},
    "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
    "xaxis": {
        "gridcolor": "rgba(148, 163, 184, 0.1)",
        "zerolinecolor": "rgba(148, 163, 184, 0.2)"
    },
    "yaxis": {
        "gridcolor": "rgba(148, 163, 184, 0.1)",
        "zerolinecolor": "rgba(148, 163, 184, 0.2)"
    },
    "legend": {
        "bgcolor": "rgba(0,0,0,0)",
        "font": {"color": COLORS["text_secondary"]}
    }
}

# Tipos de transação
TIPOS_TRANSACAO = {
    "Entrada": {"cor": COLORS["success"], "sinal": 1},
    "Saída": {"cor": COLORS["danger"], "sinal": -1},
    "Dívida": {"cor": COLORS["warning"], "sinal": 0},
    "Dívida Parcial": {"cor": "#F97316", "sinal": 0}
}

# Formatos de moeda
CURRENCY_FORMAT = {
    "locale": "pt-BR",
    "symbol": "R$",
    "decimal": ",",
    "thousand": "."
}
