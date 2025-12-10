from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTabWidget, QWidget, QMessageBox,
    QFormLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from core.ui.theme import COLORS
from core.ai.api_model_handler import APIModelHandler, APIConfig

class SettingsDialog(QDialog):
    def __init__(self, parent=None, api_handler=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(600, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: 5px;
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_highlight']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        
        self.api_handler = api_handler if api_handler else APIModelHandler()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        api_tab = QWidget()
        api_layout = QVBoxLayout()
        api_tab.setLayout(api_layout)
        
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Google Gemini"])
        self.provider_combo.currentTextChanged.connect(self.update_fields)
        provider_layout.addWidget(self.provider_combo)
        api_layout.addLayout(provider_layout)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter API Key or leave empty to use env var")
        key_layout.addWidget(self.api_key_input)
        api_layout.addLayout(key_layout)
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., gpt-4, claude-3-opus")
        model_layout.addWidget(self.model_input)
        api_layout.addLayout(model_layout)
        
        api_layout.addStretch()
        
        tabs.addTab(api_tab, "AI Configuration")
        
        # Keybindings tab
        keybindings_tab = QWidget()
        kb_layout = QVBoxLayout()
        kb_layout.setContentsMargins(20, 20, 20, 20)
        kb_layout.setSpacing(15)
        
        kb_label = QLabel("Customize keyboard shortcuts for PyCursor IDE")
        kb_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        kb_layout.addWidget(kb_label)
        
        kb_btn = QPushButton("Edit Keyboard Shortcuts")
        kb_btn.setMaximumWidth(200)
        kb_btn.clicked.connect(self.open_keybindings_dialog)
        kb_layout.addWidget(kb_btn)
        
        kb_layout.addStretch()
        keybindings_tab.setLayout(kb_layout)
        tabs.addTab(keybindings_tab, "Keybindings")
        
        general_tab = QWidget()
        gen_layout = QVBoxLayout()
        gen_layout.addWidget(QLabel("General settings coming soon..."))
        gen_layout.addStretch()
        general_tab.setLayout(gen_layout)
        tabs.addTab(general_tab, "General")
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        if self.api_handler.config:
            provider_map = {'openai': 'OpenAI', 'anthropic': 'Anthropic', 'gemini': 'Google Gemini'}
            current_provider = provider_map.get(self.api_handler.config.provider, 'OpenAI')
            self.provider_combo.setCurrentText(current_provider)
            self.model_input.setText(self.api_handler.config.model_name)
        else:
            self.update_fields(self.provider_combo.currentText())

    def update_fields(self, provider):
        pass

    def save_settings(self):
        provider = self.provider_combo.currentText().lower().split()[0]
        if provider == 'google': provider = 'gemini'
        if 'gemini' in self.provider_combo.currentText().lower():
            provider = 'gemini'
        
        api_key = self.api_key_input.text().strip()
        model = self.model_input.text().strip()
        
        success = self.api_handler.configure(
            provider=provider,
            api_key=api_key if api_key else None,
            model_name=model if model else None
        )
        
        if success:
            QMessageBox.information(self, "Success", f"Configured {provider} successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to configure API. Check logs.")
    
    def open_keybindings_dialog(self):
        """Open the keybindings editor dialog"""
        from core.ui.keybindings_dialog import KeybindingsDialog
        from core.utilities.keybindings import KeyBindingsManager
        
        keybindings_manager = KeyBindingsManager()
        dialog = KeybindingsDialog(self, keybindings_manager)
        dialog.exec()
