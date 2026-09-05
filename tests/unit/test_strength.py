from vault.core.generator import generate_password
from vault.core.strength import check_password_strength


def test_check_password_strength_senha_fraca():
    test_password = "1234567"
    score, warning = check_password_strength(test_password)
    assert score < 3 and warning != ""


def test_check_password_strength_senha_forte():
    test_password = generate_password(20)
    score, _ = check_password_strength(test_password)
    assert score >= 3
