from dados.database import conectar
from utils.formatacao import linha_separadora, linha_dupla, limpar_tela, formatar_data
from utils.componentes import titulo


def _tipo_legivel(tipo):
    tipos = {
        "comum":     "Cidadão comum",
        "moderador": "Moderador",
        "servidor":  "Servidor público"
    }
    return tipos.get(tipo, tipo)


def _buscar_postagens_usuario(usuario_id):
    with conectar() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT p.id, p.titulo, p.descricao, p.status, p.votos_uteis, p.denuncias, p.criado_em, b.nome AS bairro_nome, n.nome AS natureza_nome
            FROM postagens p
            LEFT JOIN bairros b ON b.id = p.bairro_id
            LEFT JOIN naturezas n ON n.id = p.natureza_id
            WHERE p.usuario_id = ?
            ORDER BY p.criado_em DESC
        """, (usuario_id,)).fetchall()]

def _buscar_eventos_usuario(usuario_id):
    with conectar() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT e.id, e.titulo, e.descricao, e.status, e.criado_em, b.nome AS bairro_nome
            FROM anuncios_eventos e
            LEFT JOIN bairros b ON b.id = e.bairro_id
            WHERE e.usuario_id = ?
            ORDER BY e.criado_em DESC
        """, (usuario_id,)).fetchall()]

def _totais_usuario(usuario_id):
    with conectar() as conn:
        votos = conn.execute("""
            SELECT COALESCE(SUM(p.votos_uteis), 0)
            FROM postagens p
            WHERE p.usuario_id = ?
        """, (usuario_id,)).fetchone()[0]

        denuncias = conn.execute("""
            SELECT COALESCE(SUM(p.denuncias), 0)
            FROM postagens p
            WHERE p.usuario_id = ?
        """, (usuario_id,)).fetchone()[0]

    return votos, denuncias


def ver_perfil(usuario):
    while True:
        limpar_tela()
        titulo("MEU PERFIL")

        uid = usuario["id"]
        votos, denuncias = _totais_usuario(uid)
        postagens = _buscar_postagens_usuario(uid)
        eventos = _buscar_eventos_usuario(uid)

        # Dados pessoais
        print(f"  Nome:       {usuario['nome']}")
        print(f"  E-mail:     {usuario['email']}")
        print(f"  Tipo:       {_tipo_legivel(usuario['tipo'])}")
        if usuario.get("orgao"):
            print(f"  Órgão:      {usuario['orgao']}")
        print(f"  Relevância: {usuario.get('relevancia', 0)} ponto(s)")

        linha_separadora()

        print(f"  Votos úteis recebidos:  {votos}")
        print(f"  Denúncias recebidas:    {denuncias}")

        linha_separadora()

        # Ocorrências
        print(f"\n  OCORRÊNCIAS PUBLICADAS ({len(postagens)})\n")

        if not postagens:
            print("  Nenhuma ocorrência ainda.")
        else:
            for i, p in enumerate(postagens, 1):
                status_label = {
                    "aprovado":   "✓ Aprovado",
                    "aguardando": "⏳ Pendente",
                    "oculto":     "✗ Oculto"
                }.get(p["status"], p["status"])

                print(f"  [{i}] {p['titulo']}")
                print(f"       {p['bairro_nome'] or '—'} · {p.get('natureza_nome') or '—'}")
                print(f"       {formatar_data(p['criado_em'])} · {status_label}")
                print(f"       👍 {p['votos_uteis']}  🚩 {p['denuncias']}")
                linha_separadora()

        # Eventos
        print(f"\n  EVENTOS PUBLICADOS ({len(eventos)})\n")

        if not eventos:
            print("  Nenhum evento ainda.")
        else:
            for i, e in enumerate(eventos, 1):
                status_label = {
                    "aprovado":   "✓ Aprovado",
                    "aguardando": "⏳ Pendente",
                    "oculto":     "✗ Oculto"
                }.get(e["status"], e["status"])

                print(f"  [{i}] {e['titulo']}")
                print(f"       {e['bairro_nome'] or '—'}")
                print(f"       {formatar_data(e['criado_em'])} · {status_label}")
                linha_separadora()

        print("\n  [X] Voltar")
        op = input("\n  Ação: ").strip().upper()

        if op == "X":
            return
