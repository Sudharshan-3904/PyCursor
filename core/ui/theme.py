"""
Modern VS Code / Cursor-inspired theme for PyCursor IDE
Dark theme with clean, professional aesthetics
"""

COLORS = {
    'bg_primary': '#1e1e1e',  
    'bg_secondary': '#252526',
    'bg_tertiary': '#2d2d30', 
    'bg_elevated': '#3e3e42', 
    
    'editor_bg': '#1e1e1e',
    'editor_line_bg': '#282828',
    'editor_selection': '#3a3d41',
    'editor_cursor': '#aeafad',
    
    'sidebar_bg': '#252526',
    'sidebar_hover': '#2a2d2e',
    'sidebar_selected': '#37373d',
    
    'text_primary': '#cccccc',
    'text_secondary': '#858585',
    'text_disabled': '#656565',
    'text_highlight': '#ffffff',
    
    'accent_blue': '#444444',
    'accent_blue_hover': '#555555',
    'accent_orange': '#ce9178',
    'accent_green': '#4ec9b0',
    'accent_red': '#f48771',
    'accent_yellow': '#dcdcaa',
    
    'border': '#3e3e42',
    'border_light': '#454545',
    'border_focus': '#555555',
    
    'tab_active_bg': '#1e1e1e',
    'tab_inactive_bg': '#2d2d30',
    'tab_hover_bg': '#2a2d2e',
    
    'button_bg': '#3e3e42',
    'button_hover': '#4e4e4e',
    'button_pressed': '#2d2d30',
    
    'statusbar_bg': '#007acc',
    'statusbar_text': '#ffffff',
}

COLORS['statusbar_bg'] = '#1e1e1e'
COLORS['statusbar_text'] = '#cccccc'
COLORS['accent_blue'] = '#444444'
COLORS['border_focus'] = '#666666'
COLORS['button_bg'] = '#333333'
COLORS['button_hover'] = '#444444'


