"""Teste end-to-end de apagar credencial pela DetailScreen (tecla 'd' + 's'
pra confirmar no ConfirmScreen)."""

import pytest
from textual.widgets import DataTable

from vault.core.crypto import encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import (
    get_all_credentials,
    get_credential_by_id,
    save_credential,
)
from vault.tui.app import VaultApp
from vault.tui.screens.list import ListScreen


@pytest.mark.asyncio
async def test_delete_credencial_existente():
    create_vault("senhateste12345")
    key = login("senhateste12345")
    encrypted_password = encrypt_password("senha_teste", key)
    save_credential("servico_teste", "login_teste", encrypted_password)
    credential_id = get_all_credentials()[0].id
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        tabela = pilot.app.screen.query_one("#ListaServicos", DataTable)
        tabela.focus()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("s")
        await pilot.pause()
        assert get_credential_by_id(credential_id) is None and isinstance(
            pilot.app.screen, ListScreen
        )
