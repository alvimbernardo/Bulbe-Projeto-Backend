"""Modelos das tabelas do banco da API Bulbe."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, LargeBinary, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.tipos import DataHoraComFuso
from src.domain.ativacao import Ativacao, EtapaAtivacao
from src.domain.cliente import Cliente
from src.domain.competencia import Competencia
from src.domain.conta import Conta
from src.domain.credito_usina import CreditoUsina
from src.domain.depoimento import Depoimento
from src.domain.dinheiro import Dinheiro
from src.domain.fatura import Fatura
from src.domain.pagamento import Pagamento
from src.domain.preferencia_notificacao import PreferenciaNotificacao
from src.domain.repasse import EtapaRepasse, Repasse
from src.domain.sessao import Sessao
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


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    nome_exibicao: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254))
    status: Mapped[str] = mapped_column(String(20))
    identificador_cliente: Mapped[str] = mapped_column(String(40), unique=True)
    codigo_verificacao: Mapped[str] = mapped_column(String(40))

    @classmethod
    def de_dominio(cls, cliente: Cliente) -> "ClienteModel":
        return cls(
            id=cliente.id,
            nome_exibicao=cliente.nome_exibicao,
            email=cliente.email,
            status=cliente.status,
            identificador_cliente=cliente.identificador_cliente,
            codigo_verificacao=cliente.codigo_verificacao,
        )

    def para_dominio(self) -> Cliente:
        return Cliente(
            id=self.id,
            nome_exibicao=self.nome_exibicao,
            email=self.email,
            status=self.status,
            identificador_cliente=self.identificador_cliente,
            codigo_verificacao=self.codigo_verificacao,
        )


class ContaModel(Base):
    __tablename__ = "contas"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    cliente_id: Mapped[str] = mapped_column(String(40), ForeignKey("clientes.id"), unique=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    senha_hash: Mapped[bytes] = mapped_column(LargeBinary(60))
    status: Mapped[str] = mapped_column(String(20))
    criada_em: Mapped[datetime] = mapped_column(DataHoraComFuso())

    @classmethod
    def de_dominio(cls, conta: Conta) -> "ContaModel":
        return cls(
            id=conta.id,
            cliente_id=conta.cliente_id,
            email=conta.email,
            senha_hash=conta.senha_hash,
            status=conta.status,
            criada_em=conta.criada_em,
        )

    def para_dominio(self) -> Conta:
        return Conta(
            id=self.id,
            cliente_id=self.cliente_id,
            email=self.email,
            senha_hash=bytes(self.senha_hash),
            status=self.status,
            criada_em=self.criada_em,
        )


class SessaoModel(Base):
    __tablename__ = "sessoes"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    conta_id: Mapped[str] = mapped_column(String(60), ForeignKey("contas.id", ondelete="CASCADE"), index=True)
    cliente_id: Mapped[str] = mapped_column(String(40), ForeignKey("clientes.id"))
    criada_em: Mapped[datetime] = mapped_column(DataHoraComFuso())
    expira_em: Mapped[datetime] = mapped_column(DataHoraComFuso())
    invalidada_em: Mapped[datetime | None] = mapped_column(DataHoraComFuso(), nullable=True)

    @classmethod
    def de_dominio(cls, sessao: Sessao) -> "SessaoModel":
        return cls(
            id=sessao.id,
            conta_id=sessao.conta_id,
            cliente_id=sessao.cliente_id,
            criada_em=sessao.criada_em,
            expira_em=sessao.expira_em,
            invalidada_em=sessao.invalidada_em,
        )

    def para_dominio(self) -> Sessao:
        return Sessao(
            id=self.id,
            conta_id=self.conta_id,
            cliente_id=self.cliente_id,
            criada_em=self.criada_em,
            expira_em=self.expira_em,
            invalidada_em=self.invalidada_em,
        )


class AtivacaoModel(Base):
    __tablename__ = "ativacoes"

    cliente_id: Mapped[str] = mapped_column(String(40), ForeignKey("clientes.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(20))
    atualizado_em: Mapped[datetime] = mapped_column(DataHoraComFuso())
    iniciada_em: Mapped[date | None] = mapped_column(Date, nullable=True)
    previsao_conclusao: Mapped[date | None] = mapped_column(Date, nullable=True)
    etapas: Mapped[list["EtapaAtivacaoModel"]] = relationship(
        cascade="all, delete-orphan", order_by="EtapaAtivacaoModel.ordem", lazy="selectin"
    )

    @classmethod
    def de_dominio(cls, ativacao: Ativacao) -> "AtivacaoModel":
        return cls(
            cliente_id=ativacao.cliente_id,
            status=ativacao.status.value,
            atualizado_em=ativacao.atualizado_em,
            iniciada_em=ativacao.iniciada_em,
            previsao_conclusao=ativacao.previsao_conclusao,
            etapas=[EtapaAtivacaoModel.de_dominio(ativacao.cliente_id, etapa) for etapa in ativacao.etapas],
        )

    def para_dominio(self) -> Ativacao:
        return Ativacao(
            cliente_id=self.cliente_id,
            status=self.status,
            etapas=tuple(etapa.para_dominio() for etapa in self.etapas),
            atualizado_em=self.atualizado_em,
            iniciada_em=self.iniciada_em,
            previsao_conclusao=self.previsao_conclusao,
        )


class EtapaAtivacaoModel(Base):
    __tablename__ = "etapas_ativacao"

    cliente_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("ativacoes.cliente_id", ondelete="CASCADE"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    ordem: Mapped[int] = mapped_column(Integer)
    nome: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    concluida_em: Mapped[datetime | None] = mapped_column(DataHoraComFuso(), nullable=True)
    previsao_conclusao: Mapped[date | None] = mapped_column(Date, nullable=True)

    @classmethod
    def de_dominio(cls, cliente_id: str, etapa: EtapaAtivacao) -> "EtapaAtivacaoModel":
        return cls(
            cliente_id=cliente_id,
            id=etapa.id,
            ordem=etapa.ordem,
            nome=etapa.nome,
            status=etapa.status.value,
            concluida_em=etapa.concluida_em,
            previsao_conclusao=etapa.previsao_conclusao,
        )

    def para_dominio(self) -> EtapaAtivacao:
        return EtapaAtivacao(
            id=self.id,
            ordem=self.ordem,
            nome=self.nome,
            status=self.status,
            concluida_em=self.concluida_em,
            previsao_conclusao=self.previsao_conclusao,
        )


class FaturaModel(Base):
    __tablename__ = "faturas"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    cliente_id: Mapped[str] = mapped_column(String(40), ForeignKey("clientes.id"), index=True)
    identificador_exibivel: Mapped[str] = mapped_column(String(40))
    competencia: Mapped[str] = mapped_column(String(7))
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    moeda: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20))
    vencimento: Mapped[date] = mapped_column(Date)
    atualizado_em: Mapped[datetime] = mapped_column(DataHoraComFuso())

    @classmethod
    def de_dominio(cls, fatura: Fatura) -> "FaturaModel":
        return cls(
            id=fatura.id,
            cliente_id=fatura.cliente_id,
            identificador_exibivel=fatura.identificador_exibivel,
            competencia=str(fatura.competencia),
            valor=fatura.valor.valor,
            moeda=fatura.valor.moeda,
            status=fatura.status.value,
            vencimento=fatura.vencimento,
            atualizado_em=fatura.atualizado_em,
        )

    def para_dominio(self) -> Fatura:
        return Fatura(
            id=self.id,
            cliente_id=self.cliente_id,
            identificador_exibivel=self.identificador_exibivel,
            competencia=Competencia.de_texto(self.competencia),
            valor=Dinheiro(Decimal(self.valor), self.moeda),
            status=self.status,
            vencimento=self.vencimento,
            atualizado_em=self.atualizado_em,
        )


class PagamentoModel(Base):
    __tablename__ = "pagamentos"

    fatura_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("faturas.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String(20))
    atualizado_em: Mapped[datetime] = mapped_column(DataHoraComFuso())
    forma: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pago_em: Mapped[datetime | None] = mapped_column(DataHoraComFuso(), nullable=True)
    valor: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    moeda: Mapped[str | None] = mapped_column(String(3), nullable=True)

    @classmethod
    def de_dominio(cls, pagamento: Pagamento) -> "PagamentoModel":
        return cls(
            fatura_id=pagamento.fatura_id,
            status=pagamento.status.value,
            atualizado_em=pagamento.atualizado_em,
            forma=pagamento.forma,
            pago_em=pagamento.pago_em,
            valor=pagamento.valor.valor if pagamento.valor else None,
            moeda=pagamento.valor.moeda if pagamento.valor else None,
        )

    def para_dominio(self) -> Pagamento:
        return Pagamento(
            fatura_id=self.fatura_id,
            status=self.status,
            atualizado_em=self.atualizado_em,
            forma=self.forma,
            pago_em=self.pago_em,
            valor=Dinheiro(Decimal(self.valor), self.moeda or "BRL") if self.valor is not None else None,
        )


class RepasseModel(Base):
    __tablename__ = "repasses"

    fatura_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("faturas.id", ondelete="CASCADE"), primary_key=True
    )
    atualizado_em: Mapped[datetime] = mapped_column(DataHoraComFuso())
    etapas: Mapped[list["EtapaRepasseModel"]] = relationship(
        cascade="all, delete-orphan", order_by="EtapaRepasseModel.ordem", lazy="selectin"
    )

    @classmethod
    def de_dominio(cls, repasse: Repasse) -> "RepasseModel":
        return cls(
            fatura_id=repasse.fatura_id,
            atualizado_em=repasse.atualizado_em,
            etapas=[EtapaRepasseModel.de_dominio(repasse.fatura_id, etapa) for etapa in repasse.etapas],
        )

    def para_dominio(self) -> Repasse:
        return Repasse(
            fatura_id=self.fatura_id,
            etapas=tuple(etapa.para_dominio() for etapa in self.etapas),
            atualizado_em=self.atualizado_em,
        )


class EtapaRepasseModel(Base):
    __tablename__ = "etapas_repasse"

    fatura_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("repasses.fatura_id", ondelete="CASCADE"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    ordem: Mapped[int] = mapped_column(Integer)
    nome: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    ocorrido_em: Mapped[datetime | None] = mapped_column(DataHoraComFuso(), nullable=True)
    previsao: Mapped[date | None] = mapped_column(Date, nullable=True)
    mensagem: Mapped[str | None] = mapped_column(String(200), nullable=True)

    @classmethod
    def de_dominio(cls, fatura_id: str, etapa: EtapaRepasse) -> "EtapaRepasseModel":
        return cls(
            fatura_id=fatura_id,
            id=etapa.id,
            ordem=etapa.ordem,
            nome=etapa.nome,
            status=etapa.status.value,
            ocorrido_em=etapa.ocorrido_em,
            previsao=etapa.previsao,
            mensagem=etapa.mensagem,
        )

    def para_dominio(self) -> EtapaRepasse:
        return EtapaRepasse(
            id=self.id,
            ordem=self.ordem,
            nome=self.nome,
            status=self.status,
            ocorrido_em=self.ocorrido_em,
            previsao=self.previsao,
            mensagem=self.mensagem,
        )


class PreferenciaNotificacaoModel(Base):
    __tablename__ = "preferencias_notificacao"

    cliente_id: Mapped[str] = mapped_column(String(40), ForeignKey("clientes.id"), primary_key=True)
    habilitada: Mapped[bool] = mapped_column(Boolean)
    canais: Mapped[str] = mapped_column(String(100))
    atualizada_em: Mapped[datetime] = mapped_column(DataHoraComFuso())

    @classmethod
    def de_dominio(cls, preferencia: PreferenciaNotificacao) -> "PreferenciaNotificacaoModel":
        return cls(
            cliente_id=preferencia.cliente_id,
            habilitada=preferencia.habilitada,
            canais=",".join(preferencia.canais),
            atualizada_em=preferencia.atualizada_em,
        )

    def para_dominio(self) -> PreferenciaNotificacao:
        return PreferenciaNotificacao(
            cliente_id=self.cliente_id,
            habilitada=self.habilitada,
            canais=tuple(canal for canal in self.canais.split(",") if canal),
            atualizada_em=self.atualizada_em,
        )
