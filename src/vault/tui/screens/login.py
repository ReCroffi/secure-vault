from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input

from vault.core.master_password import login


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Senha mestra", password=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            key = login(event.value)
            self.app.key = key
            self.app.switch_screen(Screen())
        except ValueError as e:
            print(e)
