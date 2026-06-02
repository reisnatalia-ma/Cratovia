from servicos.postagens import nova_postagem
from dados.database import iniciar_tabelas
from servicos.autenticacao import menu_autenticacao


iniciar_tabelas()
usuario = menu_autenticacao()

nova_postagem(usuario)