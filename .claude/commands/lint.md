---
description: Check Python code style with flake8 or ruff
---

Check the Python code style and quality for this project. If arguments are provided, check specific files: `$ARGUMENTS`

If ruff is available, use it; otherwise fall back to flake8:
```bash
ruff check . || flake8 .
```
