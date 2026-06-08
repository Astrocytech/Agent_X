"""PyQt5 chat popup window for interactive sessions."""

import json
import sys

import markdown
from pygments.formatters import HtmlFormatter

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextBrowser, QTextEdit, QPushButton,
)
from PyQt5.QtGui import QTextCursor


_PYGMENTS_CSS = HtmlFormatter().get_style_defs(".codehilite")

_CHAT_CSS = f"""
<style>
body {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    padding: 8px;
}}
.session-banner {{
    background-color: #e3f2fd;
    border: 1px solid #90caf9;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 13px;
}}
.user-msg {{
    background-color: #e8f5e9;
    border: 1px solid #a5d6a7;
    padding: 8px 12px;
    margin: 6px 0;
}}
.assistant-msg {{
    background-color: #f5f5f5;
    border: 1px solid #e0e0e0;
    padding: 8px 12px;
    margin: 6px 0;
}}
.tool-result {{
    background-color: #e8f5e9;
    border: 1px solid #a5d6a7;
    padding: 6px 10px;
    margin: 4px 0;
    font-size: 13px;
}}
.tool-error {{
    background-color: #ffebee;
    border: 1px solid #ef9a9a;
    padding: 6px 10px;
    margin: 4px 0;
    font-size: 13px;
}}
code {{
    background-color: #f5f2f0;
    padding: 1px 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
}}
pre {{
    background-color: #f8f8f8;
    border: 1px solid #e0e0e0;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.3;
}}
pre code {{
    background: none;
    padding: 0;
}}
h1, h2, h3 {{ margin: 8px 0 4px 0; }}
p {{ margin: 4px 0; }}
ul, ol {{ margin: 4px 0; padding-left: 20px; }}
{_PYGMENTS_CSS}
</style>
"""


def _md_to_html(text: str) -> str:
    if not text:
        return ""
    return markdown.markdown(text, extensions=["fenced_code", "codehilite"])


def _text_event_to_html(text: str, author: str) -> str:
    md_html = _md_to_html(text)
    if author == "user":
        return f'<div class="user-msg"><b>You:</b><br>{md_html}</div>'
    return f'<div class="assistant-msg">{md_html}</div>'


def _tool_event_to_html(event: dict) -> str | None:
    name = event.get("name", "")
    status = event.get("status", "")
    if status == "running":
        return None
    if status == "completed":
        output = event.get("output", "")
        if output:
            return f'<div class="tool-result">Tool: <b>{name}</b> done<br><pre>{output}</pre></div>'
        return f'<div class="tool-result">Tool: <b>{name}</b> done</div>'
    if status == "error":
        err = event.get("error", "")
        return f'<div class="tool-error">Tool: <b>{name}</b> error: {err}</div>'
    return None


def _page_html(session_id: str, model: str, body: str) -> str:
    banner = (
        f'<div class="session-banner">'
        f"Model: <b>{model}</b> &nbsp;|&nbsp; Session: <b>{session_id or '(new)'}</b>"
        f"</div>"
    )
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'>{_CHAT_CSS}</head><body>{banner}{body}</body></html>"


class _WorkerThread(QThread):
    event_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, provider, messages, parent=None):
        super().__init__(parent)
        self._provider = provider
        self._messages = messages

    def run(self):
        try:
            gen = self._provider.complete_streaming(self._messages)
            while True:
                try:
                    event = next(gen)
                    self.event_signal.emit(event)
                except StopIteration as e:
                    self.finished_signal.emit(e.value if hasattr(e, "value") else None)
                    return
        except Exception as e:
            self.error_signal.emit(str(e))


class _InputTextEdit(QTextEdit):
    send_requested = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.send_requested.emit()
        else:
            super().keyPressEvent(event)


class ChatWindow(QMainWindow):
    def __init__(self, provider, session_id="", model=""):
        super().__init__()
        self._provider = provider
        self._session_id = session_id
        self._model = model
        self._streaming = False
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f"Agent_X Chat \u2014 {self._model}")
        self.setMinimumSize(680, 420)
        self.resize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setReadOnly(True)
        layout.addWidget(self._browser, stretch=1)

        self._browser.setHtml(_page_html(self._session_id, self._model, ""))

        input_row = QHBoxLayout()
        input_row.setSpacing(4)

        self._input = _InputTextEdit()
        self._input.setPlaceholderText("Type a message... (Enter to send, Shift+Enter for newline)")
        self._input.setMaximumHeight(120)
        self._input.setAcceptRichText(False)
        self._input.send_requested.connect(self._on_send)
        input_row.addWidget(self._input, stretch=1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setFixedWidth(80)
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        layout.addLayout(input_row)

    def _scroll_to_bottom(self):
        self._browser.ensureCursorVisible()

    def _append_text(self, text: str):
        cursor = self._browser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(text)
        self._browser.setTextCursor(cursor)
        self._scroll_to_bottom()

    def _on_send(self):
        if self._streaming:
            return
        text = self._input.toPlainText().strip()
        if not text:
            return
        self._input.clear()

        self._append_text(_text_event_to_html(text, "user"))

        self._set_input_enabled(False)

        messages = [{"role": "user", "content": text}]
        self._worker = _WorkerThread(self._provider, messages)
        self._worker.event_signal.connect(self._on_provider_event)
        self._worker.finished_signal.connect(self._on_stream_finished)
        self._worker.error_signal.connect(self._on_stream_error)
        self._worker.start()

    def _on_provider_event(self, event: dict):
        et = event.get("type", "")
        author = event.get("author", "assistant")

        if et == "text":
            if author == "user":
                return
            self._append_text(_text_event_to_html(event.get("text", ""), author))
        elif et == "tool":
            html = _tool_event_to_html(event)
            if html:
                self._append_text(html)

    def _on_stream_finished(self, result):
        self._set_input_enabled(True)

    def _on_stream_error(self, error: str):
        self._append_text(f'<div class="tool-error">Error: {error}</div>')
        self._set_input_enabled(True)

    def _set_input_enabled(self, enabled: bool):
        self._streaming = not enabled
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)
        if enabled:
            self._input.setFocus()


def run_chat_window(provider, session_id="", model="") -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = ChatWindow(provider, session_id, model)
    window.show()
    return app.exec_()
