import pytest
from textual.widgets import DataTable, Static

from vault.core.crypto import encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import save_credential
from vault.tui.app import VaultApp
from vault.tui.screens.detail import DetailScreen


@pytest.mark.asyncio
async def test_detail_screen_exibe_detalhes_da_credencial():
    create_vault("senhateste12345")
    key = login("senhateste12345")
    encrypted_password = encrypt_password("senha_teste", key)
    save_credential("servico_teste", "login_teste", encrypted_password)
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        tabela = pilot.app.screen.query_one("#ListaServicos", DataTable)
        tabela.focus()
        await pilot.press("enter")
        await pilot.pause()
        texto = pilot.app.screen.query_one("#static", Static).content
        assert (
            isinstance(pilot.app.screen, DetailScreen)
            and "servico_teste" in texto
            and "login_teste" in texto
            and "senha_teste" in texto
        )
