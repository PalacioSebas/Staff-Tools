from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QListWidget, QListWidgetItem, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.theme_manager import theme_manager


class ThemeDialog(QDialog):
    """Diálogo para seleccionar el tema de la aplicación."""
    
    theme_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración de Tema")
        self.setFixedSize(400, 500)
        
        self.crear_ui()
        
    def crear_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = QLabel("Selecciona tu tema favorito")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo
        subtitulo = QLabel("Los cambios se aplican inmediatamente")
        subtitulo.setFont(QFont("Segoe UI", 9))
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: gray;")
        layout.addWidget(subtitulo)
        
        # Lista de temas
        self.lista_temas = QListWidget()
        self.lista_temas.setFont(QFont("Segoe UI", 11))
        self.lista_temas.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        # Agregar temas a la lista
        temas = theme_manager.get_theme_list()
        for nombre, emoji in temas:
            item = QListWidgetItem(f"{emoji} {nombre}")
            item.setData(Qt.UserRole, nombre)
            self.lista_temas.addItem(item)
            if nombre == theme_manager.current_theme:
                item.setSelected(True)
                self.lista_temas.setCurrentItem(item)
        
        self.lista_temas.itemClicked.connect(self.preview_theme)
        layout.addWidget(self.lista_temas)
        
        #Switch de color de texto
        texto_layout = QHBoxLayout()
        
        lbl_texto = QLabel("Color de texto:")
        lbl_texto.setFont(QFont("Segoe UI", 10))
        texto_layout.addWidget(lbl_texto)
        
        self.check_texto_oscuro = QCheckBox("Texto Negro")
        self.check_texto_oscuro.setFont(QFont("Segoe UI", 10))
        self.check_texto_oscuro.setChecked(theme_manager.text_color_dark)
        self.check_texto_oscuro.setStyleSheet("""
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 3px;
                border: 2px solid #ddd;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
        """)
        self.check_texto_oscuro.stateChanged.connect(self.preview_theme)
        texto_layout.addWidget(self.check_texto_oscuro)
        
        texto_layout.addStretch()
        layout.addLayout(texto_layout)
        
        #Preview del gradiente
        self.preview_label = QLabel()
        self.preview_label.setFixedHeight(80)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.preview_label.setText("Vista Previa")
        self.actualizar_preview()
        layout.addWidget(self.preview_label)
        
        #Botones
        botones_layout = QHBoxLayout()
        
        btn_aplicar = QPushButton("✓ Aplicar")
        btn_aplicar.setMinimumHeight(40)
        btn_aplicar.setCursor(Qt.PointingHandCursor)
        btn_aplicar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_aplicar.clicked.connect(self.aplicar_tema)
        botones_layout.addWidget(btn_aplicar)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumHeight(40)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)
        
        layout.addLayout(botones_layout)
    
    def preview_theme(self, item):
        """Muestra preview del tema seleccionado."""
        self.actualizar_preview()
    
    def actualizar_preview(self):
        """Actualiza el preview con el tema y color de texto seleccionado."""
        item = self.lista_temas.currentItem()
        if item:
            nombre_tema = item.data(Qt.UserRole)
            gradient = theme_manager.themes[nombre_tema]["gradient"]
            texto_oscuro = self.check_texto_oscuro.isChecked()
            color_texto = "black" if texto_oscuro else "white"
            
            self.preview_label.setStyleSheet(f"""
                QLabel {{
                    background: {gradient};
                    border-radius: 8px;
                    color: {color_texto};
                    border: 2px solid #ddd;
                }}
            """)
    
    def aplicar_tema(self):
        """Aplica el tema y color de texto seleccionado."""
        item = self.lista_temas.currentItem()
        if item:
            nombre_tema = item.data(Qt.UserRole)
            texto_oscuro = self.check_texto_oscuro.isChecked()
            if theme_manager.save_config(theme_name=nombre_tema, text_dark=texto_oscuro):
                self.theme_changed.emit(nombre_tema)
                self.accept()
