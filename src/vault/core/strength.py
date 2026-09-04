from zxcvbn import zxcvbn


def check_password_strength(password: str) -> tuple[int, str]:
    """Avalia a forca de uma senha usando o zxcvbn.

    Devolve (score, warning): score vai de 0 (pessima) a 4 (otima); warning
    e uma string vazia quando o zxcvbn nao tem nenhum aviso especifico.
    """
    result = zxcvbn(password)
    score, warning = result["score"], result["feedback"]["warning"]
    return (score, warning)
