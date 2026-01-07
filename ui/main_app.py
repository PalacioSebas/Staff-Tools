from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
import os
from ui.log_filter_ui import LogFilterWindow
from ui.monitor_servidores_ui import MonitorServidoresWindow
from ui.generador_sanciones_ui import GeneradorSancionesWindow
from ui.theme_dialog import ThemeDialog
from core.theme_manager import theme_manager


class MinecraftStaffToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Staff Tools")
        self.setFixedSize(500, 450)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        #ventanas abiertas
        self.filtro_window = None
        self.monitor_window = None
        self.generador_window = None
        
        self.crear_ui()
        
    def crear_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.aplicar_tema()
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QVBoxLayout()
        config_layout = QHBoxLayout()
        config_layout.addStretch()
        
        btn_config = QPushButton("⚙️")
        btn_config.setFixedSize(40, 40)
        btn_config.setCursor(Qt.PointingHandCursor)
        btn_config.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme_manager.get_text_color()};
                font-size: 20pt;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }}
        """)
        btn_config.clicked.connect(self.abrir_configuracion)
        config_layout.addWidget(btn_config)
        
        header_layout.addLayout(config_layout)
        
        # Título
        titulo = QLabel("Minecraft Staff Tools")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        header_layout.addWidget(titulo)

        subtitulo = QLabel("Herramientas para administración y soporte")
        subtitulo.setFont(QFont("Segoe UI", 10))
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.9)}; background: transparent;")
        header_layout.addWidget(subtitulo)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        self.crear_boton(layout, "🔍 Filtro de Logs", self.abrir_filtro_logs)
        self.crear_boton(layout, "🌐 Monitor de Servidores", self.abrir_monitor_servidores)
        self.crear_boton(layout, "⚖️ Generador de Sanciones", self.abrir_generador_sanciones)
        self.crear_boton(layout, "Proximamente!", self.no_disponible)
       
        layout.addStretch()
        
        footer = QLabel("Creado con ♡ por AboGames")
        footer.setFont(QFont("Segoe UI", 8))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.8)}; background: transparent;")
        layout.addWidget(footer)
    
    def aplicar_tema(self):
        """Aplica el tema actual desde el theme_manager."""
        central = self.centralWidget()
        if central:
            central.setStyleSheet(theme_manager.get_background_style())
        
    def crear_boton(self, layout, texto, callback):
        """Crea un botón estilizado."""
        btn = QPushButton(texto)
        btn.setFont(QFont("Segoe UI", 11))
        btn.setMinimumHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(theme_manager.get_button_style())
        
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        #Acciones de los botones  
    def abrir_filtro_logs(self):
        """Abre la ventana de filtro de logs o la trae al frente si ya está abierta."""
        if self.filtro_window is None or not self.filtro_window.isVisible():
            self.filtro_window = LogFilterWindow(self)
            self.filtro_window.show()
        else:
            self.filtro_window.raise_()
            self.filtro_window.activateWindow()
        
    def abrir_monitor_servidores(self):
        """Abre la ventana de monitor de servidores o la trae al frente si ya está abierta."""
        if self.monitor_window is None or not self.monitor_window.isVisible():
            self.monitor_window = MonitorServidoresWindow(self)
            self.monitor_window.show()
        else:
            self.monitor_window.raise_()
            self.monitor_window.activateWindow()
        
    def abrir_generador_sanciones(self):
        """Abre la ventana de generador de sanciones o la trae al frente si ya está abierta."""
        if self.generador_window is None or not self.generador_window.isVisible():
            self.generador_window = GeneradorSancionesWindow(self)
            self.generador_window.show()
        else:
            self.generador_window.raise_()
            self.generador_window.activateWindow()
    
    def abrir_configuracion(self):
        """Abre el diálogo de configuración de tema."""
        dialog = ThemeDialog(self)
        dialog.theme_changed.connect(self.on_theme_changed)
        dialog.exec()
    
    def on_theme_changed(self, theme_name):
        """Se ejecuta cuando el usuario cambia el tema."""
        self.aplicar_tema()
        QMessageBox.information(
            self,
            "Tema Actualizado",
            f"El tema '{theme_name}' se aplicará completamente al reiniciar la aplicación."
        )
        
    def no_disponible(self):
        """Mensaje para herramientas no disponibles."""
        QMessageBox.warning(
            self,
            "No disponible",
            "Esta herramienta todavía no está implementada."
        )
