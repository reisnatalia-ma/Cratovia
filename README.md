# Cratovia

Sistema de linha de comando (CLI) para reportar e acompanhar **ocorrências urbanas** e **eventos comunitários** da cidade do Crato (CE). Cidadãos podem publicar relatos (alagamentos, buracos, incêndios, etc.), servidores públicos podem publicar com aprovação automática para sua área, e moderadores cuidam da fila de revisão.

## Funcionalidades

- **Feed público**: qualquer pessoa, mesmo sem login, pode visualizar ocorrências e eventos aprovados, com paginação e filtros por bairro ou categoria.
- **Cadastro e login** de usuários com três perfis:
  - `comum` — cidadão, postagens entram em fila de moderação;
  - `servidor` — vinculado a um órgão (DETRAN, SAMU, Corpo de Bombeiros, Secretaria de Saúde), com publicação aprovada automaticamente;
  - `moderador` — aprova/rejeita postagens de qualquer tipo.
- **Códigos de acesso**: cadastro como servidor ou moderador exige um código válido e de uso único, evitando autopromoção.
- **Publicação de ocorrências e eventos**, com seleção de bairro e natureza/categoria.
- **Interações**: votar como útil, denunciar como falso (oculta automaticamente após denúncias) e comentar.
- **Moderação por órgão**: cada órgão público só pode aprovar ocorrências relacionadas à sua área de atuação; moderadores aprovam tudo.
- **Perfil do usuário**: histórico de postagens/eventos publicados, votos e denúncias recebidos.

## Estrutura do projeto

```
CratoVia
├── main.py                  # Ponto de entrada e menus por tipo de usuário
├── dados/
│   └── database.py          # Conexão SQLite, criação de tabelas e dados iniciais (seed)
├── servicos/
│   ├── autenticacao.py      # Login, cadastro, hash de senha, códigos de acesso
│   ├── feed.py               # Listagem, paginação e filtros de ocorrências/eventos
│   ├── postagens.py          # Criação de ocorrências e eventos
│   ├── moderacao.py          # Fila de revisão e aprovação/rejeição por órgão
│   ├── usuarios.py           # Perfil do usuário
│   └── interacoes.py         # Votos úteis, denúncias e comentários (não incluso neste pacote)
└── utils/
    ├── formatacao.py         # Funções de formatação de tela (linhas, limpar tela, datas)
    └── componentes.py        # Componentes de UI (títulos, mensagens de erro/sucesso)
```


## Modelo de dados (SQLite)

| Tabela | Descrição |
|---|---|
| `usuarios` | Dados de conta, tipo (`comum`/`servidor`/`moderador`), órgão e relevância |
| `codigos_acesso` | Códigos para liberar cadastro de moderador/servidor |
| `bairros` | Lista de bairros e distritos do Crato |
| `naturezas` | Categorias de ocorrência (trânsito, incêndio, alagamento, etc.) |
| `postagens` | Ocorrências publicadas, com status (`aguardando`, `aprovado`, `oculto`) |
| `comentarios` | Comentários em postagens, com suporte a respostas e marcação oficial |
| `votos_uteis` / `denuncias_fake` | Registro de votos e denúncias por usuário (evita duplicidade) |
| `anuncios_eventos` | Eventos comunitários publicados |

O banco é criado automaticamente (`iniciar_tabelas`) e populado com bairros, naturezas, códigos de acesso de exemplo e algumas postagens/eventos de demonstração (`popular_postagens_exemplo`) na primeira execução.

## Como executar

```bash
python main.py
```

Não há dependências externas: o projeto usa apenas a biblioteca padrão do Python (`sqlite3`, `hashlib`, `getpass`, `datetime`, `os`).

### Códigos de acesso de exemplo

| Código                              | Tipo      | Órgão               |
| ----------------------------------- | --------- | ------------------- |
| `MOD-CRATO-2024` / `MOD-CRATO-2025` | moderador | —                   |
| `SERV-DETRAN-001`                   | servidor  | DETRAN              |
| `SERV-SAMU-001`                     | servidor  | SAMU                |
| `SERV-BOMB-001`                     | servidor  | Corpo de Bombeiros  |
| `SERV-SAUDE-001`                    | servidor  | Secretaria de Saúde |
