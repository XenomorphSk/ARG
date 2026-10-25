#!/usr/bin/env python3
"""
Desloca o calendário de publicação inteiro em N dias (positivo adia, negativo antecipa).

Uso:
    python tools/remarcar.py 14      adia tudo duas semanas
    python tools/remarcar.py -7      antecipa uma semana

Mexe no publish_date das entradas e dos livros do Osmar e em LOG_OFFSET_DAYS do build.py,
para que entradas, registros e livros continuem andando juntos.
"""
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    dias = int(sys.argv[1])
    delta = dt.timedelta(days=dias)

    def troca(m):
        nova = dt.date.fromisoformat(m.group(2)) + delta
        return f"{m.group(1)}{nova.isoformat()}"

    arquivos = sorted((ROOT / "content" / "entries").glob("*.md")) + sorted((ROOT / "content" / "osmar").glob("*.md"))
    for path in arquivos:
        texto = path.read_text(encoding="utf-8")
        novo = re.sub(r"^(publish_date:\s*)(\d{4}-\d{2}-\d{2})", troca, texto, count=1, flags=re.M)
        path.write_text(novo, encoding="utf-8")

    build = ROOT / "build.py"
    texto = build.read_text(encoding="utf-8")
    atual = int(re.search(r"^LOG_OFFSET_DAYS = (-?\d+)", texto, re.M).group(1))
    texto = re.sub(r"^LOG_OFFSET_DAYS = -?\d+", f"LOG_OFFSET_DAYS = {atual + dias}", texto, count=1, flags=re.M)
    build.write_text(texto, encoding="utf-8")

    print(f"{len(arquivos)} arquivos remarcados em {dias:+d} dias. LOG_OFFSET_DAYS: {atual} -> {atual + dias}")
    if dias % 7:
        print("aviso: deslocamento fora de múltiplo de 7, os dias da semana deixam de bater com o diário")
    return 0


if __name__ == "__main__":
    sys.exit(main())
