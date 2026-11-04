"""Modelos das tabelas de usinas, creditos e depoimentos."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.db.tipos import DataHoraComFuso
from src.domain.competencia import Competencia
from src.domain.credito_usina import CreditoUsina
from src.domain.depoimento import Depoimento
from src.domain.dinheiro import Dinheiro
from src.domain.usina import Usina


class UsinaModel(Base):
    __tablename__ = "usinas"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(2))
    regiao: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), index=True)
    atualizada_em: Mapped[datetime] = mapped_column(DataHoraComFuso())

    @classmethod
    def de_dominio(cls, usina: Usina) -> "UsinaModel":
        return cls(
            id=usina.id,
            nome=usina.nome,
            cidade=usina.cidade,
            estado=usina.estado,
            regiao=usina.regiao,
            status=usina.status.value,
            atualizada_em=usina.atualizada_em,
        )

    def para_dominio(self) -> Usina:
        return Usina(
            id=self.id,
            nome=self.nome,
            cidade=self.cidade,
            estado=self.estado,
            regiao=self.regiao,
            status=self.status,
            atualizada_em=self.atualizada_em,
        )


class CreditoUsinaModel(Base):
    __tablename__ = "creditos_usinas"

    usina_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("usinas.id", ondelete="CASCADE"), primary_key=True
    )
    competencia: Mapped[str] = mapped_column(String(7), primary_key=True, index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    moeda: Mapped[str] = mapped_column(String(3))
    atualizado_em: Mapped[datetime] = mapped_column(DataHoraComFuso())

    @classmethod
    def de_dominio(cls, credito: CreditoUsina) -> "CreditoUsinaModel":
        return cls(
            usina_id=credito.usina_id,
            competencia=str(credito.competencia),
            valor=credito.creditos.valor,
            moeda=credito.creditos.moeda,
            atualizado_em=credito.atualizado_em,
        )

    def para_dominio(self) -> CreditoUsina:
        return CreditoUsina(
            usina_id=self.usina_id,
            competencia=Competencia.de_texto(self.competencia),
            creditos=Dinheiro(Decimal(self.valor), self.moeda),
            atualizado_em=self.atualizado_em,
        )


class DepoimentoModel(Base):
    __tablename__ = "depoimentos"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    nome_publico: Mapped[str] = mapped_column(String(100))
    localidade: Mapped[str] = mapped_column(String(100))
    avaliacao: Mapped[int] = mapped_column(Integer)
    texto: Mapped[str] = mapped_column(Text)
    publicacao_autorizada: Mapped[bool] = mapped_column(Boolean, default=False)
    economia_mensal_valor: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    economia_mensal_moeda: Mapped[str | None] = mapped_column(String(3), nullable=True)
    dias_para_ativacao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentual_desconto: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    tempo_conta_ativa_meses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cliente_id: Mapped[str | None] = mapped_column(String(40), nullable=True)

    @classmethod
    def de_dominio(cls, depoimento: Depoimento) -> "DepoimentoModel":
        economia = depoimento.economia_mensal
        return cls(
            id=depoimento.id,
            nome_publico=depoimento.nome_publico,
            localidade=depoimento.localidade,
            avaliacao=depoimento.avaliacao,
            texto=depoimento.texto,
            publicacao_autorizada=depoimento.publicacao_autorizada,
            economia_mensal_valor=economia.valor if economia else None,
            economia_mensal_moeda=economia.moeda if economia else None,
            dias_para_ativacao=depoimento.dias_para_ativacao,
            percentual_desconto=depoimento.percentual_desconto,
            tempo_conta_ativa_meses=depoimento.tempo_conta_ativa_meses,
            cliente_id=depoimento.cliente_id,
        )

    def para_dominio(self) -> Depoimento:
        economia = (
            Dinheiro(Decimal(self.economia_mensal_valor), self.economia_mensal_moeda or "BRL")
            if self.economia_mensal_valor is not None
            else None
        )
        return Depoimento(
            id=self.id,
            nome_publico=self.nome_publico,
            localidade=self.localidade,
            avaliacao=self.avaliacao,
            texto=self.texto,
            publicacao_autorizada=self.publicacao_autorizada,
            economia_mensal=economia,
            dias_para_ativacao=self.dias_para_ativacao,
            percentual_desconto=self.percentual_desconto,
            tempo_conta_ativa_meses=self.tempo_conta_ativa_meses,
            cliente_id=self.cliente_id,
        )
