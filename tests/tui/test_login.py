import pytest

from vault.core.master_password import create_vault
from vault.tui.app import VaultApp
from vault.tui.screens.list import ListScreen


@pytest.mark.asyncio
async def test_login_screen_senha_correta_avanca_para_lista():
    create_vault("senhateste12345")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhateste12345")
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.key is not None and isinstance(pilot.app.screen, ListScreen)


@pytest.mark.asyncio
async def test_login_screen_senha_incorreta_nao_avanca():
    create_vault("senhateste12345")
    app = VaultApp()
    async with app.run_test() as pilot:
        await pilot.press(*"senhaincorreta")
        await pilot.press("enter")
        await pilot.pause()
        assert (
            not isinstance(pilot.app.screen, ListScreen)
            and getattr(pilot.app, "key", None) is None
        )
