import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dados.database import criar_tabelas
from servicos.autenticacao import menu_autenticacao
from servicos.feed import exibir_feed, exibir_eventos, menu_filtrar_bairro, menu_filtrar_natureza
from servicos.postagens import formulario_nova_postagem
from servicos.moderacao import menu_moderacao, pode_moderar
from utils.formatacao import limpar_tela, linha_separadora
from utils.componentes import titulo, exibir_usuario_logado


def menu_principal(usuario):
    while True:
        limpar_tela()
        titulo("CRATOVIA — Ocorrências de Crato")
        exibir_usuario_logado(usuario)

        print("1. Ver últimas ocorrências")
        print("2. Filtrar por bairro")
        print("3. Filtrar por natureza da ocorrência")
        print("4. Fazer uma postagem")
        print("5. Eventos")

        if pode_moderar(usuario):
            print("6. Moderação")

        print("0. Sair")
        linha_separadora()

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            exibir_feed(usuario=usuario)

        elif opcao == "2":
            menu_filtrar_bairro(usuario=usuario)

        elif opcao == "3":
            menu_filtrar_natureza(usuario=usuario)

        elif opcao == "4":
            if usuario:
                formulario_nova_postagem(usuario)
            else:
                from utils.componentes import mensagem_erro
                mensagem_erro("Você precisa fazer login para publicar.")
                input("Pressione Enter para continuar...")

        elif opcao == "5":
            exibir_eventos(usuario=usuario)

        elif opcao == "6" and pode_moderar(usuario):
            menu_moderacao(usuario)

        elif opcao == "0":
            limpar_tela()
            print("Até logo!")
            break


def main():
    criar_tabelas()
    usuario = menu_autenticacao()
    menu_principal(usuario)


if __name__ == "__main__":
    main()