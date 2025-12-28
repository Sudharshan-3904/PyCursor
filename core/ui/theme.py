"""
Modern, Premium Interface Theme for PyCursor IDE
Using a refined dark palette (inspired by Catppuccin/Modern VS Code)
"""

COLORS = {
    # Backgrounds
    'bg_primary': '#1e1e2e',      # Main editor background (Mocha Base)
    'bg_secondary': '#181825',    # Sidebar/Terminal background (Mocha Mantle)
    'bg_tertiary': '#11111b',     # Title bar/Deep background (Mocha Crust)
    'bg_elevated': '#313244',     # Input fields, hover states (Mocha Surface0)
    'bg_selection': '#45475a',    # Selection background (Mocha Surface1)
    'bg_input': '#11111b',        # Specific input background (matches bg_tertiary)
    
    # Text
    'text_primary': '#cdd6f4',    # Main text (Text)
    'text_secondary': '#a6adc8',  # Subtext (Subtext0)
    'text_tertiary': '#6c7086',   # Tertiary text (same as disabled for now)
    'text_disabled': '#6c7086',   # Disabled text (Overlay0)
    'text_highlight': '#ffffff',  # Highlighted text
    
    # Accents
    'accent_blue': '#89b4fa',     # Primary Accent (Blue)
    'accent_purple': '#cba6f7',   # AI/Special (Mauve)
    'accent_green': '#a6e3a1',    # Success/Git Add (Green)
    'accent_orange': '#fab387',   # Warning (Peach)
    'accent_red': '#f38ba8',      # Error/Git Delete (Red)
    'accent_yellow': '#f9e2af',   # Info (Yellow)
    
    # Components
    'border': '#313244',          # Borders (Surface0)
    'border_light': '#45475a',    # Lighter Borders (Surface1)
    'border_focus': '#89b4fa',    # Focus Ring
    
    'button_bg': '#313244',
    'button_hover': '#45475a',
    'button_pressed': '#1e1e2e',
    'button_active': '#1e1e2e',
    
    'tab_active_bg': '#1e1e2e',
    'tab_inactive_bg': '#181825',
    'tab_hover_bg': '#1e1e2e',
    
    'statusbar_bg': '#89b4fa',    # Blue status bar like VS Code default
    'statusbar_text': '#1e1e2e',
    
    # Editor specifics (mapped for compatibility)
    'editor_bg': '#1e1e2e',
    'editor_line_bg': '#181825',
    'editor_selection': '#45475a',
    'editor_cursor': '#f5e0dc',   # Rosewater cursor
    
    'sidebar_bg': '#181825',
    'sidebar_hover': '#313244',
    'sidebar_selected': '#45475a',
    'list_hover': '#313244',
    'list_selected': '#45475a',

    'accent_blue_hover': '#b4befe', # Lavender
}

def get_stylesheet():
    """Get the complete stylesheet for PyCursor IDE with animations and glass-like feel"""
    return f"""
    /* ===== GLOBAL STYLES ===== */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
    }}
    
    QWidget {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Roboto', sans-serif;
        font-size: 13px;
        selection-background-color: {COLORS['accent_blue']};
        selection-color: {COLORS['bg_primary']};
    }}
    
    /* ===== MENU BAR ===== */
    QMenuBar {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border-bottom: 1px solid {COLORS['border']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 10px;
        border-radius: 4px;
        margin: 0 2px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_highlight']};
    }}
    
    QMenu {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QMenu::item {{
        padding: 6px 28px 6px 12px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['accent_blue']};
        color: {COLORS['bg_primary']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {COLORS['border']};
        margin: 4px 8px;
    }}
    
    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {{
        border: none;
        background-color: {COLORS['bg_primary']};
        border-top: 1px solid {COLORS['border']};
    }}
    
    QTabBar {{
        background-color: {COLORS['bg_secondary']};
        border-bottom: 1px solid {COLORS['border']};
        qproperty-drawBase: 0;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        padding: 8px 16px;
        margin-right: 1px;
        border: none;
        border-top: 2px solid transparent;
        min-width: 80px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['accent_blue']};
        border-top: 2px solid {COLORS['accent_blue']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
    }}
    
    QTabBar::close-button {{
        image: url(none); /* We use custom close buttons in code, but standardizing just in case */
    }}
    
    /* ===== DOCK WIDGETS ===== */
    QDockWidget {{
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
        color: {COLORS['text_primary']};
        border: none;
    }}
    
    QDockWidget::title {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_secondary']};
        padding: 8px 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 11px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {COLORS['button_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 5px;
        padding: 6px 12px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
        border: 1px solid {COLORS['border_light']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['accent_blue']};
        color: {COLORS['bg_primary']};
        border-color: {COLORS['accent_blue']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_disabled']};
        border-color: {COLORS['border']};
    }}
    
    /* Primary Action Button (e.g. Commit) */
    QPushButton[class="primary"] {{
        background-color: {COLORS['accent_blue']};
        color: {COLORS['bg_primary']};
        border: none;
    }}
    
    QPushButton[class="primary"]:hover {{
        background-color: {COLORS['accent_blue_hover']};
    }}
    
    /* ===== INPUT FIELDS ===== */
    QTextEdit, QPlainTextEdit, QLineEdit {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        selection-background-color: {COLORS['bg_selection']};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {{
        border: 1px solid {COLORS['border_focus']};
        background-color: {COLORS['bg_primary']};
    }}
    
    /* ===== SIDEBAR / TREE VIEW ===== */
    QTreeView {{
        background-color: {COLORS['sidebar_bg']};
        color: {COLORS['text_primary']};
        border: none;
        outline: none;
    }}
    
    QTreeView::item {{
        padding: 4px 6px;
        border-radius: 4px;
        margin: 1px 4px;
    }}
    
    QTreeView::item:hover {{
        background-color: {COLORS['sidebar_hover']};
    }}
    
    QTreeView::item:selected {{
        background-color: {COLORS['sidebar_selected']};
        color: {COLORS['text_highlight']};
        border-left: 2px solid {COLORS['accent_blue']};
    }}
    
    QTreeView::branch {{
        background-color: transparent;
    }}
    
    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['bg_elevated']};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_disabled']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: transparent;
        height: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['bg_elevated']};
        min-width: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['text_disabled']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {{
        background-color: {COLORS['bg_secondary']};
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['accent_blue']};
    }}
    
    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border-top: 1px solid {COLORS['border']};
        font-weight: normal;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    QStatusBar QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}
    
    /* ===== TOOL BAR (Activity Bar) ===== */
    QToolBar {{
        background-color: {COLORS['bg_secondary']};
        border-right: 1px solid {COLORS['border']};
        spacing: 8px;
    }}
    
    QToolButton {{
        background-color: transparent;
        border: none;
        border-left: 3px solid transparent;
        border-radius: 0;
        padding: 8px;
    }}
    
    QToolButton:hover {{
        background-color: {COLORS['bg_elevated']};
    }}
    
    QToolButton:checked {{
        border-left: 3px solid {COLORS['accent_blue']};
        background-color: {COLORS['bg_elevated']};
    }}
    
    /* ===== COMBO BOX ===== */
    QComboBox {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 5px 10px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['accent_blue']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['accent_blue']};
    }}
    
    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['accent_blue']};
        border-radius: 4px;
        padding: 4px;
    }}
    """

def get_light_stylesheet():
    # Placeholder for light mode, possibly just return dark for now to maintain the vibe
    return get_stylesheet()
