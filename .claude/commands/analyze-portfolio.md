---
description: Análise completa do portfolio com todas as features
---

Execute a análise completa do portfolio de investimentos:

1. Consolida todas as planilhas (B3, Kinvo, MyProfit, XP)
2. Aplica deduplicação inteligente
3. Gera visualizações (gráficos)
4. Cria relatório detalhado
5. Compara com versões anteriores

```bash
python cli.py all
```

Após a execução, você pode visualizar:
- Portfolio consolidado: `output/consolidated_portfolio.csv`
- Gráficos: `output/visualizations/*.png`
- Relatório: `output/detailed_report.txt`
- Resumo: `output/summary.json`

Para ver apenas os arquivos gerados:
```bash
python cli.py list
```
