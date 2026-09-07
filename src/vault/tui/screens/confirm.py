from typing import ClassVar

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static


class ConfirmScreen(ModalScreen[bool]):
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("s", "confirmar", "Sim"),
        ("n", "cancelar", "Nao"),
        ("escape", "cancelar", "Nao"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(self.message, id="message")
        yield Static(
            "Pressione 's' para confirmar ou 'n' para cancelar.", id="instructions"
        )

    def action_confirmar(self) -> None:
        self.dismiss(True)

    def action_cancelar(self) -> None:
        self.dismiss(False)
