"""
Design System and Theming Module for PyCursor IDE.
Defines the visual language, color palettes, and global stylesheets for both dark and light modes.
Standardizes UI components using Catppuccin-inspired Mocha (Dark) and Latte (Light) palettes.
"""

# Dark Theme Palette (Mocha)
COLORS = {
    'bg_primary': '#1e1e2e',      # Main background
    'bg_secondary': '#181825',    # Secondary surfaces (Sidebar/Terminal)
    'bg_tertiary': '#11111b',     # Deep backgrounds (Title/Crust)
    'bg_elevated': '#313244',     # Surface level components
    'bg_selection': '#45475a',    # Selection highlights
    'bg_input': '#11111b',        # Input field base
    
    'text_primary': '#cdd6f4',    # Primary text
    'text_secondary': '#a6adc8',  # Muted descriptive text
    'text_tertiary': '#6c7086',   # Tertiary/Subtle text
    'text_disabled': '#6c7086',   # Disabled state text
    'text_highlight': '#ffffff',  # Over-active text
    
    'accent_blue': '#89b4fa',     # Action blue
    'accent_purple': '#cba6f7',   # AI features mauve
    'accent_green': '#a6e3a1',    # Success green
    'accent_orange': '#fab387',   # Warning peach
    'accent_red': '#f38ba8',      # Error red
    'accent_yellow': '#f9e2af',   # Information yellow
    
    'border': '#313244',          # Component borders
    'border_light': '#45475a',    # Subtle contrast borders
    'border_focus': '#89b4fa',    # Active focus state
    
    'button_bg': '#313244',
    'button_hover': '#45475a',
    'button_pressed': '#1e1e2e',
    'button_active': '#1e1e2e',
    
    'tab_active_bg': '#1e1e2e',
    'tab_inactive_bg': '#181825',
    'tab_hover_bg': '#1e1e2e',
    
    'statusbar_bg': '#89b4fa',    
    'statusbar_text': '#1e1e2e',
    
    'editor_bg': '#1e1e2e',
    'editor_line_bg': '#181825',
    'editor_selection': '#45475a',
    'editor_cursor': '#f5e0dc',   
    
    'sidebar_bg': '#181825',
    'sidebar_hover': '#313244',
    'sidebar_selected': '#45475a',
}

# Light Theme Palette (Latte)
LIGHT_COLORS = {
    'bg_primary': '#eff1f5',
    'bg_secondary': '#e6e9ef',
    'bg_tertiary': '#dce0e8',
    'bg_elevated': '#ccd0da',
    'bg_selection': '#acb0be',
    'bg_input': '#dce0e8',
    
    'text_primary': '#4c4f69',
    'text_secondary': '#5c5f77',
    'text_tertiary': '#9ca0b0',
    'text_disabled': '#9ca0b0',
    'text_highlight': '#1e66f5',
    
    'accent_blue': '#1e66f5',
    'accent_purple': '#8839ef',
    'accent_green': '#40a02b',
    'accent_orange': '#fe640b',
    'accent_red': '#d20f39',
    'accent_yellow': '#df8e1d',
    
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
    
    'editor_bg': '#eff1f5',
    'editor_line_bg': '#e6e9ef',
    'editor_selection': '#acb0be',
    'editor_cursor': '#dc8a78',
    
    'sidebar_bg': '#e6e9ef',
    'sidebar_hover': '#ccd0da',
    'sidebar_selected': '#acb0be',
}

def get_color(color_name, theme='dark'):
    """
    Retrieves a specific color from the current theme palette.
    """
    palette = COLORS if theme == 'dark' else LIGHT_COLORS
    return palette.get(color_name, '#ffffff')

def get_icon_color(theme='dark'):
    """
    Returns the standard color for UI icons in the current theme.
    """
    from PyQt6.QtGui import QColor
    color_hex = get_color('text_secondary', theme)
    return QColor(color_hex)

