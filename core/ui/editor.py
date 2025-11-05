from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QColor, QPainter, QTextFormat, QFont
from PyQt6.QtCore import QRect, Qt, QPoint
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat
import re
import ast


# ---------- Line Number Area ---------- #
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return self.editor.line_number_area_size()

    def paintEvent(self, event):
        self.editor.line_number_area_paint(event)


# ---------- Code Editor with Highlighting ---------- #
class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        # --- Font & Theme ---
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; border: none;")

        # --- Line numbers ---
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # --- Syntax highlighting ---
        self.highlighter = PythonHighlighter(self.document())

    # --- Line Number Area Logic --- #
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 15 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        """Highlight the line where the cursor is."""
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#333333")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
    
    def mousePressEvent(self, event):
        # Convert position to integers
        x = int(event.position().x())
        y = int(event.position().y())

        # Check if click is on line number area
        if x < self.line_number_area_width():
            block = self.firstVisibleBlock()
            while block.isValid():
                rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
                if rect.contains(QPoint(x, y)):
                    # Toggle fold (example logic)
                    block.setVisible(not block.isVisible())
                    break
                block = block.next()
        super().mousePressEvent(event)


    def highlight_matching_brackets(self):
        cursor = self.textCursor()
        doc = self.document()
        pos = cursor.position()
        brackets = {"(":")", "[":"]", "{":"}"}
        match_pos = None

        char = doc.characterAt(pos - 1)
        if char in brackets:
            match_pos = self.find_matching_bracket(pos - 1, char, brackets[char])
        elif char in brackets.values():
            # Reverse search
            rev_brackets = {v:k for k,v in brackets.items()}
            match_pos = self.find_matching_bracket(pos - 1, rev_brackets[char], char, reverse=True)

        if match_pos is not None:
            extra = QTextEdit.ExtraSelection()
            extra.format.setBackground(QColor("#264F78"))
            for p in (pos - 1, match_pos):
                c = self.textCursor()
                c.setPosition(p)
                c.movePosition(c.MoveOperation.NextCharacter, c.MoveMode.KeepAnchor)
                extra.cursor = c
                self.setExtraSelections(self.extraSelections() + [extra])

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        if event.key() == Qt.Key.Key_Return:
            cursor.movePosition(cursor.MoveOperation.StartOfBlock)
            text = cursor.block().text()
            indentation = len(text) - len(text.lstrip())
            super().keyPressEvent(event)

            # Auto-indent for blocks
            if re.match(r".*:\s*(#.*)?$", text):  # Line ends with ':'
                self.insertPlainText(" " * (indentation + 4))
            else:
                self.insertPlainText(" " * indentation)
        else:
            super().keyPressEvent(event)

    def highlight_syntax_errors(self):
        text = self.toPlainText()
        extra_selections = []
        try:
            ast.parse(text)
        except SyntaxError as e:
            cursor = self.textCursor()
            cursor.setPosition(self.document().findBlockByLineNumber(e.lineno-1).position())
            cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
            selection = QTextEdit.ExtraSelection()
            selection.format.setUnderlineColor(Qt.GlobalColor.red)
            selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
            selection.cursor = cursor
            extra_selections.append(selection)
        self.setExtraSelections(self.extraSelections() + extra_selections)


# ---------- Syntax Highlighter for Python ---------- #
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # Define text formats
        self.keyword_format = self._format(QColor("#569CD6"), "bold")
        self.string_format = self._format(QColor("#CE9178"))
        self.comment_format = self._format(QColor("#6A9955"))
        self.number_format = self._format(QColor("#B5CEA8"))
        self.function_format = self._format(QColor("#DCDCAA"))

        # Define regex patterns
        self.rules = []

        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def", "del", "elif",
            "else", "except", "False", "finally", "for", "from", "global", "if",
            "import", "in", "is", "lambda", "None", "nonlocal", "not", "or", "pass",
            "raise", "return", "True", "try", "while", "with", "yield"
        ]
        self.rules += [(r"\b" + kw + r"\b", self.keyword_format) for kw in keywords]
        self.rules.append((r"#[^\n]*", self.comment_format))
        self.rules.append((r"\".*?\"|'.*?'", self.string_format))
        self.rules.append((r"\b[0-9]+\b", self.number_format))
        self.rules.append((r"\b[A-Za-z_][A-Za-z0-9_]*(?=\()", self.function_format))

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
