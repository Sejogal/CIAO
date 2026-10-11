import re
import unicodedata


def slugify(value: str) -> str:
    """
    Converte um texto em um slug.

    Exemplo:
    Angola Telecom -> angola-telecom
    Empresa de Telecomunicações -> empresa-de-telecomunicacoes
    """

    value = value.strip().lower()

    # Remove acentos
    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    # Substitui caracteres não alfanuméricos por "-"
    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    # Remove "-" do início e fim
    value = value.strip("-")

    return value