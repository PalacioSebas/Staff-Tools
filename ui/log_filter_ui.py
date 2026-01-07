from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                               QLineEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os
import sys
from core.filtro_logs import FiltroLogs
from core.theme_manager import theme_manager


class LogFilterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtro de Logs")
        self.setFixedSize(500, 300)
        
        self.archivo_log = None
        
        self.crear_ui()
        
    def crear_ui(self):
        self.setStyleSheet(theme_manager.get_background_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        titulo = QLabel("Filtro de Logs de Minecraft")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        layout.addWidget(titulo)       
        layout.addSpacing(10)

        btn_archivo = QPushButton("Seleccionar archivo de log")
        btn_archivo.setMinimumHeight(35)
        btn_archivo.setCursor(Qt.PointingHandCursor)
        btn_archivo.setStyleSheet(theme_manager.get_button_style())
        btn_archivo.clicked.connect(self.seleccionar_archivo)
        layout.addWidget(btn_archivo)

        self.lbl_archivo = QLabel("Ningún archivo seleccionado")
        self.lbl_archivo.setAlignment(Qt.AlignCenter)
        self.lbl_archivo.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.8)}; background: transparent;")
        layout.addWidget(self.lbl_archivo)
        
        layout.addSpacing(15)

        lbl_jugadores = QLabel("Jugadores (separados por coma)")
        lbl_jugadores.setAlignment(Qt.AlignCenter)
        lbl_jugadores.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        layout.addWidget(lbl_jugadores)

        self.entry_jugadores = QLineEdit()
        self.entry_jugadores.setPlaceholderText("Ej: AboGames, Rollmaster_")
        self.entry_jugadores.setMinimumHeight(30)
        self.entry_jugadores.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                color: {theme_manager.get_text_color()};
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        layout.addWidget(self.entry_jugadores)
        
        layout.addSpacing(10)
        btn_filtrar = QPushButton("Filtrar Logs")
        btn_filtrar.setMinimumHeight(40)
        btn_filtrar.setCursor(Qt.PointingHandCursor)
        btn_filtrar.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(76, 175, 80, 0.8);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: {theme_manager.get_text_color()};
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: rgba(76, 175, 80, 1);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        btn_filtrar.clicked.connect(self.ejecutar_filtro)
        layout.addWidget(btn_filtrar)
        
    def seleccionar_archivo(self):
        """Abre diálogo para seleccionar archivo de log."""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar log",
            "",
            "Logs (*.log *.txt);;Todos los archivos (*)"
        )
        
        if archivo:
            self.archivo_log = archivo
            self.lbl_archivo.setText(os.path.basename(archivo))
            self.lbl_archivo.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent; font-weight: bold;")
            
    def ejecutar_filtro(self):
        """Ejecuta el filtrado de logs."""
        if not self.archivo_log:
            QMessageBox.critical(self, "Error", "Seleccioná un archivo de log")
            return
            
        jugadores_raw = self.entry_jugadores.text().strip()
        if not jugadores_raw:
            QMessageBox.critical(self, "Error", "Ingresá al menos un jugador")
            return
            
        jugadores = [j.strip() for j in jugadores_raw.split(",") if j.strip()]
        filtro = FiltroLogs(self.archivo_log)
        filtro.filtrar_por_jugadores(jugadores)
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        output_dir = os.path.join(app_dir, "LOGS Filtrados")
        os.makedirs(output_dir, exist_ok=True)
        
        nombre_salida = f"filtrado_{'_'.join(jugadores)}.txt"
        salida = os.path.join(output_dir, nombre_salida)
        
        try:
            filtro.guardar_resultados(salida, incluir_stats=True, jugadores=jugadores)
            
            QMessageBox.information(
                self,
                "Proceso completado",
                f"Líneas encontradas: {len(filtro.lineas_filtradas)}\n\n"
                f"Archivo generado:\n{nombre_salida}\n\n"
                f"Ubicación:\n{output_dir}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No se pudo guardar el archivo:\n{str(e)}"
            )
