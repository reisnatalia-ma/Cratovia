import os
from datetime import datetime

# ── Limpar terminal ──────────────────────────────────────────────────────────
def limpar():
    os.system("cls" if os.name == "nt" else "clear")

# ── Cabeçalho padrão ─────────────────────────────────────────────────────────
def cabecalho(titulo=""):
    limpar()
    print("=" * 50)
    print("       CIDADE DO CRATO — Sistema de Ocorrências")
    print("=" * 50)
    if titulo:
        print(f"  {titulo}")
        print("-" * 50)

# ── Pausar tela ───────────────────────────────────────────────────────────────
def pausar():
    input("\nPressione ENTER para continuar...")

# ── Data e hora atual ─────────────────────────────────────────────────────────
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── Formatar só a hora ────────────────────────────────────────────────────────
def so_hora(data_hora):
    try:
        dt = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%H:%M")
    except:
        return data_hora

# ── Formatar data completa ────────────────────────────────────────────────────
def formatar_data(data_hora):
    try:
        dt = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return data_hora

# ── Paginação ─────────────────────────────────────────────────────────────────
def paginar(lista, por_pagina, pagina):
    total_paginas = max(1, (len(lista) + por_pagina - 1) // por_pagina)
    pagina = max(1, min(pagina, total_paginas))
    inicio = (pagina - 1) * por_pagina
    fim    = inicio + por_pagina
    return lista[inicio:fim], pagina, total_paginas
