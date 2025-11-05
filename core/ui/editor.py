from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QColor, QPainter, QTextFormat, QFont
from PyQt6.QtCore import QRect, Qt, QPoint
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat
import re
import ast

# ---------- Line Number Area ---------- #
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_width(), 0

    def paintEvent(self, event):
        self.editor.line_number_area_paint(event)


# ---------- Code Editor with Highlighting and Folding ---------- #
# class CodeEditor(QPlainTextEdit):
#     def __init__(self):
#         super().__init__()

#         # --- Font & Theme ---
#         self.setFont(QFont("Consolas", 12))
#         self.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; border: none;")

#         # --- Line numbers & folding ---
#         self.line_number_area = LineNumberArea(self)
#         self.blockCountChanged.connect(self.update_line_number_area_width)
#         self.updateRequest.connect(self.update_line_number_area)
#         self.cursorPositionChanged.connect(self.highlight_current_line)
#         self.update_line_number_area_width(0)

#         # --- Folding state ---
#         self.folded_blocks = {}  # key: starting block number, value: last folded block number

#         # --- Syntax highlighting ---
#         self.highlighter = PythonHighlighter(self.document())

#     # ---------- Line Number Area ----------
#     def line_number_area_width(self):
#         digits = len(str(max(1, self.blockCount())))
#         return 20 + self.fontMetrics().horizontalAdvance("9") * digits

#     def update_line_number_area_width(self, _):
#         self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

#     def update_line_number_area(self, rect, dy):
#         if dy:
#             self.line_number_area.scroll(0, dy)
#         else:
#             self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
#         if rect.contains(self.viewport().rect()):
#             self.update_line_number_area_width(0)

#     def resizeEvent(self, event):
#         super().resizeEvent(event)
#         cr = self.contentsRect()
#         self.line_number_area.setGeometry(
#             QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
#         )

#     def line_number_area_paint(self, event):
#         painter = QPainter(self.line_number_area)
#         painter.fillRect(event.rect(), QColor("#252526"))

#         block = self.firstVisibleBlock()
#         block_number = block.blockNumber()
#         top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
#         bottom = top + int(self.blockBoundingRect(block).height())

#         foldable_blocks = self.get_foldable_blocks()

#         while block.isValid() and top <= event.rect().bottom():
#             if block.isVisible() and bottom >= event.rect().top():
#                 # Line numbers
#                 painter.setPen(QColor("#858585"))
#                 painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
#                                  Qt.AlignmentFlag.AlignRight, str(block_number + 1))

#                 # Fold markers
#                 if block_number in foldable_blocks:
#                     marker_rect = QRect(0, top, 12, self.fontMetrics().height())
#                     is_folded = self.folded_blocks.get(block_number) is not None
#                     painter.setPen(Qt.GlobalColor.gray)
#                     painter.drawText(marker_rect, Qt.AlignmentFlag.AlignCenter, "-" if not is_folded else "+")
#             block = block.next()
#             top = bottom
#             bottom = top + int(self.blockBoundingRect(block).height())
#             block_number += 1

#     def highlight_current_line(self):
#         extra_selections = []
#         if not self.isReadOnly():
#             selection = QTextEdit.ExtraSelection()
#             line_color = QColor("#333333")
#             selection.format.setBackground(line_color)
#             selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
#             selection.cursor = self.textCursor()
#             selection.cursor.clearSelection()
#             extra_selections.append(selection)
#         self.setExtraSelections(extra_selections)

#     # ---------- Folding Logic ----------
#     def get_foldable_blocks(self):
#         foldable = []
#         block = self.document().firstBlock()
#         while block.isValid():
#             text = block.text().strip()
#             if text.startswith("def ") or text.startswith("class "):
#                 foldable.append(block.blockNumber())
#             block = block.next()
#         return foldable

#     def get_fold_range(self, start_block):
#         start_indent = len(start_block.text()) - len(start_block.text().lstrip())
#         end_block = start_block.next()
#         while end_block.isValid():
#             line_indent = len(end_block.text()) - len(end_block.text().lstrip())
#             if line_indent <= start_indent and end_block.text().strip() != "":
#                 break
#             end_block = end_block.next()
#         return end_block.previous() if end_block.isValid() else self.document().lastBlock()

#     def toggle_fold(self, block_number):
#         block = self.document().findBlockByNumber(block_number)
#         end_block = self.get_fold_range(block)
#         first_inside = block.next()
#         if not first_inside.isValid():
#             return

#         # Determine current folded state
#         folded = first_inside.isVisible()

#         # Toggle visibility of all inside blocks
#         current = first_inside
#         while current.isValid() and current.blockNumber() <= end_block.blockNumber():
#             current.setVisible(not folded)
#             current = current.next()

#         # Update folded_blocks dictionary
#         self.folded_blocks[block_number] = end_block.blockNumber() if not folded else None
#         self.viewport().update()

