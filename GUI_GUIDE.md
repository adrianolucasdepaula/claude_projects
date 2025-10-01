# Guia de Uso - Interface Web do Portfolio Analysis

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação e Configuração](#instalação-e-configuração)
3. [Iniciando a Aplicação](#iniciando-a-aplicação)
4. [Páginas e Funcionalidades](#páginas-e-funcionalidades)
5. [Testes E2E](#testes-e2e)
6. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 Visão Geral

A interface web do Portfolio Analysis System é uma aplicação Streamlit que permite:

- **Consolidar** múltiplas fontes de portfolio (B3, Kinvo, MyProfit, XP)
- **Visualizar** dados interativos com gráficos Plotly
- **Comparar** diferentes versões do portfolio ao longo do tempo
- **Gerar relatórios** executivos e detalhados
- **Exportar** dados em múltiplos formatos (CSV, Excel, TXT)

### Arquitetura

```
app.py                          # Aplicação principal Streamlit
├── src/invest/gui/
│   ├── pages/                  # Páginas da aplicação
│   │   ├── home.py            # Dashboard principal
│   │   ├── consolidation.py   # Upload e consolidação
│   │   ├── visualizations.py  # Gráficos interativos
│   │   ├── comparison.py      # Comparação de versões
│   │   └── reports.py         # Geração de relatórios
│   └── components/            # Componentes reutilizáveis
└── tests/
    └── test_gui_playwright.py # Testes E2E
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.13+
- pip
- (Opcional) Ambiente virtual

### 1. Instalar Dependências

```bash
# Instalar todas as dependências
py -m pip install -r requirements.txt

# Ou instalar manualmente
py -m pip install streamlit plotly playwright pytest-playwright
```

### 2. Instalar Navegadores Playwright

```bash
py -m playwright install chromium
```

### 3. Verificar Instalação

```bash
py -m streamlit --version
```

---

## 🎬 Iniciando a Aplicação

### Método 1: Comando Direto

```bash
py -m streamlit run app.py
```

### Método 2: Com Configurações Personalizadas

```bash
# Mudar porta (padrão: 8501)
py -m streamlit run app.py --server.port 8502

# Desabilitar watch (útil em produção)
py -m streamlit run app.py --server.fileWatcherType none

# Modo headless (sem abrir browser)
py -m streamlit run app.py --server.headless true
```

### Acessar a Aplicação

Após iniciar, acesse no navegador:
- **Local**: http://localhost:8501
- **Rede**: http://SEU_IP:8501

---

## 📱 Páginas e Funcionalidades

### 1. 🏠 Home / Dashboard

**Objetivo**: Visão geral rápida do portfolio consolidado

**Recursos**:
- ✅ Métricas principais (valor total, número de ativos, retorno médio)
- ✅ Distribuição por fonte (gráfico pizza)
- ✅ Top 10 holdings (gráfico barras)
- ✅ Análise de performance (lucros/prejuízos)
- ✅ Tabela detalhada com filtros

**Como Usar**:
1. Certifique-se de ter consolidado pelo menos uma vez
2. Use os filtros para explorar subconjuntos dos dados
3. Clique nos gráficos para interação (zoom, pan, hover)

---

### 2. 🔄 Consolidação

**Objetivo**: Fazer upload e consolidar planilhas de múltiplas fontes

**Recursos**:
- ✅ Upload de 4 fontes simultaneamente
- ✅ 3 estratégias de deduplicação:
  - **Aggregate**: Soma quantidades duplicadas
  - **Prioritize**: Mantém fonte de maior prioridade
  - **Latest**: Mantém registro mais recente
- ✅ Versionamento automático
- ✅ Detecção de duplicatas
- ✅ Download do resultado consolidado

**Como Usar**:

**Passo 1: Upload de Arquivos**
```
1. Clique em "Browse files" para cada fonte
2. Selecione o arquivo correspondente:
   - B3: arquivo .xlsx
   - Kinvo: arquivo .xlsx
   - MyProfit: arquivo .xls
   - XP: arquivo .xlsx
3. Arquivos serão validados automaticamente
```

**Passo 2: Configuração**
```
1. Selecione a estratégia de deduplicação
2. Habilite/desabilite versionamento
3. Clique em "Consolidar Portfolios"
```

**Passo 3: Resultados**
```
1. Veja estatísticas de deduplicação
2. Explore duplicatas detectadas
3. Download do CSV consolidado
```

**Ordem de Prioridade** (estratégia "Prioritize"):
1. MyProfit (dados mais completos)
2. B3 (dados oficiais da bolsa)
3. XP (dados da corretora)
4. Kinvo (agregador)

---

### 3. 📈 Visualizações

**Objetivo**: Explorar dados com gráficos interativos

**Recursos**:
- ✅ 5 tipos de análise:
  - **Distribuição**: Pizza e barras por fonte/classe
  - **Top Holdings**: Maiores posições
  - **Performance**: Ganhos e perdas
  - **Treemap**: Visualização hierárquica
  - **Concentração**: Análise de risco

**Como Usar**:

**Filtros (Sidebar)**:
```
1. Selecione fontes específicas
2. Ajuste faixa de valor (slider)
3. Gráficos atualizam automaticamente
```

**Análise de Concentração**:
```
1. Verifique % dos Top 5/10/20 ativos
2. Veja curva de concentração acumulada
3. Identifique quantos ativos = 80% do portfolio
4. Alertas automáticos se concentração > 50%
```

**Interação com Gráficos**:
- **Hover**: Ver detalhes
- **Click**: Ocultar/mostrar séries
- **Drag**: Zoom em área
- **Double-click**: Reset zoom
- **📷 Icon**: Baixar como PNG

---

### 4. 📊 Comparação de Versões

**Objetivo**: Analisar mudanças entre consolidações

**Recursos**:
- ✅ Comparar 2 versões lado a lado
- ✅ Detectar novos ativos
- ✅ Detectar ativos removidos
- ✅ Calcular mudanças de valor
- ✅ Visualizações comparativas

**Como Usar**:

**Passo 1: Selecionar Versões**
```
1. Escolha "Versão 1" (mais antiga)
2. Escolha "Versão 2" (mais recente)
3. Clique em "Comparar Versões"
```

**Passo 2: Analisar Resultados**
```
Tabs disponíveis:
- 🆕 Novos Ativos: Assets adicionados
- ❌ Ativos Removidos: Assets que saíram
- 📈 Mudanças de Valor: Alterações em ativos comuns
- 📊 Comparação Visual: Gráficos lado a lado
```

**Filtros de Mudança**:
- Todos
- Apenas Aumentos
- Apenas Reduções
- Mudanças Significativas (>10%)

---

### 5. 📄 Relatórios

**Objetivo**: Gerar e exportar relatórios detalhados

**Recursos**:
- ✅ 5 tipos de relatório:
  1. **Executivo**: Resumo geral do portfolio
  2. **Performance**: Análise de lucros/perdas
  3. **Detalhado por Ativo**: Tabela completa com filtros
  4. **Distribuição**: Quebras por categoria
  5. **Alertas**: Recomendações automáticas

**Formatos de Exportação**:
- 📄 TXT (relatórios textuais)
- 📊 CSV (dados tabulares)
- 📗 Excel (múltiplas sheets)

**Como Usar**:

**Relatório Executivo**:
```
1. Selecione "Relatório Executivo"
2. Visualize métricas principais
3. Clique em "Download TXT/CSV/Excel"
```

**Alertas e Recomendações**:
```
Alertas automáticos para:
- ⚠️ Alta concentração (>50% em 5 ativos)
- ⚠️ Perdas > 20% em ativos individuais
- ⚠️ Retorno médio negativo
- ℹ️ Portfolio muito/pouco diversificado
- ℹ️ Muitas posições pequenas (<1%)
```

---

## 🧪 Testes E2E

### Executar Testes

**Pré-requisito**: Aplicação Streamlit rodando em http://localhost:8501

```bash
# Terminal 1: Iniciar aplicação
py -m streamlit run app.py

# Terminal 2: Executar testes
pytest tests/test_gui_playwright.py -v --headed

# Apenas testes rápidos
pytest tests/test_gui_playwright.py -k "not Performance" -v

# Com relatório HTML
pytest tests/test_gui_playwright.py --html=report.html
```

### Suítes de Teste Disponíveis

| Suite | Testes | Descrição |
|-------|--------|-----------|
| `TestNavigation` | 3 | Navegação entre páginas |
| `TestConsolidationPage` | 4 | Funcionalidades de upload |
| `TestVisualizationsPage` | 3 | Renderização de gráficos |
| `TestComparisonPage` | 2 | Comparação de versões |
| `TestReportsPage` | 3 | Geração de relatórios |
| `TestResponsiveness` | 3 | Design responsivo |
| `TestPerformance` | 2 | Métricas de performance |
| `TestAccessibility` | 2 | Acessibilidade |

### Configurar Chrome DevTools MCP

**Habilitando MCP** (opcional para análise avançada):

```bash
# 1. Habilitar servidor MCP no .claude/settings.json
# (já configurado em .mcp.json)

# 2. Executar com MCP habilitado
# Claude Code detectará automaticamente o .mcp.json
```

**Métricas Coletadas**:
- ⏱️ Tempo de carregamento de página
- 🖼️ Largest Contentful Paint (LCP)
- ⚡ First Input Delay (FID)
- 📐 Cumulative Layout Shift (CLS)

---

## 🔧 Solução de Problemas

### Problema: Aplicação não inicia

**Erro**: `ModuleNotFoundError: No module named 'streamlit'`

**Solução**:
```bash
py -m pip install --upgrade streamlit
```

---

### Problema: Página em branco / não carrega

**Erro**: Página carrega mas fica em branco

**Solução**:
```bash
# 1. Limpar cache do Streamlit
py -m streamlit cache clear

# 2. Reiniciar aplicação
# Ctrl+C no terminal
py -m streamlit run app.py
```

---

### Problema: Upload de arquivo falha

**Erro**: "Erro ao carregar arquivo"

**Soluções**:
1. Verifique se o arquivo tem o formato correto:
   - B3: .xlsx
   - Kinvo: .xlsx
   - MyProfit: .xls (pode ser HTML disfarçado)
   - XP: .xlsx

2. Verifique se o arquivo não está corrompido:
```bash
# Tente abrir no Excel primeiro
```

3. Tamanho do arquivo:
```python
# Aumentar limite de upload no Streamlit
# Criar ~/.streamlit/config.toml:

[server]
maxUploadSize = 200  # MB
```

---

### Problema: Gráficos não aparecem

**Erro**: Espaço em branco onde deveria ter gráfico

**Solução**:
```bash
# 1. Verificar dependências
py -m pip install plotly --upgrade

# 2. Limpar cache
py -m streamlit cache clear

# 3. Verificar se há dados
# Na página, filtros podem ter removido todos os dados
```

---

### Problema: Testes Playwright falham

**Erro**: `Page timeout` ou conexão recusada

**Solução**:
```bash
# 1. Certifique-se que Streamlit está rodando
# Terminal 1:
py -m streamlit run app.py

# 2. Aguarde 5-10 segundos antes de rodar testes

# 3. Verifique porta correta (8501 padrão)
# Em test_gui_playwright.py, confira app_url

# 4. Reinstalar Playwright
py -m playwright install chromium
```

---

### Problema: Performance lenta

**Sintoma**: Interface lenta, demora para atualizar

**Soluções**:

1. **Reduzir número de ativos exibidos**:
```python
# Em home.py, limitar linhas:
st.dataframe(df.head(100))  # Ao invés de tudo
```

2. **Habilitar cache**:
```python
# Já implementado com @st.cache_data
# Força limpeza se necessário:
py -m streamlit cache clear
```

3. **Aumentar recursos**:
```bash
# Aumentar memória do Streamlit
streamlit run app.py --server.maxUploadSize 400
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [Playwright Python](https://playwright.dev/python/)

### Atalhos de Teclado (Streamlit)
- `R`: Reexecutar aplicação
- `C`: Limpar cache
- `Ctrl+C`: Parar servidor

### Logs e Debug

**Ver logs do Streamlit**:
```bash
# Rodar com verbosidade
py -m streamlit run app.py --logger.level=debug
```

**Debug no código**:
```python
# Adicionar em qualquer página:
import streamlit as st
st.write("DEBUG:", variavel)
st.json(dicionario)
```

---

## 🎨 Customização

### Tema

Criar arquivo `~/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Logo e Favicon

```python
# Em app.py:
st.set_page_config(
    page_icon="📊",  # Emoji ou caminho para imagem
    # page_icon="./assets/logo.png",
)
```

---

## 🤝 Contribuindo

Para adicionar novas funcionalidades à GUI:

1. **Nova página**: Criar em `src/invest/gui/pages/`
2. **Novo componente**: Criar em `src/invest/gui/components/`
3. **Adicionar rota**: Atualizar `app.py`
4. **Testes**: Adicionar em `tests/test_gui_playwright.py`

---

## 📞 Suporte

- **Issues**: https://github.com/adrianolucasdepaula/claude_projects/issues
- **Documentação do Projeto**: README.md
- **Quick Start**: QUICKSTART.md

---

**Última atualização**: 30/09/2025
**Versão**: 1.0.0
