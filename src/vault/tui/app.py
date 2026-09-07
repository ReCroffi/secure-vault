from textual.app import App

from vault.tui.screens.login import LoginScreen


class VaultApp(App):
    key: bytes | None

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())
