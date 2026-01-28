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
    'text_dim': '#6c7086', # Muted text
}

LIGHT_COLORS = {
    # Backgrounds
    'bg_primary': '#eff1f5',      # Main editor background (Latte Base)
    'bg_secondary': '#e6e9ef',    # Sidebar/Terminal background (Latte Mantle)
    'bg_tertiary': '#dce0e8',     # Title bar/Deep background (Latte Crust)
    'bg_elevated': '#ccd0da',     # Input fields, hover states (Latte Surface0)
    'bg_selection': '#acb0be',    # Selection background (Latte Surface1)
    'bg_input': '#dce0e8',
    
    # Text
    'text_primary': '#4c4f69',    # Main text (Text)
    'text_secondary': '#5c5f77',  # Subtext (Subtext0)
    'text_tertiary': '#9ca0b0',
    'text_disabled': '#9ca0b0',
    'text_highlight': '#1e66f5',
    
    # Accents
    'accent_blue': '#1e66f5',     # Primary Accent (Blue)
    'accent_purple': '#8839ef',   # AI/Special (Mauve)
    'accent_green': '#40a02b',    # Success
    'accent_orange': '#fe640b',   # Warning
    'accent_red': '#d20f39',      # Error
    'accent_yellow': '#df8e1d',   # Info
    
    # Components
    'border': '#ccd0da',
    'border_light': '#bcc0cc',
    'border_focus': '#1e66f5',
    
    'button_bg': '#ccd0da',
    'button_hover': '#bcc0cc',
    'button_pressed': '#eff1f5',
    'button_active': '#eff1f5',
    
    'tab_active_bg': '#eff1f5',
    'tab_inactive_bg': '#e6e9ef',
    'tab_hover_bg': '#eff1f5',
    
    'statusbar_bg': '#1e66f5',
    'statusbar_text': '#eff1f5',
    
    # Editor specifics
    'editor_bg': '#eff1f5',
    'editor_line_bg': '#e6e9ef',
    'editor_selection': '#acb0be',
    'editor_cursor': '#dc8a78',   # Rosewater
    
    'sidebar_bg': '#e6e9ef',
    'sidebar_hover': '#ccd0da',
    'sidebar_selected': '#acb0be',
    'list_hover': '#ccd0da',
    'list_selected': '#acb0be',

    'accent_blue_hover': '#7287fd', # Lavender
    'text_dim': '#9ca0b0',
}

def get_stylesheet(theme='dark'):
    """Get the complete stylesheet for PyCursor IDE with animations and glass-like feel"""
    theme_colors = COLORS if theme == 'dark' else LIGHT_COLORS
    return f"""
    /* ===== GLOBAL STYLES ===== */
    QMainWindow {{
        background-color: {theme_colors['bg_primary']};
        color: {theme_colors['text_primary']};
    }}
    
    QWidget {{
        background-color: {theme_colors['bg_primary']};
        color: {theme_colors['text_primary']};
        font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Roboto', sans-serif;
        font-size: 13px;
        selection-background-color: {theme_colors['accent_blue']};
        selection-color: {theme_colors['bg_primary']};
    }}
    
    /* ===== MENU BAR ===== */
    QMenuBar {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_primary']};
        border-bottom: 1px solid {theme_colors['border']};
        padding: 4px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 10px;
        border-radius: 4px;
        margin: 0 2px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {theme_colors['bg_elevated']};
        color: {theme_colors['text_highlight']};
    }}
    
    QMenu {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_primary']};
        border: 1px solid {theme_colors['border_light']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QMenu::item {{
        padding: 6px 28px 6px 12px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme_colors['accent_blue']};
        color: {theme_colors['bg_primary']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {theme_colors['border']};
        margin: 4px 8px;
    }}
    
    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {{
        border: none;
        background-color: {theme_colors['bg_primary']};
        border-top: 1px solid {theme_colors['border']};
    }}
    
    QTabBar {{
        background-color: {theme_colors['bg_secondary']};
        border-bottom: 1px solid {theme_colors['border']};
        qproperty-drawBase: 0;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {theme_colors['text_secondary']};
        padding: 8px 16px;
        margin-right: 1px;
        border: none;
        border-top: 2px solid transparent;
        min-width: 80px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme_colors['bg_primary']};
        color: {theme_colors['accent_blue']};
        border-top: 2px solid {theme_colors['accent_blue']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {theme_colors['bg_elevated']};
        color: {theme_colors['text_primary']};
    }}
    
    /* ===== DOCK WIDGETS ===== */
    QDockWidget {{
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
        color: {theme_colors['text_primary']};
        border: none;
    }}
    
    QDockWidget::title {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_secondary']};
        padding: 8px 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 11px;
        border-bottom: 1px solid {theme_colors['border']};
    }}
    
    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {theme_colors['button_bg']};
        color: {theme_colors['text_primary']};
        border: 1px solid {theme_colors['border']};
        border-radius: 5px;
        padding: 6px 12px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {theme_colors['button_hover']};
        border: 1px solid {theme_colors['border_light']};
    }}
    
    QPushButton:pressed {{
        background-color: {theme_colors['accent_blue']};
        color: {theme_colors['bg_primary']};
        border-color: {theme_colors['accent_blue']};
    }}
    
    QPushButton:disabled {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_disabled']};
        border-color: {theme_colors['border']};
    }}
    
    /* ===== INPUT FIELDS ===== */
    QTextEdit, QPlainTextEdit, QLineEdit {{
        background-color: {theme_colors['bg_tertiary']};
        color: {theme_colors['text_primary']};
        border: 1px solid {theme_colors['border']};
        border-radius: 4px;
        padding: 6px;
        selection-background-color: {theme_colors['bg_selection']};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {{
        border: 1px solid {theme_colors['border_focus']};
        background-color: {theme_colors['bg_primary']};
    }}
    
    /* ===== SIDEBAR / TREE VIEW ===== */
    QTreeView {{
        background-color: {theme_colors['sidebar_bg']};
        color: {theme_colors['text_primary']};
        border: none;
        outline: none;
    }}
    
    QTreeView::item {{
        padding: 4px 6px;
        border-radius: 4px;
        margin: 1px 4px;
    }}
    
    QTreeView::item:hover {{
        background-color: {theme_colors['sidebar_hover']};
    }}
    
    QTreeView::item:selected {{
        background-color: {theme_colors['sidebar_selected']};
        color: {theme_colors['text_highlight']};
        border-left: 2px solid {theme_colors['accent_blue']};
    }}
    
    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {theme_colors['bg_elevated']};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {{
        background-color: {theme_colors['bg_secondary']};
    }}
    
    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_primary']};
        border-top: 1px solid {theme_colors['border']};
    }}
    
    /* ===== TOOL BAR (Activity Bar) ===== */
    QToolBar {{
        background-color: {theme_colors['bg_secondary']};
        border-right: 1px solid {theme_colors['border']};
    }}
    
    QToolButton:checked {{
        border-left: 3px solid {theme_colors['accent_blue']};
        background-color: {theme_colors['bg_elevated']};
    }}
    
    /* ===== COMBO BOX ===== */
    QComboBox {{
        background-color: {theme_colors['bg_elevated']};
        color: {theme_colors['text_primary']};
        border: 1px solid {theme_colors['border']};
        border-radius: 4px;
    }}
    
    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_primary']};
        border: 1px solid {theme_colors['accent_blue']};
    }}
    """

def get_light_stylesheet():
    return get_stylesheet(theme='light')
