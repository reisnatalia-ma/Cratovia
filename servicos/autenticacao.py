
import hashlib
from dados.database import conectar

# =========================
# CRIPTOGRAFAR SENHA
# =========================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# =========================
# CADASTRAR USUÁRIO
# =========================

def cadastrar_usuario(nome, email, senha):

    conn = conectar()
    cursor = conn.cursor()

    # verifica se email já existe
    cursor.execute(
        "SELECT id FROM usuarios WHERE email = ?",
        (email,)
    )

    if cursor.fetchone():
        conn.close()
        return None, "E-mail já cadastrado."

    senha_hash = hash_senha(senha)

    # cadastra usuário
    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (?, ?, ?, 'comum')
        """,
        (nome, email, senha_hash)
    )

    conn.commit()

    # pega id do usuário criado
    usuario_id = cursor.lastrowid

    # busca usuário recém criado
    cursor.execute(
        """
        SELECT * FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    )

    usuario = cursor.fetchone()

    conn.close()

    # retorna usuário completo
    return dict(usuario), "Cadastro realizado com sucesso!"


# =========================
# LOGIN
# =========================

def fazer_login(email, senha):

    conn = conectar()
    cursor = conn.cursor()

    senha_hash = hash_senha(senha)

    cursor.execute(
        """
        SELECT * FROM usuarios
        WHERE email = ? AND senha = ?
        """,
        (email, senha_hash)
    )

    usuario = cursor.fetchone()

    conn.close()

    if usuario:
        return dict(usuario), "Login realizado com sucesso!"

    return None, "E-mail ou senha incorretos."


# =========================
# BUSCAR USUÁRIO
# =========================

def buscar_usuario_por_id(usuario_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (usuario_id,)
    )

    usuario = cursor.fetchone()

    conn.close()

    if usuario:
        return dict(usuario)

    return None


# =========================
# MENU
# =========================

def menu_autenticacao():

    def titulo(texto):

        print("\n" + "=" * 40)
        print(texto)
        print("=" * 40)


    def mensagem_erro(msg):

        print(f"\n[ERRO] {msg}")


    def mensagem_sucesso(msg):

        print(f"\n[SUCESSO] {msg}")


    def limpar_tela():

        import os
        os.system("cls")


    def linha_separadora():

        print("=" * 40)
        

    while True:

        limpar_tela()

        titulo("ACESSO AO CRATOVIA")

        print("1. Fazer login")
        print("2. Criar conta")
        print("3. Continuar sem login")
        print("0. Sair")

        linha_separadora()

        opcao = input("Escolha: ").strip()

        # =========================
        # LOGIN
        # =========================

        if opcao == "1":

            limpar_tela()

            titulo("LOGIN")

            email = input("E-mail: ").strip()
            senha = input("Senha: ").strip()

            usuario, mensagem = fazer_login(
                email,
                senha
            )

            if usuario:

                mensagem_sucesso(mensagem)

                print(f"\nBem-vindo(a), {usuario['nome']}!")

                input("\nPressione Enter para continuar...")

                return usuario

            else:

                mensagem_erro(mensagem)

                input("\nPressione Enter para tentar novamente...")

        # =========================
        # CADASTRO
        # =========================

        elif opcao == "2":

            limpar_tela()

            titulo("CRIAR CONTA")

            nome = input("Nome: ").strip()
            email = input("E-mail: ").strip()
            senha = input("Senha: ").strip()

            usuario, mensagem = cadastrar_usuario(
                nome,
                email,
                senha
            )

            if usuario:

                mensagem_sucesso(mensagem)

                print(f"\nConta criada para {usuario['nome']}!")

                input("\nPressione Enter para continuar...")

                return usuario

            else:

                mensagem_erro(mensagem)

                input("\nPressione Enter para tentar novamente...")

        # =========================
        # CONTINUAR SEM LOGIN
        # =========================

        elif opcao == "3":
            return None

        # =========================
        # SAIR
        # =========================

        elif opcao == "0":
            exit()

        else:

            print("\nOpção inválida.")
            input("\nPressione Enter para continuar...")


# =========================
# INICIAR MENU
# =========================

menu_autenticacao()
