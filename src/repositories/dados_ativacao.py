"""Ativacoes ficticias da demonstracao; nao representam a jornada oficial da Bulbe."""

from datetime import date, datetime

from src.domain.ativacao import Ativacao, EtapaAtivacao, StatusAtivacao, StatusEtapaAtivacao
from src.repositories.dados_exemplo import BRASILIA


def ativacoes_exemplo() -> list[Ativacao]:
    """Uma ativacao em andamento e outra concluida, novas a cada chamada."""
    nomes = ("Cadastro recebido", "Documentacao validada", "Homologacao", "Creditos ativos")
    atualizacao = datetime(2026, 10, 20, 9, tzinfo=BRASILIA)
    andamento = tuple(
        EtapaAtivacao(
            id=f"etapa_{ordem:02d}", ordem=ordem, nome=nome,
            status=(StatusEtapaAtivacao.concluida if ordem < 3 else
                    StatusEtapaAtivacao.atual if ordem == 3 else StatusEtapaAtivacao.pendente),
            concluida_em=datetime(2026, 10, ordem + 1, 9, tzinfo=BRASILIA) if ordem < 3 else None,
            previsao_conclusao=date(2026, 10, 28) if ordem >= 3 else None,
        )
        for ordem, nome in enumerate(nomes, 1)
    )
    concluida = tuple(
        EtapaAtivacao(
            id=f"etapa_{ordem:02d}", ordem=ordem, nome=nome,
            status=StatusEtapaAtivacao.concluida,
            concluida_em=datetime(2026, 9, ordem + 1, 9, tzinfo=BRASILIA),
        )
        for ordem, nome in enumerate(nomes, 1)
    )
    return [
        Ativacao("cliente_01", StatusAtivacao.em_andamento, andamento, atualizacao,
                 iniciada_em=date(2026, 10, 1), previsao_conclusao=date(2026, 10, 28)),
        Ativacao("cliente_02", StatusAtivacao.concluida, concluida,
                 datetime(2026, 9, 5, 9, tzinfo=BRASILIA), iniciada_em=date(2026, 9, 1)),
    ]
