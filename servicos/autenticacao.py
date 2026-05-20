import sqlite3
import os
from dados.database import conectar

conn = conectar()
cursor = conn.cursor()

def cadastrar_usuario():
    conn = conectar()
    cursor = conn.cursor()

    os.system('clear')
    nome = input('Nome: ')
    email = input('Email: ')    
    telefone = input('Telefone: ')
    senha = input('Senha: ')
    possui_tipo= input('É Moderador ou Servidor Público? (Se sim, digite "Sim" ou "S")')
    tipo = ''
    while possui_tipo.upper() in ['SIM', 'S']:
        print('[1] - Moderador\n[2] Servidor Público')
        cont = input('Entrada: ')
        if cont == '1':
            tipo = 'moderador'
            possui_tipo = False
        if cont == '2':
            tipo = 'servidor'
            possui_tipo = False
        else:
            possui_tipo = 'Sim'
    try:
        cursor.execute('''
        INSERT INTO usuarios (nome, email, senha, telefone, tipo)
        VALUES (?, ?, ?, ?, ?)
        ''', (nome, email, senha, telefone, tipo))
        conn.commit()
        print('Usuário cadastrado!')
    except sqlite3.IntegrityError:
        print('Erro: email já cadastrado!')


def login():
    email = input('Email: ')
    senha = input('Senha: ')

    cursor.execute('''
    SELECT * FROM usuarios WHERE email = ? AND senha = ?
    ''', (email, senha))

    usuario = cursor.fetchone()

    if usuario:
        print('Login feito!')
        print('Bem-vindo', usuario[1])
        return usuario
    else:
        print('Erro no login!')


def listar():
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()

    if usuarios:
        for u in usuarios:
            print(f'ID: {u[0]} | Nome: {u[1]} | Email: {u[2]} | Tipo: {u[4]}')
    else:
        print('Nenhum usuário cadastrado.')

executando = 0
while executando != 4:
    print('\n1 - Cadastrar')
    print('2 - Login')
    print('3 - Listar')
    print('4 - Sair')

    opcao = input('Escolha: ')

    if opcao == '1':
        cadastrar_usuario()
    elif opcao == '2':
        login()
    elif opcao == '3':
        listar()
    elif opcao == '4':
        print('Encerrando sistema...')
        executando = 4
    else:
        print('Opção inválida')
    

conn.close()