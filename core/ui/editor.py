from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QColor, QFont, QAction
from PyQt6.QtCore import pyqtSignal
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from core.ui.theme import COLORS, LIGHT_COLORS

class CodeEditor(QsciScintilla):
    git_blame_requested = pyqtSignal(str)
    git_history_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_lexer()
        self.apply_theme_colors()

        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)

        self.setMarginWidth(0, "0000")

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self._modified = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        self._modified = True

    def isModified(self):
        return self._modified

    def setModified(self, value: bool):
        self._modified = value

    def append_text(self, text: str):
        text = text.replace("\r\n", "\n")
        existing_text = self.text()
        if existing_text and not existing_text.endswith("\n"):
            self.setText(existing_text + "\n" + text)
        else:
            self.setText(existing_text + text)
            
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        
        blame_action = QAction("Git Blame", self)
        blame_action.triggered.connect(self.request_blame)
        menu.addAction(blame_action)
        
        history_action = QAction("Git History", self)
        history_action.triggered.connect(self.request_history)
        menu.addAction(history_action)
        
        menu.exec(event.globalPos())
        
    def request_blame(self):
        if hasattr(self, 'file_path') and self.file_path:
            self.git_blame_requested.emit(self.file_path)
            
    def request_history(self):
        if hasattr(self, 'file_path') and self.file_path:
            self.git_history_requested.emit(self.file_path)

    def setup_lexer(self):
        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setMarginsFont(font)
        
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        # Standard colors that look okay on both
        lexer.setColor(QColor("#569cd6"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor("#699856"), QsciLexerPython.Comment)
        self.setLexer(lexer)

    def apply_theme_colors(self, theme='dark'):
        theme_colors = COLORS if theme == 'dark' else LIGHT_COLORS
        bg = QColor(theme_colors['editor_bg'])
        fg = QColor(theme_colors['text_primary'])
        
        self.setPaper(bg)
        if self.lexer():
            self.lexer().setPaper(bg)
            self.lexer().setDefaultColor(fg)
            # Adjust syntax colors for light mode if needed
            if theme == 'light':
                self.lexer().setColor(QColor("#0000ff"), QsciLexerPython.Keyword)
                self.lexer().setColor(QColor("#a31515"), QsciLexerPython.SingleQuotedString)
                self.lexer().setColor(QColor("#008000"), QsciLexerPython.Comment)
            else:
                self.lexer().setColor(QColor("#569cd6"), QsciLexerPython.Keyword)
                self.lexer().setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)
                self.lexer().setColor(QColor("#6a9955"), QsciLexerPython.Comment)

        self.setMarginsBackgroundColor(bg)
        self.setMarginsForegroundColor(QColor(theme_colors['text_secondary']))
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(bg, bg)
        
        self.setCaretForegroundColor(QColor(theme_colors['editor_cursor']))
        self.setSelectionBackgroundColor(QColor(theme_colors['editor_selection']))
        self.setSelectionForegroundColor(QColor(theme_colors['text_highlight']))
        self.setEdgeColor(QColor(theme_colors['bg_tertiary']))

    def refresh_theme(self, theme_name):
        self.apply_theme_colors(theme_name)
