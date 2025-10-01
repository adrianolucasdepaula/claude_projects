# Investment Portfolio Analysis System

Sistema completo de análise e consolidação de carteiras de investimento com deduplicação inteligente e versionamento automático.

## Funcionalidades

### 📊 Consolidação de Portfolios
Importa e consolida carteiras de múltiplas fontes:
  - **B3** (Bolsa de Valores Brasileira)
  - **Kinvo** (Plataforma de Gestão de Investimentos)
  - **MyProfit** (Plataforma de Gestão de Investimentos)
  - **XP Investimentos** (Corretora)

### 🔄 Deduplicação Inteligente
- Detecta automaticamente ativos duplicados entre fontes
- Três estratégias disponíveis:
  - **AGGREGATE**: Soma quantidades de todas as fontes (padrão)
  - **PRIORITIZE**: Mantém dados da fonte de maior prioridade
  - **LATEST**: Mantém dados mais recentes
- Normalização de tickers (ex: variações de Tesouro Direto)
- Relatório detalhado de duplicatas

### 📁 Versionamento Automático
- Snapshots semanais de todas as planilhas
- Histórico completo de consolidações
- Comparação entre versões
- Rastreamento de mudanças ao longo do tempo

### 📈 Análise de Portfolio
- Valor total consolidado
- Lucro/Prejuízo por ativo
- Top holdings com detalhamento de fontes
- Métricas de performance
- Relatórios em CSV e JSON

## Estrutura do Projeto

```
invest/
├── src/
│   └── invest/
│       ├── readers/          # Leitores de diferentes fontes
│       ├── analyzers/        # Análises e métricas
│       └── utils/            # Utilitários
├── tests/                    # Testes unitários
├── planilhas/               # Planilhas de entrada
├── output/                  # Arquivos de saída
├── main.py                  # Script principal
└── requirements.txt         # Dependências
```

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### 🖥️ Interface Web (Recomendado)

O sistema possui uma **interface web interativa** construída com Streamlit:

```bash
# Iniciar aplicação web
python -m streamlit run app.py

# Ou use o script helper (Windows)
run_gui.bat
```

Acesse no navegador: **http://localhost:8501**

**Funcionalidades da Interface Web**:
- 📤 Upload interativo de planilhas
- 📊 Dashboard com métricas em tempo real
- 📈 Gráficos interativos (Plotly)
- 🔄 Comparação visual de versões
- 📄 Geração e exportação de relatórios
- 🎨 Interface intuitiva e responsiva

**Documentação completa**: Veja [GUI_GUIDE.md](GUI_GUIDE.md)

---

### 💻 Interface de Linha de Comando (CLI)

O sistema também possui uma CLI completa para automação:

```bash
# Ver todos os comandos disponíveis
python cli.py --help

# Análise completa (recomendado)
python cli.py all

# Apenas consolidação
python cli.py consolidate

# Gerar visualizações
python cli.py visualize

# Gerar relatório detalhado
python cli.py report

# Comparar versões
python cli.py compare

# Listar arquivos gerados
python cli.py list
```

### Executando a Consolidação Diretamente

```bash
python main.py
```

O sistema irá:
1. ✅ Carregar todas as planilhas da pasta `planilhas/`
2. 🔍 Detectar e reportar ativos duplicados
3. 🔄 Aplicar deduplicação (estratégia AGGREGATE)
4. 📊 Gerar estatísticas e resumo
5. 💾 Salvar resultados em `output/`
6. 📁 Criar snapshot versionado em `data/raw/YYYY-MM-DD/`

### Arquivos de Saída

- `output/consolidated_portfolio.csv` - Portfolio consolidado completo
- `output/summary.json` - Resumo estatístico
- `output/consolidated/latest.csv` - Última consolidação
- `output/consolidated/portfolio_YYYY-MM-DD.csv` - Consolidações históricas
- `data/raw/YYYY-MM-DD/` - Snapshots das planilhas originais

### Comandos Claude Code

- `/setup` - Configurar ambiente virtual e dependências
- `/test` - Executar testes unitários
- `/lint` - Verificar qualidade do código
- `/analyze` - Analisar portfolio específico

### Scripts Disponíveis

| Script | Descrição | Comando |
|--------|-----------|---------|
| **Consolidação** | Consolida portfolios com deduplicação | `python main.py` |
| **CLI** | Interface de linha de comando | `python cli.py [command]` |
| **Visualizações** | Gera gráficos e dashboards | `python scripts/visualize_portfolio.py` |
| **Relatório** | Gera relatório detalhado em texto | `python scripts/generate_report.py` |
| **Comparação** | Compara versões históricas | `python scripts/compare_versions.py` |
| **Exploração** | Analisa estrutura das planilhas | `python scripts/explore_sheets.py` |
| **Testes** | Testa readers individualmente | `python scripts/test_readers.py` |

## Atualização Semanal

Para consolidar novas planilhas semanalmente:

1. Substitua os arquivos em `planilhas/` pelas versões mais recentes
2. Execute `python main.py`
3. O sistema criará automaticamente:
   - Novo snapshot datado
   - Nova consolidação versionada
   - Relatório de mudanças

## Recursos Avançados

### Comparação de Versões

```python
from src.invest.utils.versioning import PortfolioVersionManager

vm = PortfolioVersionManager()

# Listar todas as versões
versions = vm.list_versions()

# Comparar duas versões
comparison = vm.compare_versions("2025-09-23", "2025-09-30")

# Gerar relatório de mudanças
report = vm.generate_change_report("2025-09-23")
```

### Estratégias de Deduplicação

```python
from src.invest.analyzers.portfolio import PortfolioConsolidator

# Usar estratégia de priorização
consolidator = PortfolioConsolidator(
    deduplication_strategy="prioritize"  # ou "aggregate", "latest"
)
```

## Arquivos Gerados

Após executar o sistema completo (`python cli.py all`), você terá:

### Consolidações
- `output/consolidated_portfolio.csv` - Portfolio consolidado completo
- `output/consolidated/latest.csv` - Última versão (link simbólico)
- `output/consolidated/portfolio_YYYY-MM-DD.csv` - Versões históricas

### Visualizações
- `output/visualizations/dashboard.png` - Dashboard com métricas principais
- `output/visualizations/top_holdings.png` - Gráfico de maiores posições
- `output/visualizations/source_distribution.png` - Distribuição por fonte
- `output/visualizations/profit_loss_distribution.png` - Distribuição de L/P

### Relatórios
- `output/detailed_report.txt` - Relatório completo em texto
- `output/summary.json` - Resumo estatístico em JSON
- `output/reports/changes_*.json` - Relatórios de mudanças entre versões

### Snapshots
- `data/raw/YYYY-MM-DD/` - Cópias das planilhas originais por data
- `data/raw/YYYY-MM-DD/metadata.json` - Metadados do snapshot

## Roadmap

### ✅ Implementado
- Sistema de consolidação completo
- Deduplicação inteligente com 3 estratégias
- Versionamento automático com snapshots
- Visualizações (4 tipos de gráficos)
- Relatórios detalhados
- CLI completa
- Comparação de versões

### 🔜 Próximas Features
- Integração com APIs de cotações em tempo real (yfinance, B3)
- Alertas automáticos de mudanças significativas
- Dashboard web interativo (Streamlit/Dash)
- Relatórios em PDF com gráficos
- Análise de risco e diversificação
- Recomendações automatizadas de rebalanceamento
- Export para Excel com formatação

## Desenvolvimento

- Python 3.10+
- Pandas para manipulação de dados
- Openpyxl/xlrd para leitura de Excel
- Pytest para testes

## Licença

MIT
