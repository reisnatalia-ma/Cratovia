import hashlib
import getpass
from dados.database import conectar

# =========================
# CRIPTOGRAFAR SENHA
# =========================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# =========================
# CADASTRAR USUÁRIO
# =========================

def cadastrar_usuario(nome, email, telefone, senha, tipo, orgao=None):

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
        INSERT INTO usuarios (nome, email, telefone, senha, tipo, orgao)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (nome, email, telefone, senha_hash, tipo, orgao)
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

def validar_codigo_acesso(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM codigos_acesso WHERE codigo = ? AND usado = 0", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return dict(resultado)
    return None

def marcar_codigo_usado(codigo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE codigos_acesso SET usado = 1 WHERE codigo = ?", (codigo,))
    conn.commit()
    conn.close()



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
        os.system("clear")


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
            senha = getpass.getpass("Senha: ").strip()
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
            telefone = input("Telefone: ").strip()
            senha = getpass.getpass("Senha: ").strip()
            linha_separadora()

            print("Tipo de conta:")
            print(" 1. Cidadão comum")
            print(" 2. Moderador")
            print(" 3. Servidor público")

            linha_separadora()
            escolha_tipo = input("Escolha: ").strip()
            tipo = "comum"

            orgao = None

            if escolha_tipo == "2":
                codigo = input("Insira o código de moderador: ").strip()
                resultado = validar_codigo_acesso(codigo)
                if not resultado or resultado["tipo"] != "moderador":
                    mensagem_erro("Código inválido ou já utilizado.")
                    input("Pressione Enter para tentar novamente...")
                    continue
                marcar_codigo_usado(codigo)
                tipo = "moderador"

            elif escolha_tipo == "3":
                codigo = input("Insira código de servidor público: ").strip()
                resultado = validar_codigo_acesso(codigo)
                if not resultado or resultado["tipo"] != "servidor":
                    mensagem_erro("Código inválido ou já utilizado.")
                    input("Pressione Enter para tentar novamente...")
                    continue
                marcar_codigo_usado(codigo)
                tipo = "servidor"
                orgao = resultado.get("orgao")

            usuario, mensagem = cadastrar_usuario(
                nome,
                email,
                telefone,
                senha,
                tipo,
                orgao
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

            print("\nOpção inválida.")
            input("\nPressione Enter para continuar...")
