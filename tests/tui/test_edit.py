"""Testes end-to-end da EditScreen: troca de senha e botao gerador."""

import pytest
from textual.widgets import DataTable, Static

from vault.core.crypto import encrypt_password
from vault.core.master_password import create_vault, login
from vault.db.credentials import save_credential
from vault.tui.app import VaultApp
from vault.tui.screens.detail import DetailScreen


@pytest.mark.asyncio
async def test_edit_edita_credencial_existente():
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
        await pilot.press("e")
        await pilot.pause()
        await pilot.press(*"senha_nova_forte123")
        await pilot.press("enter")
        await pilot.pause()
        assert (
            isinstance(pilot.app.screen, DetailScreen)
            and "senha_nova_forte123"
            in pilot.app.screen.query_one("#static", Static).content
        )


@pytest.mark.asyncio
async def test_edit_gerador_copia_e_preenche_automaticamente():
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
        await pilot.press("e")
        await pilot.pause()
        await pilot.click("#password")
        await pilot.pause()
        await pilot.click("#gerador")
        await pilot.pause()
        valor_gerado = pilot.app.screen.query_one("#password").value
        assert len(valor_gerado) == 16
        assert pilot.app._clipboard == valor_gerado
