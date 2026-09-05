import pytest

from vault.core.generator import generate_password


def test_generate_password_respeita_tamanho():
    result = generate_password(20)
    assert len(result) == 20


def test_generate_password_so_digitos():
    result = generate_password(
        length=16,
        use_uppercase=False,
        use_lowercase=False,
        use_digits=True,
        use_symbols=False,
    )
    assert result.isdigit()


def test_generate_password_sem_opcoes_levanta_erro():

    with pytest.raises(ValueError, match="Ative pelo menos uma opção"):
        generate_password(
            length=16,
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_symbols=False,
        )
