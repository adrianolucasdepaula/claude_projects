---
description: Atualizar portfolio com novas planilhas semanais
---

Atualizar o portfolio com novas planilhas da semana:

**Passo 1**: Substitua as planilhas antigas pelas novas em `planilhas/`

**Passo 2**: Execute a consolidação completa:
```bash
python cli.py all
```

O sistema irá automaticamente:
- ✅ Criar snapshot datado das novas planilhas
- ✅ Consolidar com deduplicação
- ✅ Comparar com a semana anterior
- ✅ Gerar novos gráficos e relatórios
- ✅ Identificar mudanças significativas

**Passo 3**: Revise os resultados:
```bash
# Ver mudanças entre versões
python cli.py compare

# Ver lista de outputs
python cli.py list
```
