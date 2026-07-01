import os


def linha_separadora():
    print("-" * 60)


def linha_dupla():
    print("=" * 60)


def centralizar(texto):
    print(texto.center(60))


def limpar_tela():
    os.system("clear")


def formatar_data(criado_em):
    try:
        data, hora = criado_em.split(" ")
        a, m, d = data.split("-")
        return f"{d}/{m}/{a} às {hora[:5]}"
    except Exception:
        return criado_em
