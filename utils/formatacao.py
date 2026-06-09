import os

def linha_separadora():
    print("-" * 60)

def linha_dupla():
    print("=" * 60)

def centralizar(texto):
    print(texto.center(60))

def formatar_data_hora(data, hora):
    return f"{data} às {hora}"

def limpar_tela():
    os.system("clear")