# 🚀 Guia de Início Rápido

Comece a usar o sistema de análise de portfolio em 5 minutos!

## ⚡ Instalação Rápida

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Execute a análise completa
python cli.py all
```

Pronto! O sistema irá processar suas planilhas e gerar todos os relatórios.

## 📁 Preparando suas Planilhas

Coloque suas planilhas na pasta `planilhas/`:

```
planilhas/
├── b3_carrteira.xlsx      # Planilha da B3
├── kinvo_carteira.xlsx    # Planilha do Kinvo
├── myprofit_carteira.xls  # Planilha do MyProfit
└── xp_carteira.xlsx       # Planilha da XP
```

**Nota**: Se você não tiver todas as fontes, sem problema! O sistema processa as que estiverem disponíveis.

## 🎯 Comandos Essenciais

### Análise Completa (Recomendado)
```bash
python cli.py all
```
Executa todo o pipeline: consolidação + visualizações + relatórios + comparação

### Apenas Consolidação
```bash
python cli.py consolidate
# ou
python main.py
```
Consolida as planilhas e salva o resultado em CSV

### Ver Resultados
```bash
python cli.py list
```
Lista todos os arquivos gerados

### Visualizações
```bash
python cli.py visualize
```
Gera 4 gráficos em PNG (dashboard, top holdings, distribuição, P/L)

### Relatório Detalhado
```bash
python cli.py report
```
Gera relatório de análise completo em texto

### Comparar Versões
```bash
python cli.py compare
```
Compara a versão atual com a anterior (requer pelo menos 2 execuções)

## 📊 O Que Você Vai Obter

### 1. Portfolio Consolidado
Arquivo `output/consolidated_portfolio.csv` com:
- Todos os ativos únicos (duplicatas removidas)
- Valores atualizados
- Lucro/Prejuízo por ativo
- Fonte dos dados

### 2. Visualizações
Pasta `output/visualizations/` com:
- **dashboard.png**: Visão geral com métricas principais
- **top_holdings.png**: Seus 20 maiores investimentos
- **source_distribution.png**: Distribuição por corretora/plataforma
- **profit_loss_distribution.png**: Distribuição de ganhos e perdas

### 3. Relatório Detalhado
Arquivo `output/detailed_report.txt` com:
- Resumo executivo
- Top 10 ganhos e perdas
- Análise de concentração
- Recomendações

### 4. Histórico
- Snapshots semanais em `data/raw/YYYY-MM-DD/`
- Comparação automática entre versões
- Rastreamento de mudanças

## 🔄 Atualização Semanal

Para atualizar seu portfolio toda semana:

1. **Baixe** as planilhas atualizadas das corretoras
2. **Substitua** os arquivos em `planilhas/`
3. **Execute**: `python cli.py all`

O sistema automaticamente:
- ✅ Cria novo snapshot datado
- ✅ Consolida os dados atualizados
- ✅ Compara com a semana anterior
- ✅ Gera novos gráficos e relatórios

## 💡 Dicas Úteis

### Ver Ajuda
```bash
python cli.py --help
```

### Testar se Tudo Está Funcionando
```bash
python cli.py test
```

### Explorar Estrutura das Planilhas
```bash
python cli.py explore
```
Útil para entender o formato dos seus arquivos

### Verificar Versões Anteriores
```bash
ls output/consolidated/
```
Lista todas as consolidações históricas

## ⚠️ Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "File not found"
Verifique se suas planilhas estão em `planilhas/` com os nomes corretos

### Erro no Git Commit
Configure o git primeiro:
```bash
git config --global user.email "seu@email.com"
git config --global user.name "Seu Nome"
```

### Gráficos não Aparecem
Os gráficos são salvos como PNG em `output/visualizations/`. Use um visualizador de imagens para abri-los.

## 📚 Próximos Passos

Depois de rodar a análise completa, explore:

1. **Arquivo CSV**: Abra em Excel/LibreOffice para análise personalizada
2. **Gráficos**: Veja as visualizações geradas
3. **Relatório**: Leia o relatório detalhado para insights
4. **Comparação**: Compare com semanas anteriores

## 🆘 Precisa de Ajuda?

- Veja o README.md completo para documentação detalhada
- Consulte os exemplos em cada script
- Verifique os comandos disponíveis: `python cli.py --help`

---

**Pronto para começar?** Execute `python cli.py all` agora! 🚀
