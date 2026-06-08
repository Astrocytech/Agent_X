import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


class ChatUI:
    def __init__(self, session_id: str = "", model: str = "", mode: str = "plan"):
        self.console = Console()
        self._session_id = session_id
        self._model = model
        self._mode = mode
        self._banner_printed = False

    def _print_banner(self) -> None:
        self.print_banner()

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in ("plan", "apply"):
            raise ValueError(f"invalid mode: {mode}")
        self._mode = mode

    def print_banner(self) -> None:
        if self._banner_printed:
            return
        self._banner_printed = True
        self.console.print(
            Panel(
                f"Model: {self._model}\nSession: {self._session_id}\nMode: {self._mode}",
                title="Session",
                border_style="bright_blue",
            )
        )

    def ask(self, prompt: str = "chat> ") -> str:
        return self.console.input(prompt)

    def add_event(self, event: dict) -> None:
        self._print_banner()
        et = event.get("type", "")
        author = event.get("author", "assistant")

        if et == "agent":
            self.console.print(
                Panel(
                    Text(event["agent"], style="bold blue"),
                    title="Agent",
                    border_style="blue",
                )
            )
        elif et == "reasoning":
            self.console.print(
                Panel(
                    Text(event["text"], style="dim italic"),
                    title="Thinking",
                    border_style="bright_black",
                )
            )
        elif et == "text":
            if author == "user":
                self.console.print(
                    Panel(
                        Markdown(event["text"]),
                        title="You",
                        border_style="green",
                    )
                )
            else:
                self.console.print(
                    Markdown(event["text"], code_theme="monokai")
                )
        elif et == "tool":
            name = event.get("name", "")
            status = event.get("status", "")
            if status == "running":
                inp = json.dumps(event.get("input", {}))
                self.console.print(
                    Panel(
                        f"[bold]{name}[/bold]\n{inp}",
                        title="Tool",
                        border_style="yellow",
                    )
                )
            elif status == "completed":
                output = event.get("output", "")
                if output:
                    self.console.print(
                        Panel(
                            f"[bold]{name}[/bold] done\n{output}",
                            title="Tool Result",
                            border_style="green",
                        )
                    )
                else:
                    self.console.print(
                        Panel(
                            f"[bold]{name}[/bold] done",
                            title="Tool Result",
                            border_style="green",
                        )
                    )
            elif status == "error":
                self.console.print(
                    Text(
                        f"\u2717 {name} failed: {event.get('error', '')}",
                        style="bold red",
                    )
                )
