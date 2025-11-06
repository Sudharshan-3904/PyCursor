from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QPolygon
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP
from PyQt6.QtCore import QPoint
import ast

class LanguageConfig:
    """Holds editor customization per language."""
    def __init__(self, lexer_class, font=None, colors=None, indent=4, use_tabs=False):
        self.lexer_class = lexer_class
        self.font = font or QFont("Consolas", 12)
        self.colors = colors or {}
        self.indent = indent
        self.use_tabs = use_tabs

# Language configs
LANGUAGE_CONFIGS = {
    "python": LanguageConfig(
        QsciLexerPython,
        colors={
            "keyword": "#569CD6",
            "string": "#CE9178",
            "comment": "#6A9955",
            "function": "#DCDCAA",
            "number": "#B5CEA8",
        }
    ),
    "cpp": LanguageConfig(
        QsciLexerCPP,
        colors={
            "keyword": "#569CD6",
            "string": "#CE9178",
            "comment": "#6A9955",
            "preprocessor": "#D4D4D4",
            "number": "#B5CEA8",
        },
        indent=4,
        use_tabs=True
    )
}

class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # General colors
        self.background_color = QColor("#1E1E1E")
        self.line_number_color = QColor("#858585")
        self.caret_color = QColor("#AEAFAD")
        self.selection_color = QColor("#264F78")
        self.current_line_color = QColor("#2A2D2E")
        self.fold_arrow_color = QColor("#569CD6")

        self.indentation_chars = (":", "{", "[", "(")

        self.setup_ui()
        self.setup_fold_markers()
        self.apply_language_config("python")

        # Syntax error checking
        self.textChanged.connect(self.highlight_syntax_errors)

    def setup_ui(self):
        font = QFont("Consolas", 12)
        self.setFont(font)
        self.setMarginsFont(font)

        # Line numbers
        self.setMarginsBackgroundColor(self.background_color)
        self.setMarginsForegroundColor(self.line_number_color)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)

        # Folding margin
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(1, 12)
        self.setMarginSensitivity(1, True)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.setFoldMarginColors(self.background_color, self.background_color)

        # Caret & selection
        self.setCaretForegroundColor(self.caret_color)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(self.current_line_color)
        self.setSelectionBackgroundColor(self.selection_color)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # Tabs & indentation
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)

    def setup_fold_markers(self):
        """Custom fold arrows."""
        FOLD_CLOSED_MARKER = 1
        FOLD_OPEN_MARKER = 2

        def create_arrow_pixmap(direction="down", size=12):
            pixmap = QPixmap(size, size)
            pixmap.fill(self.background_color)
            painter = QPainter(pixmap)
            painter.setPen(self.fold_arrow_color)
            painter.setBrush(self.fold_arrow_color)
            if direction == "down":
                points = [(size*0.2,size*0.3),(size*0.8,size*0.3),(size*0.5,size*0.7)]
            else:
                points = [(size*0.2,size*0.7),(size*0.8,size*0.7),(size*0.5,size*0.3)]
            qpoints = QPolygon([QPoint(int(x),int(y)) for x,y in points])
            painter.drawPolygon(qpoints)
            painter.end()
            return pixmap

        closed_pixmap = create_arrow_pixmap("down")
        open_pixmap = create_arrow_pixmap("up")
        self.SendScintilla(QsciScintilla.SCI_MARKERDEFINEPIXMAP, FOLD_CLOSED_MARKER, closed_pixmap)
        self.SendScintilla(QsciScintilla.SCI_MARKERDEFINEPIXMAP, FOLD_OPEN_MARKER, open_pixmap)
        self.setMarkerBackgroundColor(self.background_color, FOLD_CLOSED_MARKER)
        self.setMarkerBackgroundColor(self.background_color, FOLD_OPEN_MARKER)

    def apply_language_config(self, language_name):
        config = LANGUAGE_CONFIGS.get(language_name.lower(), LANGUAGE_CONFIGS["python"])
        lexer = config.lexer_class()
        lexer.setDefaultFont(config.font)
        lexer.setFoldComments(True)
        lexer.setFoldCompact(True)

        # Map colors
        color_map = {}
        if isinstance(lexer, QsciLexerPython):
            color_map = {
                "keyword": QsciLexerPython.Keyword,
                "string": QsciLexerPython.DoubleQuotedString,
                "comment": QsciLexerPython.Comment,
                "function": QsciLexerPython.FunctionMethodName,
                "number": QsciLexerPython.Number
            }
        elif isinstance(lexer, QsciLexerCPP):
            color_map = {
                "keyword": QsciLexerCPP.Keyword,
                "string": QsciLexerCPP.DoubleQuotedString,
                "comment": QsciLexerCPP.Comment,
                "preprocessor": QsciLexerCPP.Preprocessor,
                "number": QsciLexerCPP.Number
            }

        for key, color in config.colors.items():
            style = color_map.get(key.lower())
            if style is not None:
                lexer.setColor(QColor(color), style)

        self.setLexer(lexer)

        # Indentation
        self.setIndentationWidth(config.indent)
        self.setTabWidth(config.indent)
        self.setIndentationsUseTabs(config.use_tabs)
        self.lexer = lexer

    def highlight_syntax_errors(self):
        self.markerDeleteAll()
        try:
            ast.parse(self.text())
        except SyntaxError as e:
            self.markerDefine(QsciScintilla.MarkerSymbol.FullRectangle, 0)
            self.setMarkerBackgroundColor(QColor("#FF5555"), 0)
            self.markerAdd(e.lineno - 1, 0)

    def keyPressEvent(self, event):
        if event.key() in (0x01000004, 0x01000005):  # Qt.Key_Return, Qt.Key_Enter
            line, index = self.getCursorPosition()
            prev_text = self.text(line) if line >= 0 else ""
            stripped_prev = prev_text.rstrip()
            base_indent = len(prev_text) - len(prev_text.lstrip())

            # Decide extra indentation
            extra_indent = self.indentationWidth() if stripped_prev.endswith(self.indentation_chars) else 0
            desired_indent = base_indent + extra_indent

            # Insert newline with correct indentation
            self.insert("\n" + " " * desired_indent)
            self.setCursorPosition(line + 1, desired_indent)
        else:
            super().keyPressEvent(event)

