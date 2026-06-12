# CRATOVIA 🏙️

**Plataforma de ocorrências e notícias comunitárias de Crato-CE**

---

## Como executar

```bash
python main.py
```

> Requer Python 3.10+. Nenhuma dependência externa — usa apenas a biblioteca padrão.

---

## Estrutura do projeto

```
CRATOVIA/
├── main.py                  # Ponto de entrada e menus
├── cratovia.db              # Banco SQLite (criado automaticamente)
│
├── dados/
│   └── database.py          # Conexão SQLite e criação de tabelas
│
├── modulos/
│   ├── usuarios.py          # Cadastro, login, perfil
│   ├── postagens.py         # Criar e visualizar ocorrências
│   ├── interacoes.py        # Votar útil, denunciar, comentar
│   ├── feed.py              # Feed e filtros de ocorrências
│   ├── moderacao.py         # Painel do moderador
│   └── utils.py             # Utilitários de terminal
│
└── servicos/
    └── postagens.py         # Anúncios e eventos (servidores)
```

---

## Tipos de usuário

| Tipo        | O que pode fazer                                                |
|-------------|------------------------------------------------------------------|
| **Cidadão** | Publicar ocorrências, votar, denunciar, comentar                |
| **Servidor**| Tudo do cidadão + publicar anúncios e eventos oficiais          |
| **Moderador**| Tudo + aprovar/rejeitar postagens e anúncios                   |

### Códigos de acesso (pré-cadastrados)

| Código            | Tipo       | Órgão              |
|-------------------|------------|--------------------|
| `MOD-CRATO-2024`  | Moderador  | —                  |
| `MOD-CRATO-2025`  | Moderador  | —                  |
| `SERV-DETRAN-001` | Servidor   | DETRAN             |
| `SERV-SAMU-001`   | Servidor   | SAMU               |
| `SERV-BOMB-001`   | Servidor   | Corpo de Bombeiros |
| `SERV-SAUDE-001`  | Servidor   | Secretaria de Saúde|

---

## Regras de negócio

- Postagens e anúncios entram com status **aguardando** e precisam de aprovação do moderador
- Uma postagem com **5 ou mais denúncias** é removida automaticamente
- **Pontuação de relevância:**
  - +1 pt ao publicar uma ocorrência
  - +5 pts ao ter uma postagem aprovada
  - +2 pts por cada voto útil recebido

### Níveis de confiabilidade

| Pontos   | Nível               |
|----------|---------------------|
| 0–9      | ⭐ Cidadão          |
| 10–49    | ⭐⭐ Confiável      |
| 50+      | ⭐⭐⭐ Muito Confiável|