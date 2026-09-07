import pytest

from vault.core.master_password import create_vault
from vault.db.credentials import get_all_credentials
from vault.tui.app import VaultApp
from vault.tui.screens.list import ListScreen


@pytest.mark.asyncio
async def test_add_nova_credencial():
    create_vault("senhateste12345")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.click("#service_name")
        await pilot.press(*"servico_teste")
        await pilot.click("#login")
        await pilot.press(*"login_teste")
        await pilot.click("#password")
        await pilot.press(*"senha_teste")
        await pilot.press("enter")
        await pilot.pause()
        assert (
            isinstance(pilot.app.screen, ListScreen) and len(get_all_credentials()) == 1
        )


@pytest.mark.asyncio
async def test_add_gerador_copia_e_preenche_automaticamente():
    create_vault("senhateste12345")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.click("#password")
        await pilot.pause()
        await pilot.click("#gerador")
        await pilot.pause()
        valor_gerado = pilot.app.screen.query_one("#password").value
        assert len(valor_gerado) == 16
        assert pilot.app._clipboard == valor_gerado