#     def blockAtMarker(self, y):
#         block = self.document().firstBlock()
#         offset = self.contentOffset().y()
#         while block.isValid():
#             rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
#             marker_rect = QRect(0, rect.top(), 12, self.fontMetrics().height())
#             if marker_rect.top() <= y <= marker_rect.bottom():
#                 return block.blockNumber()
#             block = block.next()
#         return None

#     def mousePressEvent(self, event):
#         x = int(event.position().x())
#         y = int(event.position().y())
#         if x <= 12:  # Marker area width
#             block_number = self.blockAtMarker(y)
#             if block_number in self.get_foldable_blocks():
#                 self.toggle_fold(block_number)
#                 return
#         super().mousePressEvent(event)

#     # ---------- Auto-indent & Syntax Highlighting ----------
#     def keyPressEvent(self, event):
#         cursor = self.textCursor()
#         if event.key() == Qt.Key.Key_Return:
#             cursor.movePosition(cursor.MoveOperation.StartOfBlock)
#             text = cursor.block().text()
#             indentation = len(text) - len(text.lstrip())
#             super().keyPressEvent(event)
#             if re.match(r".*:\s*(#.*)?$", text):
#                 self.insertPlainText(" " * (indentation + 4))
#             else:
#                 self.insertPlainText(" " * indentation)
#         else:
#             super().keyPressEvent(event)

#     def highlight_syntax_errors(self):
#         text = self.toPlainText()
#         extra_selections = []
#         try:
#             ast.parse(text)
#         except SyntaxError as e:
#             cursor = self.textCursor()
#             cursor.setPosition(self.document().findBlockByLineNumber(e.lineno - 1).position())
#             cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
#             selection = QTextEdit.ExtraSelection()
#             selection.format.setUnderlineColor(Qt.GlobalColor.red)
#             selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
#             selection.cursor = cursor
#             extra_selections.append(selection)
#         self.setExtraSelections(self.extraSelections() + extra_selections)


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Font & Theme ---
        font = QFont("Consolas", 12)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setMarginsBackgroundColor(QColor("#252526"))
        self.setMarginsForegroundColor(QColor("#858585"))

        # --- Line Numbers ---
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)

        # --- Folding ---
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(1, 12)
        self.setMarginSensitivity(1, True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedFoldStyle)
        self.setFoldMarginColors(QColor("#252526"), QColor("#252526"))

        # --- Lexer & Syntax Highlighting ---
        self.lexer = QsciLexerPython()
        self.lexer.setDefaultFont(font)
        self.setLexer(self.lexer)

        # --- Caret & Selection ---
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#333333"))
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)

        # --- Tabs & Indentation ---
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)

        # --- Syntax error highlights (optional) ---
        self.textChanged.connect(self.highlight_syntax_errors)

    def highlight_syntax_errors(self):
        """
        Highlights lines with syntax errors using red underlines.
        """
        # Clear previous markers
        self.markerDeleteAll()

        try:
            ast.parse(self.text())
        except SyntaxError as e:
            # Use marker 0 for error highlight
            self.markerDefine(QsciScintilla.MarkerSymbol.FullRectangle, 0)
            self.setMarkerBackgroundColor(QColor("#FF5555"), 0)
            self.markerAdd(e.lineno - 1, 0)

    def keyPressEvent(self, event):
        """
        Handles auto-indentation after pressing Enter.
        """
        super().keyPressEvent(event)

        cursor_pos = self.getCursorPosition()
        line, index = cursor_pos
        text = self.text(line)

        # Auto-indent after colon
        if text.rstrip().endswith(":"):
            self.insertAt("    ", line + 1, 0)
            self.setCursorPosition(line + 1, 4)
        else:
            # Copy previous line's indentation
            indentation = len(text) - len(text.lstrip())
            self.insertAt(" " * indentation, line + 1, 0)
            self.setCursorPosition(line + 1, indentation)



# ---------- Python Syntax Highlighter ----------
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = self._format(QColor("#569CD6"), "bold")
        self.string_format = self._format(QColor("#CE9178"))
        self.comment_format = self._format(QColor("#6A9955"))
        self.number_format = self._format(QColor("#B5CEA8"))
        self.function_format = self._format(QColor("#DCDCAA"))

        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def", "del", "elif",
            "else", "except", "False", "finally", "for", "from", "global", "if",
            "import", "in", "is", "lambda", "None", "nonlocal", "not", "or", "pass",
            "raise", "return", "True", "try", "while", "with", "yield"
        ]
        self.rules = [(r"\b" + kw + r"\b", self.keyword_format) for kw in keywords]
        self.rules += [
            (r"#[^\n]*", self.comment_format),
            (r"\".*?\"|'.*?'", self.string_format),
            (r"\b[0-9]+\b", self.number_format),
            (r"\b[A-Za-z_][A-Za-z0-9_]*(?=\()", self.function_format)
        ]

    def _format(self, color: QColor, style: str = ""):
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        if "bold" in style:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
