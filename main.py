from dados.database import iniciar_tabelas
from modulos.autenticacao import menu_autenticacao
from modulos.feed import feed_geral, feed_por_bairro, feed_por_natureza
from modulos.postagens import criar_postagem
import os

iniciar_tabelas()
usuario = menu_autenticacao()

while True:
    os.system("clear")
    print("=" * 40)
    print("       CRATOVIA — MENU PRINCIPAL")
    print("=" * 40)
    if usuario:
        print(f"  Logado como: {usuario['nome']} [{usuario['tipo']}]")
    else:
        print("  Visitante (sem login)")
    print("-" * 40)
    print("  1. Ver feed geral")
    print("  2. Filtrar por bairro")
    print("  3. Filtrar por tipo")
    print("  4. Divulgar ocorrência")
    print("  0. Sair")
    print("=" * 40)

    op = input("  Escolha: ").strip()

    if op == "1":
        feed_geral(usuario)
    elif op == "2":
        feed_por_bairro(usuario)
    elif op == "3":
        feed_por_natureza(usuario)
    elif op == "4":
        criar_postagem(usuario)
    elif op == "0":
        print("\nAté logo!")
        break
    else:
        print("  Opção inválida.")
        input("  ENTER para continuar...")