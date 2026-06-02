
from utils.formatacao import linha_dupla, linha_separadora, centralizar

def titulo(texto):
    linha_dupla()
    centralizar(f"  {texto}  ")
    linha_dupla()
    print()

def mensagem_sucesso(texto):
    print(f"\n[OK] {texto}\n")

def mensagem_erro(texto):
    print(f"\n[ERRO] {texto}\n")