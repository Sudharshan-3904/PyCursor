from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QPolygon
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtCore import QPoint
import ast

class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont("Consolas", 12)
        self.setFont(font)
        self.setMarginsFont(font)

        background_color = QColor("#1E1E1E")
        fold_arrow_color = QColor("#569CD6")
        line_number_color = QColor("#858585")
        caret_color = QColor("#AEAFAD")
        selection_color = QColor("#264F78")
        current_line_color = QColor("#2A2D2E")

        # Line Numbers
        self.setMarginsBackgroundColor(background_color)
        self.setMarginsForegroundColor(line_number_color)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)

        # Folding margin
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(1, 12)
        self.setMarginSensitivity(1, True)

        # IMPORTANT: Disable built-in folding style to avoid conflicts
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.setFoldMarginColors(background_color, background_color)

        self.markerDeleteAll()

        FOLD_CLOSED_MARKER = 1
        FOLD_OPEN_MARKER = 2

        def create_arrow_pixmap(direction="down", size=12):
            pixmap = QPixmap(size, size)
            pixmap.fill(background_color)
            painter = QPainter(pixmap)
            painter.setPen(fold_arrow_color)
            painter.setBrush(fold_arrow_color)

            if direction == "down":
                points = [(size * 0.2, size * 0.3), (size * 0.8, size * 0.3), (size * 0.5, size * 0.7)]
            else:  # up
                points = [(size * 0.2, size * 0.7), (size * 0.8, size * 0.7), (size * 0.5, size * 0.3)]

            qpoints = QPolygon([QPoint(int(x), int(y)) for x, y in points])
            painter.drawPolygon(qpoints)
            painter.end()
            return pixmap

        # Create pixmaps for fold markers
        closed_pixmap = create_arrow_pixmap("down")
        open_pixmap = create_arrow_pixmap("up")

        # Assign pixmaps to markers via SendScintilla
        self.SendScintilla(QsciScintilla.SCI_MARKERDEFINEPIXMAP, FOLD_CLOSED_MARKER, closed_pixmap)
        self.SendScintilla(QsciScintilla.SCI_MARKERDEFINEPIXMAP, FOLD_OPEN_MARKER, open_pixmap)

        # Set marker background to background color so pixmap is visible
        self.setMarkerBackgroundColor(background_color, FOLD_CLOSED_MARKER)
        self.setMarkerBackgroundColor(background_color, FOLD_OPEN_MARKER)

        # Lexer setup (same as before)...
        self.lexer = QsciLexerPython()
        self.lexer.setDefaultFont(font)
        self.lexer.setColor(QColor("#569CD6"), QsciLexerPython.Keyword)
        self.lexer.setColor(QColor("#CE9178"), QsciLexerPython.DoubleQuotedString)
        self.lexer.setColor(QColor("#CE9178"), QsciLexerPython.SingleQuotedString)
        self.lexer.setColor(QColor("#6A9955"), QsciLexerPython.Comment)
        self.lexer.setColor(QColor("#DCDCAA"), QsciLexerPython.FunctionMethodName)
        self.lexer.setColor(QColor("#B5CEA8"), QsciLexerPython.Number)
        self.setLexer(self.lexer)

        # Caret & Selection
        self.setCaretForegroundColor(caret_color)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(current_line_color)
        self.setSelectionBackgroundColor(selection_color)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # Tabs & Indentation
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)

        # Syntax errors
        self.textChanged.connect(self.highlight_syntax_errors)

    def highlight_syntax_errors(self):
        self.markerDeleteAll()
        try:
            ast.parse(self.text())
        except SyntaxError as e:
            self.markerDefine(QsciScintilla.MarkerSymbol.FullRectangle, 0)
            self.setMarkerBackgroundColor(QColor("#FF5555"), 0)
            self.markerAdd(e.lineno - 1, 0)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        line, index = self.getCursorPosition()
        text = self.text(line)

        if text.rstrip().endswith(":"):
            self.insertAt("    ", line + 1, 0)
            self.setCursorPosition(line + 1, 4)
        else:
            indentation = len(text) - len(text.lstrip())
            self.insertAt(" " * indentation, line + 1, 0)
            self.setCursorPosition(line + 1, indentation)
