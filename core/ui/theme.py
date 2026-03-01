"""
Design System and Theming Module for PyCursor IDE.
Defines the visual language, color palettes, and global stylesheets for both dark and light modes.
Standardizes UI components using Catppuccin-inspired Mocha (Dark) and Latte (Light) palettes.
"""

# Dark Theme Palette (Mocha)
MOCHA_DARK_COLORS = {
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

# Dark Theme Palette (Lexor Nova Dark)
LEXOR_NOVA_DARK_COLORS = {
    # --- Base Background Layers ---
    'bg_primary': '#151821',      # Main background (deep graphite)
    'bg_secondary': '#1B1F2A',    # Panels / Sidebar / Terminal
    'bg_tertiary': '#10131A',     # Deep surfaces (Titlebar)
    'bg_elevated': '#232838',     # Cards / Elevated panels
    'bg_selection': '#2F3650',    # Selection highlights
    'bg_input': '#11151D',        

    # --- Typography ---
    'text_primary': '#E6EAF2',    # High contrast main text
    'text_secondary': '#A9B1C6',  
    'text_tertiary': '#6E7891',   
    'text_disabled': '#5B6378',   
    'text_highlight': '#FFFFFF',

    # --- Accents (More vivid & modern) ---
    'accent_blue': '#5DA9FF',     # Action / Primary accent
    'accent_purple': '#A78BFA',   # AI / Smart features
    'accent_green': '#4ADE80',    # Success
    'accent_orange': '#F59E0B',   # Warning
    'accent_red': '#F43F5E',      # Error
    'accent_yellow': '#FACC15',   # Info / Highlight

    # --- Borders ---
    'border': '#2A3142',
    'border_light': '#343C52',
    'border_focus': '#5DA9FF',

    # --- Buttons ---
    'button_bg': '#232838',
    'button_hover': '#2C3347',
    'button_pressed': '#1A1F2C',
    'button_active': '#1A1F2C',

    # --- Tabs ---
    'tab_active_bg': '#151821',
    'tab_inactive_bg': '#1B1F2A',
    'tab_hover_bg': '#1E2432',

    # --- Status Bar ---
    'statusbar_bg': '#5DA9FF',
    'statusbar_text': '#0F172A',

    # --- Editor ---
    'editor_bg': '#151821',
    'editor_line_bg': '#1B1F2A',
    'editor_selection': '#2F3650',
    'editor_cursor': '#FFDD57',

    # --- Sidebar ---
    'sidebar_bg': '#1B1F2A',
    'sidebar_hover': '#232838',
    'sidebar_selected': '#2C3347',
}

# Light Theme Palette (Lexor Nova Light)
LEXOR_NOVA_LIGHT_COLORS = {
    # --- Base Background Layers ---
    'bg_primary': '#F7F9FC',      # Soft white
    'bg_secondary': '#EEF2F8',
    'bg_tertiary': '#E4E9F2',
    'bg_elevated': '#FFFFFF',
    'bg_selection': '#DCE4F5',
    'bg_input': '#FFFFFF',

    # --- Typography ---
    'text_primary': '#1F2937',    
    'text_secondary': '#4B5563',
    'text_tertiary': '#9AA3B2',
    'text_disabled': '#B0B8C5',
    'text_highlight': '#2563EB',

    # --- Accents ---
    'accent_blue': '#2563EB',
    'accent_purple': '#7C3AED',
    'accent_green': '#16A34A',
    'accent_orange': '#EA580C',
    'accent_red': '#DC2626',
    'accent_yellow': '#D97706',

    # --- Borders ---
    'border': '#E2E8F0',
    'border_light': '#CBD5E1',
    'border_focus': '#2563EB',

    # --- Buttons ---
    'button_bg': '#E4E9F2',
    'button_hover': '#DCE4F5',
    'button_pressed': '#F7F9FC',
    'button_active': '#F7F9FC',

    # --- Tabs ---
    'tab_active_bg': '#FFFFFF',
    'tab_inactive_bg': '#EEF2F8',
    'tab_hover_bg': '#F2F6FC',

    # --- Status Bar ---
    'statusbar_bg': '#2563EB',
    'statusbar_text': '#FFFFFF',

    # --- Editor ---
    'editor_bg': '#F7F9FC',
    'editor_line_bg': '#EEF2F8',
    'editor_selection': '#DCE4F5',
    'editor_cursor': '#F59E0B',

    # --- Sidebar ---
    'sidebar_bg': '#EEF2F8',
    'sidebar_hover': '#E4E9F2',
    'sidebar_selected': '#DCE4F5',
}

# Midnight Navy Theme (Lexor Abyss)
LEXOR_ABYSS_COLORS = {
    # --- Base Layers ---
    'bg_primary': '#0B1220',      # Deep navy
    'bg_secondary': '#0F172A',    # Panels
    'bg_tertiary': '#0A0F1C',     # Title / deeper surfaces
    'bg_elevated': '#162033',     # Cards / elevated
    'bg_selection': '#1E293B',    
    'bg_input': '#0E1626',

    # --- Typography ---
    'text_primary': '#E2E8F0',
    'text_secondary': '#94A3B8',
    'text_tertiary': '#64748B',
    'text_disabled': '#475569',
    'text_highlight': '#FFFFFF',

    # --- Accents ---
    'accent_blue': '#3B82F6',     # Crisp royal blue
    'accent_purple': '#8B5CF6',
    'accent_green': '#22C55E',
    'accent_orange': '#F97316',
    'accent_red': '#EF4444',
    'accent_yellow': '#EAB308',

    # --- Borders ---
    'border': '#1E293B',
    'border_light': '#273449',
    'border_focus': '#3B82F6',

    # --- Buttons ---
    'button_bg': '#162033',
    'button_hover': '#1E293B',
    'button_pressed': '#0F172A',
    'button_active': '#0F172A',

    # --- Tabs ---
    'tab_active_bg': '#0B1220',
    'tab_inactive_bg': '#0F172A',
    'tab_hover_bg': '#162033',

    # --- Status Bar ---
    'statusbar_bg': '#3B82F6',
    'statusbar_text': '#0B1220',

    # --- Editor ---
    'editor_bg': '#0B1220',
    'editor_line_bg': '#0F172A',
    'editor_selection': '#1E293B',
    'editor_cursor': '#FACC15',

    # --- Sidebar ---
    'sidebar_bg': '#0F172A',
    'sidebar_hover': '#162033',
    'sidebar_selected': '#1E293B',
}

# Cyberpunk Theme (Lexor Neon Grid)
LEXOR_NEON_GRID_COLORS = {
    # --- Base Layers ---
    'bg_primary': '#0A0A0F',      
    'bg_secondary': '#11111A',
    'bg_tertiary': '#07070C',
    'bg_elevated': '#1A1A26',
    'bg_selection': '#222233',
    'bg_input': '#0D0D14',

    # --- Typography ---
    'text_primary': '#E5E7EB',
    'text_secondary': '#9CA3AF',
    'text_tertiary': '#6B7280',
    'text_disabled': '#4B5563',
    'text_highlight': '#FFFFFF',

    # --- Neon Accents ---
    'accent_blue': '#00E5FF',     # Neon cyan
    'accent_purple': '#FF00FF',   # Hot magenta
    'accent_green': '#00FF9F',    
    'accent_orange': '#FF7A00',
    'accent_red': '#FF0055',
    'accent_yellow': '#FFE600',

    # --- Borders ---
    'border': '#1F1F2E',
    'border_light': '#2B2B3C',
    'border_focus': '#00E5FF',

    # --- Buttons ---
    'button_bg': '#1A1A26',
    'button_hover': '#222233',
    'button_pressed': '#11111A',
    'button_active': '#11111A',

    # --- Tabs ---
    'tab_active_bg': '#0A0A0F',
    'tab_inactive_bg': '#11111A',
    'tab_hover_bg': '#1A1A26',

    # --- Status Bar ---
    'statusbar_bg': '#00E5FF',
    'statusbar_text': '#0A0A0F',

    # --- Editor ---
    'editor_bg': '#0A0A0F',
    'editor_line_bg': '#11111A',
    'editor_selection': '#222233',
    'editor_cursor': '#FF00FF',

    # --- Sidebar ---
    'sidebar_bg': '#11111A',
    'sidebar_hover': '#1A1A26',
    'sidebar_selected': '#222233',
}

# Nord-Inspired Minimal Theme (Lexor Arctic)
LEXOR_ARCTIC_COLORS = {
    # --- Base Layers ---
    'bg_primary': '#2E3440',
    'bg_secondary': '#3B4252',
    'bg_tertiary': '#2B303B',
    'bg_elevated': '#434C5E',
    'bg_selection': '#4C566A',
    'bg_input': '#2E3440',

    # --- Typography ---
    'text_primary': '#ECEFF4',
    'text_secondary': '#D8DEE9',
    'text_tertiary': '#A3AFC2',
    'text_disabled': '#7B88A1',
    'text_highlight': '#88C0D0',

    # --- Muted Accents ---
    'accent_blue': '#81A1C1',
    'accent_purple': '#B48EAD',
    'accent_green': '#A3BE8C',
    'accent_orange': '#D08770',
    'accent_red': '#BF616A',
    'accent_yellow': '#EBCB8B',

    # --- Borders ---
    'border': '#4C566A',
    'border_light': '#5E6A7E',
    'border_focus': '#88C0D0',

    # --- Buttons ---
    'button_bg': '#434C5E',
    'button_hover': '#4C566A',
    'button_pressed': '#3B4252',
    'button_active': '#3B4252',

    # --- Tabs ---
    'tab_active_bg': '#2E3440',
    'tab_inactive_bg': '#3B4252',
    'tab_hover_bg': '#434C5E',

    # --- Status Bar ---
    'statusbar_bg': '#81A1C1',
    'statusbar_text': '#2E3440',

    # --- Editor ---
    'editor_bg': '#2E3440',
    'editor_line_bg': '#3B4252',
    'editor_selection': '#4C566A',
    'editor_cursor': '#EBCB8B',

    # --- Sidebar ---
    'sidebar_bg': '#3B4252',
    'sidebar_hover': '#434C5E',
    'sidebar_selected': '#4C566A',
}

# Theme Registry
THEMES = {
    'dark': {'name': 'Mocha Dark', 'palette': MOCHA_DARK_COLORS},
    'light': {'name': 'Mocha Light', 'palette': LIGHT_COLORS},
    'lexor_nova_dark': {'name': 'Lexor Nova Dark', 'palette': LEXOR_NOVA_DARK_COLORS},
    'lexor_nova_light': {'name': 'Lexor Nova Light', 'palette': LEXOR_NOVA_LIGHT_COLORS},
    'lexor_abyss': {'name': 'Lexor Abyss', 'palette': LEXOR_ABYSS_COLORS},
    'lexor_neon_grid': {'name': 'Lexor Neon Grid', 'palette': LEXOR_NEON_GRID_COLORS},
    'lexor_arctic': {'name': 'Lexor Arctic', 'palette': LEXOR_ARCTIC_COLORS},
}

# Backward compatibility aliases
COLORS = MOCHA_DARK_COLORS

def get_color(color_name, theme='dark'):
    """
    Retrieves a specific color from the current theme palette.
    """
    theme_info = THEMES.get(theme, THEMES['dark'])
    palette = theme_info['palette']
    return palette.get(color_name, '#ffffff')

def get_icon_color(theme='dark'):
    """
    Returns the standard color for UI icons in the current theme.
    """
    from PyQt6.QtGui import QColor
    color_hex = get_color('text_secondary', theme)
    return QColor(color_hex)

# Caching system to prevent redundant processing of stylesheets
_STYLESHEET_CACHE = {}

def get_stylesheet(theme='dark'):
    """
    Generates the comprehensive application-wide Qt Stylesheet (QSS).
    Loads the template from style.qss and performs tag substitution using the theme palette.
    """
    global _STYLESHEET_CACHE
    if theme in _STYLESHEET_CACHE:
        return _STYLESHEET_CACHE[theme]

    from core.utilities.utils import get_asset_path
    template_path = get_asset_path("themes", "style.qss")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            qss = f.read()
            
        theme_info = THEMES.get(theme, THEMES['dark'])
        theme_colors = theme_info['palette']
        
        for key, value in theme_colors.items():
            qss = qss.replace(f"@{key}", value)
            
        _STYLESHEET_CACHE[theme] = qss
        return qss
    except Exception as e:
        print(f"[Theme Error] Failed to load stylesheet: {e}")
        return ""
