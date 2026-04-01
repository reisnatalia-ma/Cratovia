print("Dev de usuários)
import csv

def cadastrar_usuario():
    nome = input('Nome: ')
    email = input('Email: ')
    senha = input('Senha: ')
    tipo = input('Tipo (morador/servidor): ')
    try:
        arquivo = open('usuarios.txt', 'a')
        leitura = open('usuarios.txt', 'r')
        linhas = leitura.readlines() + 1
    except:
        novo_id = 1

    linha = str(novo_id) + ',' + nome + ',' + senha + ',' + tipo + '\n'
    arquivo.write(linha)
    arquivo.close()

    print('Usuário cadastrado!')


def login():
    email = input('Email: ')
    senha = input("Senha: ")

    arquivo = open('usuarios.txt', 'r')
    linhas = arquivo.readlines()

    for linha in linhas:
        dados = linha.strip.split(',')

        if dados[2] == email and dados[3] == senha:
            print('Login feito! ')
            print('Bem-vindo', dados[1])
            arquivo.close()
            return
    arquivo.close()
    print('Erro no login!')

def listar():
    arquivo = open('usuarios.txt', 'r')
    linhas = arquivo.readlines()

    for linha in linhas:
        print(linha)

    arquivo.close()

while True:
    print('\n1 - Cadastrar' )
    print('2 - Login')
    print('3 - Listar')
    print('4 - Sair')

    opçao = input('Escolha: ')

    if opçao == '1':
        cadastrar_usuario()
    elif opçao == '2':
        login()
    elif opçao == '3':
        listar()
    elif opçao == '0':
        break
    else:
        print('Opçao inválida')
