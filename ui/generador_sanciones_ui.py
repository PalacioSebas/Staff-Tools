from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QComboBox, QTextEdit,
                               QGroupBox, QWidget, QMessageBox, QListView)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication
import sys
import os
import json
from core.theme_manager import theme_manager


class GeneradorSancionesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generador de Sanciones - Minecraft Staff Tools")
        self.setFixedSize(600, 750)
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.config_file = os.path.join(app_dir, "core", "sanciones_config.json")
        self.cargar_config()        
        self.crear_ui()
    
    def cargar_config(self):
        """Carga la configuración desde JSON."""
        if not os.path.exists(self.config_file):
            QMessageBox.critical(
                self, 
                "Error de Configuración",
                f"No se encontró el archivo de configuración:\n{self.config_file}\n\n"
                "Por favor, asegúrate de que el archivo 'sanciones_config.json' existe en la carpeta 'core'."
            )
            self.tiempos_por_motivo = {}
            self.sanciones_config = {}
            self.modalidades = []
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.tiempos_por_motivo = config.get("tiempos_por_motivo", {})
                self.sanciones_config = config.get("sanciones_config", {})
                self.modalidades = config.get("modalidades", [])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de Configuración", 
                f"Error al leer el archivo de configuración:\n{e}"
            )
            self.tiempos_por_motivo = {}
            self.sanciones_config = {}
            self.modalidades = []
    
    def guardar_config(self):
        """Guarda la configuración actual en JSON."""
        try:
            config = {
                "tiempos_por_motivo": self.tiempos_por_motivo,
                "sanciones_config": self.sanciones_config,
                "modalidades": self.modalidades
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar config de sanciones: {e}")
    
    def closeEvent(self, event):
        """Guardar al cerrar la ventana."""
        self.guardar_config()
        event.accept()
    
    def _configurar_combobox(self, combo):
        """Configura un QComboBox con estilos que fuerzan texto negro en el dropdown."""
        list_view = QListView()
        list_view.setStyleSheet("""
            QListView {
                background-color: white;
                color: black;
                selection-background-color: #2196F3;
                selection-color: white;
                outline: none;
                border: 1px solid #ccc;
            }
            QListView::item {
                color: black;
                padding: 5px;
                min-height: 25px;
            }
            QListView::item:hover {
                background-color: #e3f2fd;
                color: black;
            }
            QListView::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        combo.setView(list_view)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                color: {theme_manager.get_text_color()};
            }}
            QComboBox:hover {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {theme_manager.get_text_color()};
                margin-right: 5px;
            }}
        """)
    
    def crear_ui(self):
        self.setStyleSheet(theme_manager.get_background_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        titulo = QLabel("⚖️ Generador de Comandos de Sanción")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        layout.addWidget(titulo)

        #Tipo de Sanción
        grupo_sancion = QGroupBox("📋 Tipo de Sanción")
        grupo_sancion.setFont(QFont("Segoe UI", 10, QFont.Bold))
        grupo_sancion.setStyleSheet(f"QGroupBox {{ color: {theme_manager.get_text_color()}; background: transparent; }}")
        layout_sancion = QVBoxLayout(grupo_sancion)
        
        self.tipo_sancion = QComboBox()
        self.tipo_sancion.addItems(list(self.sanciones_config.keys()))
        self.tipo_sancion.setFont(QFont("Segoe UI", 10))
        self._configurar_combobox(self.tipo_sancion)
        self.tipo_sancion.currentTextChanged.connect(self.on_sancion_change)
        layout_sancion.addWidget(self.tipo_sancion)
        
        layout.addWidget(grupo_sancion)

        #Nickname
        grupo_nick = QGroupBox("👤 Nickname del Jugador")
        grupo_nick.setFont(QFont("Segoe UI", 10, QFont.Bold))
        grupo_nick.setStyleSheet(f"QGroupBox {{ color: {theme_manager.get_text_color()}; background: transparent; }}")
        layout_nick = QVBoxLayout(grupo_nick)
        
        self.entry_nick = QLineEdit()
        self.entry_nick.setPlaceholderText("Ej: AboGames")
        self.entry_nick.setFont(QFont("Segoe UI", 10))
        self.entry_nick.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                color: {theme_manager.get_text_color()};
            }}
            QLineEdit:focus {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        self.entry_nick.textChanged.connect(self.generar_comando)
        layout_nick.addWidget(self.entry_nick)
        
        layout.addWidget(grupo_nick)

        #Tiempo (condicional)
        self.grupo_tiempo = QGroupBox("⏱️ Tiempo de Sanción")
        self.grupo_tiempo.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.grupo_tiempo.setStyleSheet(f"QGroupBox {{ color: {theme_manager.get_text_color()}; background: transparent; }}")
        layout_tiempo = QVBoxLayout(self.grupo_tiempo)
        
        tiempo_layout = QHBoxLayout()
        
        self.entry_tiempo = QLineEdit()
        self.entry_tiempo.setFont(QFont("Segoe UI", 10))
        self.entry_tiempo.setMaximumWidth(100)
        self.entry_tiempo.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                color: {theme_manager.get_text_color()};
            }}
            QLineEdit:focus {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        self.entry_tiempo.textChanged.connect(self.generar_comando)
        tiempo_layout.addWidget(self.entry_tiempo)
        
        lbl_hint = QLabel("(Formato: 1h = 1 hora | 7d = 7 días)")
        lbl_hint.setFont(QFont("Segoe UI", 9))
        lbl_hint.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.7)}; background: transparent;")
        tiempo_layout.addWidget(lbl_hint)
        tiempo_layout.addStretch()
        
        layout_tiempo.addLayout(tiempo_layout)
        
        layout.addWidget(self.grupo_tiempo)
        self.grupo_tiempo.hide()

        #Motivo
        grupo_motivo = QGroupBox("📝 Motivo")
        grupo_motivo.setFont(QFont("Segoe UI", 10, QFont.Bold))
        grupo_motivo.setStyleSheet(f"QGroupBox {{ color: {theme_manager.get_text_color()}; background: transparent; }}")
        layout_motivo = QVBoxLayout(grupo_motivo)
        
        self.motivo_combo = QComboBox()
        self.motivo_combo.setFont(QFont("Segoe UI", 10))
        self._configurar_combobox(self.motivo_combo)
        self.motivo_combo.currentTextChanged.connect(self.on_motivo_change)
        layout_motivo.addWidget(self.motivo_combo)
        
        lbl_custom = QLabel("O escribe un motivo personalizado:")
        lbl_custom.setFont(QFont("Segoe UI", 9))
        lbl_custom.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.8)}; background: transparent;")
        layout_motivo.addWidget(lbl_custom)
        
        self.entry_motivo_custom = QLineEdit()
        self.entry_motivo_custom.setPlaceholderText("Motivo personalizado...")
        self.entry_motivo_custom.setFont(QFont("Segoe UI", 10))
        self.entry_motivo_custom.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 5px;
                color: {theme_manager.get_text_color()};
            }}
            QLineEdit:focus {{
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        self.entry_motivo_custom.textChanged.connect(self.generar_comando)
        layout_motivo.addWidget(self.entry_motivo_custom)
        
        layout.addWidget(grupo_motivo)
        
        #Modalidad (condicional)
        self.grupo_modalidad = QGroupBox("🎮 Modalidad/Servidor")
        self.grupo_modalidad.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.grupo_modalidad.setStyleSheet(f"QGroupBox {{ color: {theme_manager.get_text_color()}; background: transparent; }}")
        layout_modalidad = QVBoxLayout(self.grupo_modalidad)
        
        self.modalidad_combo = QComboBox()
        # Primero las modalidades, Global al final
        self.modalidad_combo.addItems(self.modalidades)
        self.modalidad_combo.addItem("Global")
        self.modalidad_combo.setFont(QFont("Segoe UI", 10))
        self._configurar_combobox(self.modalidad_combo)
        self.modalidad_combo.currentTextChanged.connect(self.generar_comando)
        layout_modalidad.addWidget(self.modalidad_combo)
        
        layout.addWidget(self.grupo_modalidad)
        self.grupo_modalidad.hide()

        #Comando Generado
        grupo_comando = QGroupBox("💻 Comando Generado")
        grupo_comando.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout_comando = QVBoxLayout(grupo_comando)
        
        self.text_comando = QTextEdit()
        self.text_comando.setMaximumHeight(80)
        self.text_comando.setFont(QFont("Consolas", 11))
        self.text_comando.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #00ff00;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.text_comando.setReadOnly(True)
        layout_comando.addWidget(self.text_comando)
        
        layout.addWidget(grupo_comando)

        #Botones
        botones_layout = QHBoxLayout()
        
        btn_generar = QPushButton("🔄 Generar Comando")
        btn_generar.setMinimumHeight(40)
        btn_generar.setCursor(Qt.PointingHandCursor)
        btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_generar.clicked.connect(self.generar_comando)
        botones_layout.addWidget(btn_generar)
        
        btn_copiar = QPushButton("📋 Copiar")
        btn_copiar.setMinimumHeight(40)
        btn_copiar.setCursor(Qt.PointingHandCursor)
        btn_copiar.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        btn_copiar.clicked.connect(self.copiar_comando)
        botones_layout.addWidget(btn_copiar)
        
        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.setMinimumHeight(40)
        btn_limpiar.setCursor(Qt.PointingHandCursor)
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_limpiar.clicked.connect(self.limpiar_campos)
        botones_layout.addWidget(btn_limpiar)
        
        layout.addLayout(botones_layout)
    
    def on_motivo_change(self, motivo):
        """Actualiza la visibilidad de modalidad según el motivo seleccionado."""
        if not motivo:
            return
        
        tipo = self.tipo_sancion.currentText()
        if not tipo:
            return
        
        config = self.sanciones_config[tipo]
        if motivo in self.tiempos_por_motivo:
            self.entry_tiempo.setText(self.tiempos_por_motivo[motivo])
        motivos_modalidad = config.get("motivos_requieren_modalidad", {})
        
        if motivo in motivos_modalidad and motivos_modalidad[motivo]:
            self.modalidad_combo.setCurrentText("SurvivalClasico")
            self.grupo_modalidad.show()
        else:
            self.grupo_modalidad.hide()
        self.generar_comando()
    
    def on_sancion_change(self, tipo):
        """Actualiza campos según el tipo de sanción seleccionado."""
        if not tipo:
            return

        config = self.sanciones_config[tipo]
        if config["requiere_tiempo"]:
            self.grupo_tiempo.show()
            self.entry_tiempo.setText(config.get("tiempo_default", ""))
        else:
            self.grupo_tiempo.hide()
        self.motivo_combo.clear()
        self.motivo_combo.addItems(config["motivos"])
        if config["motivos"]:
            primer_motivo = config["motivos"][0]
            motivos_modalidad = config.get("motivos_requieren_modalidad", {})
            
            if primer_motivo in motivos_modalidad and motivos_modalidad[primer_motivo]:
                self.modalidad_combo.setCurrentText("SurvivalClasico")
                self.grupo_modalidad.show()
            else:
                self.grupo_modalidad.hide()
        self.generar_comando()
    
    def generar_comando(self):
        """Genera el comando de sanción sin mostrar errores."""
        tipo = self.tipo_sancion.currentText()
        if not tipo:
            return

        nick = self.entry_nick.text().strip()
        if not nick:
            return

        config = self.sanciones_config[tipo]
        motivo_custom = self.entry_motivo_custom.text().strip()
        motivo = motivo_custom if motivo_custom else self.motivo_combo.currentText()

        if not motivo:
            return
        comando = f"/{config['comando']} {nick}"
        if config["requiere_tiempo"]:
            tiempo = self.entry_tiempo.text().strip()
            if not tiempo:
                return
            comando += f" {tiempo}"
        comando += f" {motivo}"
        if self.grupo_modalidad.isVisible():
            modalidad = self.modalidad_combo.currentText()
            if modalidad != "Global":
                comando += f" server:{modalidad}"
        self.text_comando.setPlainText(comando)
    
    def copiar_comando(self):
        """Copia el comando al portapapeles."""
        comando = self.text_comando.toPlainText().strip()
        if not comando:
            QMessageBox.warning(self, "Advertencia", "Genera un comando primero")
            return

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(comando)

        self.mostrar_tooltip("✓ Comando copiado")
    
    def mostrar_tooltip(self, mensaje):
        """Muestra un tooltip temporal."""
        tooltip = QLabel(mensaje, self)
        tooltip.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 5px;
            }
        """)
        tooltip.setAlignment(Qt.AlignCenter)
        x = self.width() - 200
        y = 50
        tooltip.setGeometry(x, y, 180, 40)
        tooltip.show()
        QTimer.singleShot(1000, tooltip.deleteLater)
    
    def limpiar_campos(self):
        """Limpia todos los campos."""
        self.tipo_sancion.setCurrentIndex(-1)
        self.entry_nick.clear()
        self.entry_tiempo.clear()
        self.motivo_combo.setCurrentIndex(-1)
        self.entry_motivo_custom.clear()
        self.modalidad_combo.setCurrentText("Global")
        self.text_comando.clear()
        self.grupo_tiempo.hide()
        self.grupo_modalidad.hide()