def get_stylesheet(theme='dark'):
    """
    Generates the comprehensive application-wide Qt Stylesheet (QSS).
    Maps theme palette colors to functional CSS rules for widgets and components.
    """
    theme_colors = COLORS if theme == 'dark' else LIGHT_COLORS
    return f"""
    QMainWindow {{
        background-color: {theme_colors['bg_primary']};
    }}
    
    QWidget {{
        background-color: {theme_colors['bg_primary']};
        color: {theme_colors['text_primary']};
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        font-size: 10pt;
    }}
    
    /* Exclude QsciScintilla and QTextEdit from global font settings to prevent conflicts */
    QsciScintilla, QTextEdit {{
        font-family: inherit;
    }}
    
    QMenuBar {{
        background-color: {theme_colors['bg_secondary']};
        border-bottom: 1px solid {theme_colors['border']};
        padding: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {theme_colors['bg_elevated']};
        border-radius: 4px;
    }}
    
    QMenu {{
        background-color: {theme_colors['bg_secondary']};
        border: 1px solid {theme_colors['border_light']};
        padding: 5px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme_colors['accent_blue']};
        color: {theme_colors['bg_primary']};
    }}
    
    QTabWidget::pane {{
        border-top: 1px solid {theme_colors['border']};
    }}
    
    QTabBar::tab {{
        padding: 8px 16px;
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_secondary']};
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme_colors['bg_primary']};
        color: {theme_colors['accent_blue']};
        border-top: 2px solid {theme_colors['accent_blue']};
    }}
    
    QDockWidget::title {{
        background-color: {theme_colors['bg_secondary']};
        color: {theme_colors['text_secondary']};
        padding: 8px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 8pt;
    }}
    
    QPushButton {{
        background-color: {theme_colors['button_bg']};
        border: 1px solid {theme_colors['border']};
        border-radius: 4px;
        padding: 5px 12px;
    }}
    
    QPushButton:hover {{
        background-color: {theme_colors['button_hover']};
    }}
    
    QPushButton#SearchOptionBtn {{
        background-color: transparent;
        padding: 0;
        border: 1px solid transparent;
        color: {theme_colors['text_secondary']};
    }}
    
    QPushButton#SearchOptionBtn:checked {{
        background-color: {theme_colors['bg_selection']};
        border: 1px solid {theme_colors['accent_blue']};
        color: {theme_colors['accent_blue']};
    }}
    
    QPushButton#SearchOptionBtn:hover, QPushButton#AIChatControl:hover {{
        background-color: {theme_colors['bg_elevated']};
    }}
    
    QPushButton#AIChatControl {{
        background-color: {theme_colors['bg_elevated']};
        border: 1px solid {theme_colors['border']};
        padding: 4px;
        border-radius: 4px;
    }}
    
    QPushButton#AIChatControl:checked {{
        background-color: {theme_colors['bg_selection']};
        border: 1px solid {theme_colors['accent_blue']};
    }}
    
    QLineEdit, QTextEdit {{
        background-color: {theme_colors['bg_tertiary']};
        border: 1px solid {theme_colors['border']};
        padding: 5px;
        border-radius: 3px;
    }}
    
    QTreeView {{
        background-color: {theme_colors['sidebar_bg']};
        border: none;
    }}
    
    QTreeView::item:selected {{
        background-color: {theme_colors['bg_selection']};
        border-left: 3px solid {theme_colors['accent_blue']};
    }}

    QScrollBar:vertical {{
        background-color: transparent;
        width: 12px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {theme_colors['bg_elevated']};
        border-radius: 6px;
        margin: 2px;
    }}
    
    QStatusBar {{
        background-color: {theme_colors['bg_secondary']};
        border-top: 1px solid {theme_colors['border']};
        min-height: 22px;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    QStatusBar QLabel, QStatusBar QPushButton {{
        background-color: transparent;
        color: {theme_colors['text_secondary']};
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 11px;
        padding: 0px 12px;
        border-left: 1px solid {theme_colors['border_light']};
    }}
    
    QStatusBar QLabel#StatusFirst {{
        border-left: none;
    }}
    
    QStatusBar QPushButton {{
        border: none;
        border-radius: 0;
        text-align: center;
    }}
    
    QStatusBar QPushButton:hover {{
        background-color: {theme_colors['bg_elevated']};
    }}
    
    QToolBar {{
        background-color: {theme_colors['bg_secondary']};
        border-right: 1px solid {theme_colors['border']};
    }}
    """
