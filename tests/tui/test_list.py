"""Testes end-to-end da ListScreen (tabela de credenciais + busca ao vivo)."""

import pytest
from textual.widgets import DataTable

from vault.core.master_password import create_vault
from vault.db.credentials import save_credential
from vault.tui.app import VaultApp


@pytest.mark.asyncio
async def test_list_screen_popula_tabela_ao_entrar():
    create_vault("senhateste12345")
    save_credential("servico1", "login1", b"senha1")
    save_credential("servico2", "login2", b"senha2")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        tabela = pilot.app.screen.query_one("#ListaServicos", DataTable)
        assert tabela.row_count == 2


@pytest.mark.asyncio
async def test_list_screen_busca_ao_vivo_filtra_tabela():
    create_vault("senhateste12345")
    save_credential("servico1", "login1", b"senha1")
    save_credential("servico2", "login2", b"senha2")
    save_credential("outro_servico", "login3", b"senha3")
    save_credential("servico1_extra", "login4", b"senha4")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.click("#busca")
        await pilot.press(*"servico1_extra")
        await pilot.pause()
        tabela = pilot.app.screen.query_one("#ListaServicos", DataTable)
        assert tabela.row_count == 1
