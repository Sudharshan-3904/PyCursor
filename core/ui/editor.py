from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QColor, QFont, QAction, QFontDatabase, QFontInfo
from PyQt6.QtCore import pyqtSignal
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from core.ui.theme import COLORS, LIGHT_COLORS
import os

class CodeEditor(QsciScintilla):
    """
    Advanced source code editor based on QScintilla.
    Provides syntax highlighting, indentation, and integrated Git/AI operations.
    """
    git_blame_requested = pyqtSignal(str)
    git_history_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initializes the editor with default settings for Python development.
        """
        super().__init__(parent)

        self._setup_font()
        
        self.setup_lexer()
        self.apply_theme_colors()

        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)

        # Set line number margin width (calculate width for 4 digits)
        font_metrics = self.fontMetrics()
        margin_width = font_metrics.horizontalAdvance("0000") + 10  # Add some padding
        self.setMarginWidth(0, margin_width)

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self._modified = False
        self.textChanged.connect(self._on_text_changed)

        # Ensure font is properly set after all initialization
        self._ensure_font_valid()

    def _ensure_font_valid(self):
        """
        Final validation to ensure the editor font is properly set and valid.
        """
        font = self.font()
        if font.pointSize() <= 0:
            font.setPixelSize(-1)
            font.setPointSize(11)
            self.setFont(font)
        
        if self.lexer():
            lexer_font = self.lexer().font(0)  # Get the default font from lexer
            if lexer_font.pointSize() <= 0:
                self.lexer().setDefaultFont(font)

    def resizeEvent(self, event):
        """
        Handle resize events to ensure fonts remain valid.
        """
        super().resizeEvent(event)
        # Ensure font remains valid after resize
        font = self.font()
        if font.pointSize() <= 0:
            font.setPixelSize(-1)
            font.setPointSize(11)
            self.setFont(font)
            if self.lexer():
                self.lexer().setDefaultFont(font)
            self.setMarginsFont(font)

    def _setup_font(self):
        """
        Sets up the editor font with proper fallbacks and validation.
        """
        # Use system fixed font to ensure a valid monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPixelSize(-1)
        font.setPointSize(11)
        
        # Verify the font is actually resolved correctly
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            # Fallback to a known font
            font = QFont("Courier New", 11)
            font.setPixelSize(-1)
            font.setPointSize(11)
        
        # Ensure font size is valid and positive
        if font.pointSize() <= 0:
            font.setPointSize(11)
        
        # Additional validation - ensure the font is actually usable
        if font.pointSizeF() <= 0.0:
            font.setPointSizeF(11.0)
        
        # Set the font on the widget
        self.setFont(font)
        
        # Ensure font is properly set after all initialization
        if self.font().pointSize() <= 0:
            font.setPixelSize(-1)
            font.setPointSize(11)
            self.setFont(font)

    def _on_text_changed(self):
        """
        Internal handler to track modification state.
        """
        self._modified = True

    def isModified(self):
        """
        Returns true if the buffer has unsaved changes.
        """
        return self._modified

    def setModified(self, value: bool):
        """
        Explicitly sets the modification flag.
        """
        self._modified = value

    def append_text(self, text: str):
        """
        Appends text to the end of the document, ensuring proper newline handling.
        """
        text = text.replace("\r\n", "\n")
        existing_text = self.text()
        if existing_text and not existing_text.endswith("\n"):
            self.setText(existing_text + "\n" + text)
        else:
            self.setText(existing_text + text)
            
    def contextMenuEvent(self, event):
        """
        Constructs and displays the context menu with standard and custom IDE actions.
        """
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        
        # Symbol Navigation
        def_action = QAction("Go to Definition", self)
        def_action.triggered.connect(self.go_to_definition)
        menu.addAction(def_action)
        
        menu.addSeparator()

        # Edit Operations
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo)
        undo_action.setEnabled(self.isUndoAvailable())
        menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo)
        redo_action.setEnabled(self.isRedoAvailable())
        menu.addAction(redo_action)
        
        menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(self.hasSelectedText())
        menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.hasSelectedText())
        menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        # AI Intelligence Actions
        explain_action = QAction("✨ Explain with AI", self)
        explain_action.triggered.connect(self.ai_explain)
        menu.addAction(explain_action)
        
        refactor_action = QAction("✨ Refactor with AI", self)
        refactor_action.triggered.connect(self.ai_refactor)
        menu.addAction(refactor_action)

        menu.addSeparator()

        # Git Integration Actions
        blame_action = QAction("Git Blame", self)
        blame_action.triggered.connect(self.request_blame)
        menu.addAction(blame_action)
        
        history_action = QAction("Git History", self)
        history_action.triggered.connect(self.request_history)
        menu.addAction(history_action)
        
        menu.exec(event.globalPos())

    def go_to_definition(self):
        """
        Request the LSP server for symbol definition location.
        """
        line, col = self.getCursorPosition()
        if hasattr(self, 'file_path') and self.file_path:
            parent = self._find_main_window()
            if parent and hasattr(parent, 'lsp_manager'):
                parent.lsp_manager.get_definition(self.file_path, line, col, self._handle_definition)

    def _handle_definition(self, result):
        """
        Navigates to the definition location returned by the LSP.
        """
        if not result: return
        
        if isinstance(result, list):
            if not result: return
            target = result[0]
        else:
            target = result
            
        uri = target.get('uri')
        range_data = target.get('range', {}).get('start', {})
        line = range_data.get('line', 0)
        
        if uri:
            path = uri.replace('file:///', '').replace('/', os.sep)
            parent = self._find_main_window()
            if parent:
                parent.open_file_in_tab(path)
                editor = parent.editor_tabs.currentWidget()
                if editor:
                    editor.setCursorPosition(line, 0)
                    editor.ensureLineVisible(line)

    def ai_explain(self):
        """
        Sends the selected code (or entire file) to the AI assistant for explanation.
        """
        text = self.selectedText() or self.text()
        if not text: return
        parent = self._find_main_window()
        if parent and hasattr(parent, 'ai_widget'):
            parent.toggle_view("ai")
            parent.ai_widget.input_field.setText(f"Explain this code:\n\n```python\n{text}\n```")
            parent.ai_widget.handle_send()

    def ai_refactor(self):
        """
        Asks the AI assistant to suggest refactoring for the selected code block.
        """
        text = self.selectedText()
        if not text:
            return
        parent = self._find_main_window()
        if parent and hasattr(parent, 'ai_widget'):
            parent.toggle_view("ai")
            parent.ai_widget.input_field.setText(f"Refactor this code to be more efficient and clean:\n\n```python\n{text}\n```")
            parent.ai_widget.handle_send()

    def _find_main_window(self):
        """
        Walks up the widget tree to find the main application window.
        """
        pw = self.parent()
        while pw:
            if hasattr(pw, 'ai_widget') or hasattr(pw, 'lsp_manager'):
                return pw
            pw = pw.parent()
        return None
        
    def request_blame(self):
        """
        Emits a signal to show Git blame for the current file.
        """
        if hasattr(self, 'file_path') and self.file_path:
            self.git_blame_requested.emit(self.file_path)
            
    def request_history(self):
        """
        Emits a signal to show Git history for the current file.
        """
        if hasattr(self, 'file_path') and self.file_path:
            self.git_history_requested.emit(self.file_path)

    def setup_lexer(self):
        """
        Configures the Python lexer with default fonts and base colors.
        """
        # Get the font that was already set
        font = self.font()
        
        # Ensure the font is still valid
        if font.pointSize() <= 0:
            font.setPixelSize(-1)
            font.setPointSize(11)
            self.setFont(font)
        
        self.setMarginsFont(font)
        
        # Set the widget font before setting the lexer to prevent defaults
        self.setFont(font)
        
        lexer = QsciLexerPython()
        # Ensure lexer font is valid before setting
        lexer_font = font
        lexer_font.setPixelSize(-1)
        lexer_font.setPointSize(11)
        lexer.setDefaultFont(lexer_font)
        
        # Set the font for all lexer styles to ensure valid font sizes
        for style in range(16):
            lexer.setFont(lexer_font, style)
        
        self.setLexer(lexer)
        
        # Ensure the widget font is set after lexer to override any defaults
        self.setFont(font)
        self.setMarginsFont(font)

    def apply_theme_colors(self, theme='dark'):
        """
        Applies a comprehensive color palette based on the chosen theme (dark/light).
        Configures paper colors, caret, selection, and syntax highlighting.
        """
        theme_colors = COLORS if theme == 'dark' else LIGHT_COLORS
        bg = QColor(theme_colors['editor_bg'])
        fg = QColor(theme_colors['text_primary'])
        
        self.setPaper(bg)
        if self.lexer():
            self.lexer().setPaper(bg)
            self.lexer().setDefaultColor(fg)
            
            # Syntax highlighting adjustments
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
        """
        Updates the editor's visual style dynamically when theme is changed.
        """
        self.apply_theme_colors(theme_name)
