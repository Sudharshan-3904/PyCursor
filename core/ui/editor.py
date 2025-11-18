from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setMarginsFont(font)

        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)

        editor_bg = QColor("#1e1e1e")
        self.setPaper(editor_bg)
        lexer.setPaper(editor_bg)

        lexer.setDefaultColor(QColor("#ffffff"))

        lexer.setColor(QColor("#ffd700"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#98c379"), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor("#98c379"), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor("#d19a66"), QsciLexerPython.Number)
        lexer.setColor(QColor("#c678dd"), QsciLexerPython.Operator)
        lexer.setColor(QColor("#61afef"), QsciLexerPython.ClassName)
        lexer.setColor(QColor("#56b6c2"), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor("#e06c75"), QsciLexerPython.Decorator)
        lexer.setColor(QColor("#5c6370"), QsciLexerPython.Comment)

        self.setLexer(lexer)

        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)

        transparent = QColor(0, 0, 0, 0)
        fg = QColor("#bbbbbb")

        self.setMarginWidth(0, "0000")
        self.setMarginsBackgroundColor(transparent)
        self.setMarginsForegroundColor(fg)

        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(transparent, transparent)

        self.SendScintilla(QsciScintilla.SCI_SETFOLDFLAGS, 0)

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeBackground)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor("#333333"))

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
