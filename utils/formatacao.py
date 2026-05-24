import os

LARGURA = 60


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def linha_separadora():
    print("-" * LARGURA)


def linha_dupla():
    print("=" * LARGURA)


def centralizar(texto):
    print(texto.center(LARGURA))


def formatar_data_hora(data, hora):
    return f"{data} às {hora}"