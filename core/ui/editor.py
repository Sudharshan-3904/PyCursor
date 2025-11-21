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

from core.ui.theme import COLORS

class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setMarginsFont(font)

        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)

        editor_bg = QColor(COLORS['editor_bg'])
        self.setPaper(editor_bg)
        lexer.setPaper(editor_bg)

        lexer.setDefaultColor(QColor(COLORS['text_primary']))
        
        lexer.setColor(QColor("#569cd6"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor("#b5cea8"), QsciLexerPython.Number)
        lexer.setColor(QColor("#d4d4d4"), QsciLexerPython.Operator)
        lexer.setColor(QColor("#4ec9b0"), QsciLexerPython.ClassName)
        lexer.setColor(QColor("#dcdcaa"), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor("#dcdcaa"), QsciLexerPython.Decorator)
        lexer.setColor(QColor("#6a9955"), QsciLexerPython.Comment)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.TripleSingleQuotedString)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.TripleDoubleQuotedString)

        self.setLexer(lexer)

        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)

        transparent = QColor(0, 0, 0, 0)
        fg = QColor(COLORS['text_secondary'])
        
        self.setMarginWidth(0, "0000")
        self.setMarginsBackgroundColor(QColor(COLORS['editor_bg']))
        self.setMarginsForegroundColor(fg)

        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(QColor(COLORS['editor_bg']), QColor(COLORS['editor_bg']))

        self.SendScintilla(QsciScintilla.SCI_SETFOLDFLAGS, 0)

        self.setCaretForegroundColor(QColor(COLORS['editor_cursor']))
        self.setCaretWidth(2)
        
        self.setSelectionBackgroundColor(QColor(COLORS['editor_selection']))
        self.setSelectionForegroundColor(QColor(COLORS['text_highlight']))

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeBackground)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor(COLORS['bg_tertiary']))

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
