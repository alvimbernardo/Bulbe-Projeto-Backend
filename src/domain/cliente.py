"""Cliente corporativo elegivel e confirmacao do primeiro acesso (US05)."""

from dataclasses import dataclass, field
import re
from secrets import compare_digest

from src.domain.erros import DadoInvalido, ErroDeNegocio


def normalizar_email(email: str) -> str:
    """Normalizacao usada tanto pelo cadastro quanto pela busca da conta."""
    normalizado = email.strip().casefold()
    try:
        normalizado.encode("utf-8")
    except UnicodeEncodeError:
        raise DadoInvalido("email", "O email deve conter caracteres UTF-8 validos.") from None
    if len(normalizado) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+", normalizado):
        raise DadoInvalido("email", "Informe um email valido.")
    return normalizado


class ClienteInelegivel(ErroDeNegocio):
    def __init__(self) -> None:
        super().__init__(
            "CLIENTE_INELEGIVEL", "Nao foi possivel confirmar o vinculo com um cliente Bulbe.", 422,
        )


@dataclass
class Cliente:
    id: str
    nome_exibicao: str
    email: str
    status: str
    identificador_cliente: str = field(repr=False)
    codigo_verificacao: str = field(repr=False)

    def __post_init__(self) -> None:
        self.email = normalizar_email(self.email)
        if self.status not in {"ativo", "inativo"}:
            raise DadoInvalido("status", "Status do cliente deve ser ativo ou inativo.")
        if not self.id.strip() or not self.identificador_cliente.strip():
            raise DadoInvalido("identificador_cliente", "O cliente deve possuir identificacao.")
        if not self.codigo_verificacao:
            raise DadoInvalido("codigo_verificacao", "O cliente deve possuir codigo de verificacao.")

    def esta_ativo(self) -> bool:
        return self.status == "ativo"

    def confirmar_vinculo(self, email: str, codigo_verificacao: str | None) -> bool:
        """Politica provisoria da Sprint 2: cliente ativo, email e codigo conferidos.

        O codigo e ficticio nos seeds. Em producao, emissao, validade e entrega
        precisam seguir o processo de primeiro acesso aprovado pela Bulbe.
        """
        codigo = codigo_verificacao or ""
        try:
            codigo_bytes = codigo.encode("utf-8")
        except UnicodeEncodeError:
            raise DadoInvalido("codigo_verificacao", "O codigo deve conter caracteres UTF-8 validos.") from None
        codigo_valido = compare_digest(codigo_bytes, self.codigo_verificacao.encode("utf-8"))
        email_valido = normalizar_email(email) == self.email
        return self.esta_ativo() and email_valido and codigo_valido
