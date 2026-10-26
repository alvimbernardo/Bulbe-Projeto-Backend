"""Destino externo configurado e aprovado, sem redirecionamento aberto (US14)."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from src.domain.erros import DadoInvalido


@dataclass(frozen=True)
class DestinoHistorico:
    url: str

    def validar(self, hosts_aprovados: frozenset[str]) -> str:
        try:
            partes = urlsplit(self.url)
            porta = partes.port
        except ValueError:
            raise DadoInvalido("destino", "Destino de historico invalido.") from None
        if (
            any(ord(caractere) <= 32 or ord(caractere) == 127 for caractere in self.url)
            or "\\" in self.url
            or partes.scheme != "https"
            or not partes.hostname
            or partes.hostname.casefold() not in hosts_aprovados
            or partes.username is not None
            or partes.password is not None
            or partes.fragment
            or porta not in (None, 443)
        ):
            raise DadoInvalido("destino", "O historico deve usar HTTPS em um host aprovado.")
        return self.url
