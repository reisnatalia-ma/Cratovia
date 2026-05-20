from servicos.postagens import nova_postagem
from dados.database import iniciar_tabelas
from servicos.autenticacao import listar


iniciar_tabelas()
usuario = listar()

nova_postagem(usuario)