def get_stylesheet():
    """Get the complete stylesheet for PyCursor IDE"""
    return f"""
    /* ===== GLOBAL STYLES ===== */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
    }}
    
    QWidget {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Consolas', 'Monaco', monospace;
        font-size: 13px;
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
        padding: 6px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['bg_tertiary']};
    }}
    
    QMenuBar::item:pressed {{
        background-color: {COLORS['accent_blue']};
    }}
    
    QMenu {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 3px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['bg_tertiary']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {COLORS['border']};
        margin: 4px 0px;
    }}
    
    /* ===== TAB WIDGET ===== */
    QTabWidget::pane {{
        border: none;
        background-color: {COLORS['bg_primary']};
    }}
    
    QTabBar {{
        background-color: {COLORS['bg_secondary']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['tab_inactive_bg']};
        color: {COLORS['text_secondary']};
        padding: 8px 16px;
        margin-right: 2px;
        border: none;
        border-top: 2px solid transparent;
        min-width: 80px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['tab_active_bg']};
        color: {COLORS['text_highlight']};
        border-top: 2px solid {COLORS['accent_blue']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['tab_hover_bg']};
        color: {COLORS['text_primary']};
    }}
    
    QTabBar::close-button {{
        image: url(none);
        background-color: transparent;
        border-radius: 3px;
        padding: 2px;
    }}
    
    QTabBar::close-button:hover {{
        background-color: {COLORS['bg_elevated']};
    }}
    
    /* ===== DOCK WIDGETS ===== */
    QDockWidget {{
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
        color: {COLORS['text_primary']};
    }}
    
    QDockWidget::title {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        padding: 6px;
        border-bottom: 1px solid {COLORS['border']};
        font-weight: 600;
        text-align: left;
    }}
    
    QDockWidget::close-button, QDockWidget::float-button {{
        background-color: transparent;
        border: none;
        padding: 2px;
    }}
    
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
        background-color: {COLORS['bg_tertiary']};
        border-radius: 3px;
    }}
    
    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {COLORS['button_bg']};
        color: {COLORS['text_highlight']};
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['button_pressed']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_disabled']};
    }}
    
    /* Secondary button style */
    QPushButton[class="secondary"] {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['bg_elevated']};
    }}
    
    /* ===== TEXT EDIT / INPUT ===== */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['editor_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px;
        selection-background-color: {COLORS['editor_selection']};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {COLORS['border_focus']};
    }}
    
    QLineEdit {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 10px;
        selection-background-color: {COLORS['editor_selection']};
    }}
    
    QLineEdit:focus {{
        border: 1px solid {COLORS['border_focus']};
        background-color: {COLORS['bg_primary']};
    }}
    
    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: {COLORS['bg_primary']};
        width: 14px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['bg_elevated']};
        min-height: 30px;
        border-radius: 7px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: #4e4e4e;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['bg_primary']};
        height: 14px;
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['bg_elevated']};
        min-width: 30px;
        border-radius: 7px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: #4e4e4e;
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* ===== TREE VIEW (Sidebar) ===== */
    QTreeView {{
        background-color: {COLORS['sidebar_bg']};
        color: {COLORS['text_primary']};
        border: none;
        outline: none;
        show-decoration-selected: 1;
    }}
    
    QTreeView::item {{
        padding: 4px;
        border-radius: 4px;
    }}
    
    QTreeView::item:hover {{
        background-color: {COLORS['sidebar_hover']};
    }}
    
    QTreeView::item:selected {{
        background-color: {COLORS['sidebar_selected']};
        color: {COLORS['text_highlight']};
    }}
    
    QTreeView::branch {{
        background-color: transparent;
    }}
    
    QTreeView::branch:has-children:!has-siblings:closed,
    QTreeView::branch:closed:has-children:has-siblings {{
        image: url(none);
        border-image: none;
    }}
    
    QTreeView::branch:open:has-children:!has-siblings,
    QTreeView::branch:open:has-children:has-siblings {{
        image: url(none);
        border-image: none;
    }}
    
    /* ===== COMBO BOX ===== */
    QComboBox {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 10px;
        min-width: 100px;
    }}
    
    QComboBox:hover {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border_light']};
    }}
    
    QComboBox:focus {{
        border: 1px solid {COLORS['border_focus']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        selection-background-color: {COLORS['bg_tertiary']};
        outline: none;
    }}
    
    /* ===== LABELS ===== */
    QLabel {{
        background-color: transparent;
        color: {COLORS['text_primary']};
    }}
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {{
        background-color: {COLORS['border']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 1px;
    }}
    
    QSplitter::handle:vertical {{
        height: 1px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['accent_blue']};
    }}
    
    /* ===== STATUS BAR ===== */
    QStatusBar {{
        background-color: {COLORS['statusbar_bg']};
        color: {COLORS['statusbar_text']};
        border-top: 1px solid {COLORS['border']};
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    /* ===== DIALOG ===== */
    QDialog {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
    }}
    
    QDialogButtonBox QPushButton {{
        min-width: 80px;
    }}
    
    /* ===== MESSAGE BOX ===== */
    QMessageBox {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
    }}
    
    QMessageBox QPushButton {{
        min-width: 80px;
        padding: 6px 16px;
    }}
    
    /* ===== CHECKBOX ===== */
    QCheckBox {{
        color: {COLORS['text_primary']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {COLORS['border']};
        border-radius: 3px;
        background-color: {COLORS['bg_tertiary']};
    }}
    
    QCheckBox::indicator:hover {{
        border: 1px solid {COLORS['border_light']};
        background-color: {COLORS['bg_elevated']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['accent_blue']};
        border: 1px solid {COLORS['accent_blue']};
    }}
    
    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {COLORS['bg_elevated']};
        color: {COLORS['text_highlight']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px 8px;
    }}
    """


def get_light_stylesheet():
    """Get light theme stylesheet (VS Code Light)"""
    light_colors = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f3f3f3',
        'bg_tertiary': '#e8e8e8',
        'bg_elevated': '#d4d4d4',
        'text_primary': '#3b3b3b',
        'text_secondary': '#6c6c6c',
        'text_highlight': '#000000',
        'accent_blue': '#007acc',
        'border': '#d4d4d4',
        'editor_bg': '#ffffff',
        'editor_selection': '#add6ff',
    }
    return get_stylesheet()
