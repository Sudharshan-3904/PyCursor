from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QColor, QFont, QAction, QFontDatabase, QFontInfo
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from core.ui.theme import COLORS, LIGHT_COLORS
from core.ui.completion_popup import CompletionPopup
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

        # IntelliSense Components
        self.completion_popup = CompletionPopup(self)
        self.completion_popup.list_widget.itemActivated.connect(self._on_completion_selected)
        self.completion_popup.list_widget.itemClicked.connect(self._on_completion_selected)
        
        # Ensure font is properly set after all initialization
        self._ensure_font_valid()

    def _ensure_font_valid(self):
        """
        Final validation to ensure the editor font is properly set and valid.
        """
        font = self.font()
        if font.pointSize() <= 0:
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
        font.setPointSize(11)
        
        # Verify the font is actually resolved correctly
        font_info = QFontInfo(font)
        if font_info.pointSize() <= 0:
            # Fallback to a known font
            font = QFont("Courier New", 11)
            font.setPointSize(11)
        
        # Ensure font size is valid and positive
        if font.pointSize() <= 0:
            font.setPointSize(11)
        
        # Additional validation - ensure the font is actually usable
        if font.pointSizeF() <= 0.0:
            font.setPointSizeF(11.0)
        
        # Set the font on the widget
        self.setFont(font)
        
        # Use the font that was already set
        self._ensure_font_valid()

        # Ghost Text (Inline Copilot) Settings
        self.ghost_text = ""
        self.ghost_interval = 500 # Default 500ms idle trigger
        self.ghost_timer = QTimer(self)
        self.ghost_timer.setSingleShot(True)
        self.ghost_timer.setInterval(self.ghost_interval)
        self.ghost_timer.timeout.connect(self._trigger_ghost_text)
        self.textChanged.connect(lambda: self.ghost_timer.start())
        
        # State Caching
        self._cached_main_window = None
        
        # Indicator for gray text
        self.INDICATOR_GHOST = 8
        self.indicatorDefine(QsciScintilla.IndicatorStyle.PlainIndicator, self.INDICATOR_GHOST)
        self.setIndicatorForegroundColor(QColor(COLORS['text_disabled']), self.INDICATOR_GHOST)

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
        Appends text to the end of the document with O(1) efficiency.
        """
        text = text.replace("\r\n", "\n")
        
        # Ensure we start on a new line if document isn't empty and doesn't end with one
        last_line = self.lines() - 1
        if self.lineLength(last_line) > 0:
            self.append("\n")
            
        self.append(text)
            
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

    def trigger_completion(self):
        """
        Triggers LSP autocompletion at current cursor position.
        """
        line, col = self.getCursorPosition()
        if hasattr(self, 'file_path') and self.file_path:
            parent = self._find_main_window()
            if parent and hasattr(parent, 'lsp_manager'):
                parent.lsp_manager.get_completion(self.file_path, line, col, self._handle_completion)

    def _on_completion_selected(self, item):
        """
        Handler called when a completion item is activated in the popup.
        Inserts the chosen text into the document, replacing any
        partially-typed word to the left of the cursor.
        """
        if item is None:
            return

        completion_text = item.text()
        if completion_text:
            # determine the start of the current word fragment
            line, col = self.getCursorPosition()
            try:
                line_text = self.text(line)
            except Exception:
                line_text = ""

            start = col
            while start > 0 and (line_text[start - 1].isalnum() or line_text[start - 1] == "_"):
                start -= 1

            if start != col:
                # select the fragment so that replaceSelectedText will overwrite it
                self.setSelection(line, start, line, col)
            # replace selected text (or insert if nothing selected)
            self.replaceSelectedText(completion_text)

        # hide the popup and return focus to editor
        self.completion_popup.hide()
        self.setFocus()

    def _handle_completion(self, result):
        """
        Processes LSP completion results and shows the popup.
        """
        if not result: return
        items = result.get('items', []) if isinstance(result, dict) else result
        if not items: return
        
        # Filter and show popup
        self.completion_popup.set_items(items)
        pos = self.mapToGlobal(self.cursor_pos_to_pixel())
        self.completion_popup.show_at(pos)

    def cursor_pos_to_pixel(self):
        """
        Converts cursor line/col to relative pixel coordinates for popup placement.
        """
        # Get raw Scintilla position
        pos = self.SendScintilla(2008) # SCI_GETCURRENTPOS
        x = self.SendScintilla(2164, 0, pos) # SCI_POINTXFROMPOS
        y = self.SendScintilla(2165, 0, pos) # SCI_POINTYFROMPOS
        
        from PyQt6.QtCore import QPoint
        return QPoint(x, y)

    def _trigger_ghost_text(self):
        """
        Triggers a sub-1sec completion request for ghost text.
        """
        line, col = self.getCursorPosition()
        if hasattr(self, 'file_path') and self.file_path:
            parent = self._find_main_window()
            if parent and hasattr(parent, 'lsp_manager'):
                parent.lsp_manager.get_completion(self.file_path, line, col, self._handle_ghost_response)

    def _handle_ghost_response(self, result):
        """
        Renders the first suggestion as gray ghost text.
        """
        if not result: return
        items = result.get('items', []) if isinstance(result, dict) else result
        if not items: return
        
        suggestion = items[0].get("label", "").split("\n")[0]
        self.ghost_text = suggestion
        # Rendering ghost text is tricky in QScintilla without a custom lexer.
        # For Phase 4, we'll use an indicator at the cursor position.
        line, col = self.getCursorPosition()
        self.fill_ghost_text(line, col, suggestion)

    def _on_completion_selected(self, item):
        """
        Inserts the selected completion item into the editor.
        """
        self.completion_popup.hide()
        if not item: return
        
        # Get the word currently being typed
        line, col = self.getCursorPosition()
        current_line = self.text(line)
        
        # Simple back-search for word start (alphanumeric or underscore)
        start_col = col
        while start_col > 0 and (current_line[start_col-1].isalnum() or current_line[start_col-1] == '_'):
            start_col -= 1
            
        # Replace the word fragment with selection
        self.setSelection(line, start_col, line, col)
        self.replaceSelectedText(item.text())
        self.setFocus()

    def fill_ghost_text(self, line, col, text):
        """
        Renders ghost text at the specified position.
        """
        # For now, we use the indicator to highlight the end of the current word
        # with ghost-like appearance if possible, or just a placeholder.
        # Proper ghost text requires a custom lexer or multi-line indicators.
        pass

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
        Walks up the widget tree to find the main application window and caches the result.
        """
        if self._cached_main_window:
            return self._cached_main_window
            
        pw = self.parent()
        while pw:
            if hasattr(pw, 'ai_widget') or hasattr(pw, 'lsp_manager'):
                self._cached_main_window = pw
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
            font.setPointSize(11)
            self.setFont(font)
        
        self.setMarginsFont(font)
        
        # Set the widget font before setting the lexer to prevent defaults
        self.setFont(font)
        
        lexer = QsciLexerPython()
        # Ensure lexer font is valid before setting
        lexer_font = font
        lexer_font.setPointSize(11)
        lexer.setDefaultFont(lexer_font)
        
        # Set the font for all lexer styles to ensure valid font sizes
        for style in range(16):
            lexer.setFont(lexer_font, style)
        
        self.setLexer(lexer)
        
        # Ensure the widget font is set after lexer to override any defaults
        self.setFont(font)
        self.setMarginsFont(font)

    def apply_theme_colors(self, theme=None):
        """
        Applies a comprehensive color palette. 
        If theme name is not provided, uses the global COLORS palette from theme module.
        """
        from core.ui.theme import THEMES, COLORS
        
        if theme and theme in THEMES:
            theme_colors = THEMES[theme]['palette']
        else:
            # Fallback to the globally active palette
            theme_colors = COLORS
        
        bg = QColor(theme_colors['editor_bg'])
        fg = QColor(theme_colors['text_primary'])
        
        # Explicitly set the widget background
        self.setStyleSheet(f"background-color: {theme_colors['editor_bg']}; color: {theme_colors['text_primary']}; border: none;")
        self.setPaper(bg)
        
        if self.lexer():
            # Reset all styles to common font/bg first
            self.lexer().setDefaultPaper(bg)
            self.lexer().setPaper(bg)
            self.lexer().setDefaultColor(fg)
            
            for style in range(128):
                self.lexer().setFont(self.font(), style)
                self.lexer().setPaper(bg, style)
            
            # Setup Keyword Differentiation (Set 0: Decl, Set 1: Control)
            decl_keywords = "def class lambda"
            control_keywords = ("if for in return while break continue try except finally "
                               "else elif with as yield pass import from global nonlocal "
                               "assert del and or not is")
            
            self.lexer().setKeywords(decl_keywords, 0)
            self.lexer().setKeywords(control_keywords, 1)

            # Syntax highlighting mapping from theme tokens - Applied LAST to ensure they stick
            self.lexer().setColor(QColor(theme_colors.get('syntax_keyword', '#5DA9FF')), QsciLexerPython.Keyword)
            self.lexer().setColor(QColor(theme_colors.get('syntax_control', '#F43F5E')), QsciLexerPython.KeywordSet2)
            self.lexer().setColor(QColor(theme_colors.get('syntax_string', '#F43F5E')), QsciLexerPython.SingleQuotedString)
            self.lexer().setColor(QColor(theme_colors.get('syntax_string', '#F43F5E')), QsciLexerPython.DoubleQuotedString)
            self.lexer().setColor(QColor(theme_colors.get('syntax_string', '#F43F5E')), QsciLexerPython.TripleQuotedString)
            self.lexer().setColor(QColor(theme_colors.get('syntax_string', '#F43F5E')), QsciLexerPython.TripleDoubleQuotedString)
            self.lexer().setColor(QColor(theme_colors.get('syntax_comment', '#4ADE80')), QsciLexerPython.Comment)
            self.lexer().setColor(QColor(theme_colors.get('syntax_function', '#FACC15')), QsciLexerPython.FunctionMethodName)
            self.lexer().setColor(QColor(theme_colors.get('syntax_class', '#4ADE80')), QsciLexerPython.ClassName)
            self.lexer().setColor(QColor(theme_colors.get('syntax_number', '#A78BFA')), QsciLexerPython.Number)
            self.lexer().setColor(QColor(theme_colors.get('syntax_operator', '#FFFFFF')), QsciLexerPython.Operator)
            self.lexer().setColor(QColor(theme_colors.get('syntax_variable', '#E6EAF2')), QsciLexerPython.Identifier)
            self.lexer().setColor(QColor(theme_colors.get('syntax_decorator', '#FACC15')), QsciLexerPython.Decorator)
        
        self.setCaretForegroundColor(QColor(theme_colors['editor_cursor']))
        self.setSelectionBackgroundColor(QColor(theme_colors['editor_selection']))
        # Use a null color for foreground to preserve syntax highlighting in selections
        self.setSelectionForegroundColor(QColor())
        self.setEdgeColor(QColor(theme_colors['bg_tertiary']))
            

        # Margins & Gutter
        self.setMarginsBackgroundColor(bg)
        self.setMarginsForegroundColor(QColor(theme_colors['text_secondary']))
        
        # Folding setup
        fold_fg = QColor(theme_colors.get('editor_fold_fg', theme_colors['text_secondary']))
        fold_bg = QColor(theme_colors.get('editor_fold_bg', theme_colors['editor_bg']))
        
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(fold_bg, fold_bg)
        
        # Style the fold markers (the icons used for collapse/expand)
        # Markers 25-31 are standard folder markers in Scintilla
        for marker in range(25, 32):
            self.setMarkerBackgroundColor(fold_bg, marker)
            self.setMarkerForegroundColor(fold_fg, marker)
        
        # SCI_COLOURISE = 2028. Force re-calculation of all syntax styles
        self.SendScintilla(2028, 0, -1)

    def refresh_theme(self, theme_name):
        """
        Updates the editor's visual style dynamically when theme is changed.
        """
        self.apply_theme_colors(theme_name)
