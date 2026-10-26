"""Ativacao e etapas com progresso calculado e sequencia coerente (US09)."""

from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import Enum

from src.domain.erros import DadoInvalido


class StatusAtivacao(str, Enum):
    nao_iniciada = "nao_iniciada"
    em_andamento = "em_andamento"
    concluida = "concluida"
    cancelada = "cancelada"


class StatusEtapaAtivacao(str, Enum):
    concluida = "concluida"
    atual = "atual"
    pendente = "pendente"


def _data_com_fuso(valor: datetime, campo: str) -> None:
    if valor.tzinfo is None or valor.utcoffset() is None:
        raise DadoInvalido(campo, "Data e hora devem incluir fuso horario.")


@dataclass(frozen=True)
class EtapaAtivacao:
    id: str
    ordem: int
    nome: str
    status: StatusEtapaAtivacao
    concluida_em: datetime | None = None
    previsao_conclusao: date | None = None

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.nome.strip():
            raise DadoInvalido("etapas", "A etapa precisa de identificador e nome.")
        if self.ordem < 1:
            raise DadoInvalido("ordem", "A ordem da etapa deve ser positiva.")
        try:
            object.__setattr__(self, "status", StatusEtapaAtivacao(self.status))
        except ValueError:
            raise DadoInvalido("status", "Status da etapa deve ser concluida, atual ou pendente.") from None
        if self.concluida_em is not None:
            _data_com_fuso(self.concluida_em, "concluida_em")
            if self.status is not StatusEtapaAtivacao.concluida:
                raise DadoInvalido("concluida_em", "Somente uma etapa concluida tem data de conclusao.")

    def iniciar(self) -> "EtapaAtivacao":
        if self.status is not StatusEtapaAtivacao.pendente:
            raise DadoInvalido("status", "Somente uma etapa pendente pode ser iniciada.")
        return replace(self, status=StatusEtapaAtivacao.atual)

    def concluir(self, ocorrido_em: datetime) -> "EtapaAtivacao":
        if self.status is not StatusEtapaAtivacao.atual:
            raise DadoInvalido("status", "Somente a etapa atual pode ser concluida.")
        return replace(
            self, status=StatusEtapaAtivacao.concluida,
            concluida_em=ocorrido_em, previsao_conclusao=None,
        )


@dataclass(frozen=True)
class Ativacao:
    cliente_id: str
    status: StatusAtivacao
    etapas: tuple[EtapaAtivacao, ...]
    atualizado_em: datetime
    iniciada_em: date | None = None
    previsao_conclusao: date | None = None

    def __post_init__(self) -> None:
        if not self.cliente_id.strip():
            raise DadoInvalido("cliente_id", "A ativacao precisa de um cliente.")
        _data_com_fuso(self.atualizado_em, "atualizado_em")
        try:
            object.__setattr__(self, "status", StatusAtivacao(self.status))
        except ValueError:
            raise DadoInvalido("status", "Status de ativacao invalido.") from None
        etapas = tuple(sorted(self.etapas, key=lambda etapa: etapa.ordem))
        if not etapas:
            raise DadoInvalido("etapas", "A ativacao precisa de pelo menos uma etapa.")
        if len({e.id for e in etapas}) != len(etapas) or len({e.ordem for e in etapas}) != len(etapas):
            raise DadoInvalido("etapas", "Identificadores e ordens de etapas devem ser unicos.")
        object.__setattr__(self, "etapas", etapas)
        estados = [e.status for e in etapas]
        concluidas = estados.count(StatusEtapaAtivacao.concluida)
        atuais = estados.count(StatusEtapaAtivacao.atual)
        esperados = [StatusEtapaAtivacao.concluida] * concluidas
        esperados += [StatusEtapaAtivacao.atual] * atuais
        esperados += [StatusEtapaAtivacao.pendente] * (len(etapas) - concluidas - atuais)
        if atuais > 1 or estados != esperados:
            raise DadoInvalido("etapas", "Etapas devem seguir a ordem concluida, atual e pendente.")
        if self.status is StatusAtivacao.em_andamento and atuais != 1:
            raise DadoInvalido("etapas", "Ativacao em andamento precisa de uma unica etapa atual.")
        if self.status is not StatusAtivacao.em_andamento and atuais:
            raise DadoInvalido("etapas", "Somente uma ativacao em andamento pode ter etapa atual.")
        if self.status is StatusAtivacao.nao_iniciada and concluidas:
            raise DadoInvalido("status", "Ativacao nao iniciada nao pode ter etapas concluidas.")
        if self.status is StatusAtivacao.concluida and concluidas != len(etapas):
            raise DadoInvalido("status", "Ativacao concluida exige todas as etapas concluidas.")
        if concluidas == len(etapas) and self.status is not StatusAtivacao.concluida:
            raise DadoInvalido("status", "Todas as etapas concluidas exigem ativacao concluida.")

    def calcular_percentual(self) -> int:
        """Percentual inteiro, truncado, calculado somente das etapas concluidas."""
        concluidas = sum(e.status is StatusEtapaAtivacao.concluida for e in self.etapas)
        return concluidas * 100 // len(self.etapas)

    def obter_etapa_atual(self) -> EtapaAtivacao | None:
        return next((e for e in self.etapas if e.status is StatusEtapaAtivacao.atual), None)

    def concluir_etapa_atual(self, ocorrido_em: datetime) -> "Ativacao":
        atual = self.obter_etapa_atual()
        if self.status is not StatusAtivacao.em_andamento or atual is None:
            raise DadoInvalido("status", "A ativacao nao tem etapa em andamento para concluir.")
        _data_com_fuso(ocorrido_em, "ocorrido_em")
        if ocorrido_em < self.atualizado_em:
            raise DadoInvalido("ocorrido_em", "A conclusao nao pode preceder a ultima atualizacao.")
        etapas = list(self.etapas)
        indice = etapas.index(atual)
        etapas[indice] = atual.concluir(ocorrido_em)
        status = StatusAtivacao.concluida
        if indice + 1 < len(etapas):
            etapas[indice + 1] = etapas[indice + 1].iniciar()
            status = StatusAtivacao.em_andamento
        return replace(
            self, etapas=tuple(etapas), status=status, atualizado_em=ocorrido_em,
            previsao_conclusao=None if status is StatusAtivacao.concluida else self.previsao_conclusao,
        )
