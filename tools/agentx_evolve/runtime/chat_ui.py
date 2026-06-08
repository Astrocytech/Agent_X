import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style
from rich.text import Text


_USER_STYLE = Style(color="#ffffff", bgcolor="#2d6a4f")
_AGENT_STYLE = Style(color="#ffffff", bgcolor="#1b4965")


class ChatUI:
    def __init__(self, session_id: str = "", model: str = "", mode: str = "plan"):
        self.console = Console()
        self._session_id = session_id
        self._model = model
        self._mode = mode

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in ("plan", "apply"):
            raise ValueError(f"invalid mode: {mode}")
        self._mode = mode

    def ask(self, prompt: str = "chat> ") -> str:
        return self.console.input(prompt)

    def add_event(self, event: dict) -> None:
        et = event.get("type", "")
        author = event.get("author", "assistant")

        if et == "text":
            if author == "user":
                self.console.print(
                    Panel(
                        Markdown(event["text"], code_theme="monokai"),
                        title=Text(" You ", style=_USER_STYLE),
                        border_style="green",
                        subtitle=Text(" USER ", style=_USER_STYLE),
                    )
                )
            else:
                self.console.print(
                    Panel(
                        Markdown(event["text"], code_theme="monokai"),
                        title=Text(" Agent ", style=_AGENT_STYLE),
                        border_style="blue",
                        subtitle=Text(" ASSISTANT ", style=_AGENT_STYLE),
                    )
                )
        elif et == "reasoning":
            self.console.print(f"[dim]  [{event['text']}][/dim]")
        elif et == "agent":
            self.console.print(f"[dim]  [Agent: {event['agent']}][/dim]")
        elif et == "tool":
            name = event.get("name", "")
            status = event.get("status", "")
            if status == "running":
                inp = json.dumps(event.get("input", {}))
                self.console.print(f"[dim]  [Tool: {name}] {inp}[/dim]")
            elif status == "completed":
                output = event.get("output", "")
                if output:
                    self.console.print(f"[dim]  [Tool: {name} done] {output[:200]}[/dim]")
                else:
                    self.console.print(f"[dim]  [Tool: {name} done][/dim]")
            elif status == "error":
                self.console.print(f"[bold red]  [Tool: {name} error] {event.get('error', '')}[/bold red]")
