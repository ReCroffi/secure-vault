import secrets
import string


def generate_password(
    length: int,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Gera uma senha aleatoria usando o CSPRNG do sistema (`secrets`), nunca `random`.

    Cada flag liga/desliga um conjunto de caracteres na pool de sorteio.
    Levanta ValueError se todas vierem False (pool ficaria vazia).
    """
    components = [
        (string.ascii_uppercase, use_uppercase),
        (string.ascii_lowercase, use_lowercase),
        (string.digits, use_digits),
        (string.punctuation, use_symbols),
    ]
    pool = "".join(character for character, flag in components if flag)
    if not pool:
        raise ValueError("Ative pelo menos uma opção")

    generated_password = "".join([secrets.choice(pool) for i in range(length)])

    return generated_password
