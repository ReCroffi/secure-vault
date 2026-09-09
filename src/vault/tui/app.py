"""App Textual do vault (`secure-vault tui`). Ponto de entrada da interface
interativa - o resto das telas vive em `vault.tui.screens`."""

from textual.app import App

from vault.tui.screens.login import LoginScreen


class VaultApp(App):
    # Chave de cifragem guardada em memoria durante a sessao (`self.app.key`
    # nas telas), definida por LoginScreen apos a senha mestra ser conferida.
    # Nunca vai pro disco.
    key: bytes | None

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())
