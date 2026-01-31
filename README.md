# 🚀 Dashboard Financeiro Interativo 2026

Dashboard moderno e interativo para análise financeira pessoal/empresarial, desenvolvido em Python com integração de IA local (Ollama) para análise contextual inteligente.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Dash](https://img.shields.io/badge/Dash-2.14+-green)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-purple)

## ✨ Funcionalidades

### 📊 Visualizações Interativas (Estilo Power BI)
- **Gráfico de Fluxo de Caixa** - Receitas vs Despesas ao longo do tempo
- **Gráfico de Pizza/Donut** - Distribuição por categoria
- **Barras Empilhadas** - Comparativo mensal
- **Treemap** - Hierarquia de gastos com drill-down
- **Heatmap** - Padrões de gastos por dia
- **Waterfall** - Evolução do saldo
- **Sunburst** - Visão hierárquica circular
- **Gráfico de Previsão** - Projeções com intervalo de confiança
- **Gauge Charts** - Indicadores de performance

### 📈 KPIs e Métricas
- Saldo Total com variação
- Total de Receitas
- Total de Despesas
- Balanço Líquido
- Dívidas Pendentes
- Taxa de Economia

### 🤖 Análise com IA (Ollama)
- **Chat Interativo** - Faça perguntas sobre seus dados
- **Insights Automáticos** - Geração de observações relevantes
- **Recomendações** - Sugestões de melhoria financeira
- **Explicação de Anomalias** - Entenda gastos fora do padrão

### 🎨 Design Moderno
- Tema Dark Mode premium
- Glassmorphism e gradientes
- Animações suaves
- Totalmente responsivo

## 📋 Pré-requisitos

- **Python 3.11** ou superior
- **Ollama** (para análise com IA) - [Instalar Ollama](https://ollama.ai)
- **GPU NVIDIA com CUDA** (opcional, para processamento acelerado)

## 🚀 Instalação

### 1. Clone ou baixe o projeto

### 2. Execute o setup
```batch
setup.bat
```

Isso irá:
- Criar um ambiente virtual Python
- Instalar todas as dependências

### 3. Configure o Ollama (para IA)
```bash
# Instale o Ollama de https://ollama.ai
# Baixe o modelo
ollama pull qwen2.5:7b

# Inicie o servidor (deixe rodando)
ollama serve
```

### 4. Inicie o Dashboard
```batch
run.bat
```

### 5. Acesse no navegador
```
http://127.0.0.1:8050
```

## 📁 Estrutura do Projeto

```
Dashboard/
├── app.py                 # Aplicação principal
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── setup.bat              # Script de instalação
├── run.bat                # Script de execução
│
├── data/
│   └── dados_financeiros.csv  # Dados financeiros
│
├── src/
│   ├── data_loader.py         # Carregamento de dados
│   ├── analytics_engine.py    # Motor de análises
│   └── ollama_client.py       # Cliente Ollama
│
├── components/
│   └── charts.py              # Componentes de gráficos
│
└── assets/
    └── styles.css             # Estilos dark mode
```

## 💡 Como Usar

### Filtros
- **Período**: Selecione o intervalo de datas
- **Categoria**: Filtre por categoria de gasto/receita
- **Tipo**: Entrada, Saída, Dívida
- **Status**: Pago ou Não Pago
- **Busca**: Pesquise por descrição

### Chat com IA
Exemplos de perguntas:
- "Como está minha situação financeira?"
- "Quais categorias tiveram maior aumento de gastos?"
- "Onde posso economizar?"
- "Quanto gastei com gasolina este mês?"
- "Qual a tendência dos meus gastos?"

### Cross-Filtering
Clique em elementos dos gráficos para filtrar os demais (estilo Power BI).

## ⚙️ Configurações

Edite `config.py` para personalizar:

```python
# Configurações do Ollama
OLLAMA_CONFIG = {
    "host": "http://localhost:11434",
    "model": "qwen2.5:7b",  # Altere o modelo aqui
    "timeout": 120
}

# Configurações do Dashboard
DASHBOARD_CONFIG = {
    "port": 8050,  # Altere a porta aqui
    "debug": True
}
```

## 📊 Seus Dados

Os dados são carregados do arquivo `data/dados_financeiros.csv`. O formato esperado:

| Coluna | Descrição |
|--------|-----------|
| Codigo | ID da categoria |
| Nome | Descrição da transação |
| Data | Data (DD/MM/YYYY) |
| Categoria | Categoria do gasto |
| Tipo | Entrada/Saída/Dívida |
| Pago_ou_nao_pago | Status |
| Custo_Fixo_x_Variavel | Classificação |
| Valor | Valor da transação |
| Lucro | Lucro associado |
| Saldo | Saldo resultante |

## 🔧 Tecnologias

- **Dash** - Framework web interativo
- **Plotly** - Visualizações de dados
- **Pandas** - Processamento de dados
- **Ollama** - IA local (qwen2.5)
- **Bootstrap** - Componentes UI

## 📝 Licença

Este projeto é de uso pessoal/educacional.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

Desenvolvido com ❤️ usando Python, Dash e Ollama
