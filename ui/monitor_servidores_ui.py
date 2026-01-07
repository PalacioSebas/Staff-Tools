from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QScrollArea, QWidget, QFrame,
                               QMessageBox, QInputDialog, QListWidget)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QCoreApplication
from PySide6.QtGui import QFont, QClipboard, QGuiApplication
import sys
import os
import json
from core.monitor_servidor import MonitorServidor
from core.theme_manager import theme_manager


class ServerCheckThread(QThread):
    """Thread para verificar un servidor sin bloquear la UI."""
    finished = Signal(dict, dict)
    
    def __init__(self, nombre, monitor, widgets):
        super().__init__()
        self.nombre = nombre
        self.monitor = monitor
        self.widgets = widgets
        
    def run(self):
        estado = self.monitor.verificar()
        self.finished.emit(estado, self.widgets)


class MonitorServidoresWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Monitor de Servidores - Minecraft Staff Tools")
        self.setFixedSize(700, 650)
        
        # Archivo de configuración
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.config_file = os.path.join(app_dir, "core", "monitor_config.json")
        self.servidores = self.cargar_config()
        
        self.monitores = {}
        self.auto_refresh = True
        self.threads = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.verificar_todos)
        
        self.crear_ui()
        self.actualizar_servidores()
        self.timer.start(5000)
        
    def cargar_config(self):
        """Carga la configuración desde el archivo JSON."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    from collections import OrderedDict
                    config = json.load(f, object_pairs_hook=OrderedDict)
                    servidores = config.get("servidores", self.servidores_por_defecto())
                    return dict(servidores)
        except:
            pass
        
        return self.servidores_por_defecto()
    
    def servidores_por_defecto(self):
        """Retorna la lista de servidores por defecto."""
        return {
            "Staff": "staff.minelatino.com",
            "Horus": "play.horusmc.net",
            "BG 3": "bg3.minelatino.com",
            "BG 4": "bg4.minelatino.com",
            "BG 5": "bg5.minelatino.com"
        }

    def guardar_config(self):
        """Guarda la configuración en el archivo JSON."""
        try:
            config = {"servidores": self.servidores}
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar config: {e}")
    
    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana."""
        self.guardar_config()
        self.timer.stop()
        for thread in self.threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        event.accept()
    
    def crear_ui(self):
        self.setStyleSheet(theme_manager.get_background_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        titulo = QLabel("🌐 Monitor de Servidores")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        layout.addWidget(titulo)
        
        controles_layout = QHBoxLayout()
        
        btn_refrescar = QPushButton("🔄 Refrescar Ahora")
        btn_refrescar.setMinimumHeight(35)
        btn_refrescar.setCursor(Qt.PointingHandCursor)
        btn_refrescar.setStyleSheet(theme_manager.get_button_style())
        btn_refrescar.clicked.connect(self.refrescar_manual)
        controles_layout.addWidget(btn_refrescar)
        
        btn_agregar = QPushButton("➕ Agregar Servidor")
        btn_agregar.setMinimumHeight(35)
        btn_agregar.setCursor(Qt.PointingHandCursor)
        btn_agregar.setStyleSheet(theme_manager.get_button_style())
        btn_agregar.clicked.connect(self.agregar_servidor)
        controles_layout.addWidget(btn_agregar)
        
        btn_eliminar = QPushButton("❌ Eliminar Servidor")
        btn_eliminar.setMinimumHeight(35)
        btn_eliminar.setCursor(Qt.PointingHandCursor)
        btn_eliminar.setStyleSheet(theme_manager.get_button_style())
        btn_eliminar.clicked.connect(self.eliminar_servidor)
        controles_layout.addWidget(btn_eliminar)

        lbl_refresh = QLabel("⏱️ Auto-refresh: 5s")
        lbl_refresh.setStyleSheet(f"color: {theme_manager.get_text_alpha(0.8)}; background: transparent;")
        controles_layout.addWidget(lbl_refresh)
        
        layout.addLayout(controles_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll)
        
        #Tip
        tip = QLabel("💡 Tip: Haz click en cualquier servidor para copiar su IP")
        tip.setFont(QFont("Segoe UI", 8))
        tip.setStyleSheet(f"color: {theme_manager.get_text_color()}; background: transparent;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)
    
    def crear_card_servidor(self, nombre, ip):
        """Crea una tarjeta visual para un servidor."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setLineWidth(1)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setSpacing(10)

        #Botones de flechas (izquierda)
        flechas_layout = QVBoxLayout()
        flechas_layout.setSpacing(2)
        
        btn_subir = QPushButton("▲")
        btn_subir.setFixedSize(25, 25)
        btn_subir.setCursor(Qt.PointingHandCursor)
        btn_subir.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        btn_subir.clicked.connect(lambda: self.mover_servidor_arriba(nombre))
        flechas_layout.addWidget(btn_subir)
        
        btn_bajar = QPushButton("▼")
        btn_bajar.setFixedSize(25, 25)
        btn_bajar.setCursor(Qt.PointingHandCursor)
        btn_bajar.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 3px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        btn_bajar.clicked.connect(lambda: self.mover_servidor_abajo(nombre))
        flechas_layout.addWidget(btn_bajar)
        
        card_layout.addLayout(flechas_layout)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        #Nombre del servidor
        lbl_nombre = QLabel(f"🖥️ {nombre}")
        lbl_nombre.setFont(QFont("Segoe UI", 11, QFont.Bold))
        info_layout.addWidget(lbl_nombre)
        
        #IP (clickeable para copiar)
        lbl_ip = QLabel(ip)
        lbl_ip.setStyleSheet("color: gray;")
        lbl_ip.setCursor(Qt.PointingHandCursor)
        lbl_ip.mousePressEvent = lambda event: self.copiar_ip(ip, card)
        info_layout.addWidget(lbl_ip)
        
        #Info frame
        status_layout = QHBoxLayout()
        
        #Estado
        lbl_estado = QLabel("⚪ Verificando...")
        status_layout.addWidget(lbl_estado)
        
        #Ping
        lbl_ping = QLabel("📶 -- ms")
        status_layout.addWidget(lbl_ping)
        
        #Jugadores
        lbl_jugadores = QLabel("👥 --/--")
        status_layout.addWidget(lbl_jugadores)
        
        status_layout.addStretch()
        info_layout.addLayout(status_layout)
        
        card_layout.addLayout(info_layout, 1)
        
        return {
            "card": card,
            "estado": lbl_estado,
            "ping": lbl_ping,
            "jugadores": lbl_jugadores
        }
    
    def copiar_ip(self, ip, card):
        """Copia la IP al portapapeles y muestra feedback."""
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(ip)
        original_style = card.styleSheet()
        card.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        QTimer.singleShot(200, lambda: card.setStyleSheet(original_style))
        
        # Mostrar tooltip
        self.mostrar_tooltip(f"✓ Copiado: {ip}")
    
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
    
    def actualizar_servidores(self):
        """Actualiza la visualización de todos los servidores."""
        timer_estaba_activo = self.timer.isActive()
        if timer_estaba_activo:
            self.timer.stop()
        
        for thread in self.threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        self.threads = []
        
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        QCoreApplication.processEvents()
        
        self.monitores = {}
        for nombre, ip in self.servidores.items():
            monitor = MonitorServidor(ip)
            card_widgets = self.crear_card_servidor(nombre, ip)
            
            self.scroll_layout.addWidget(card_widgets["card"])
            
            self.monitores[nombre] = {
                "monitor": monitor,
                "widgets": card_widgets
            }
        
        if timer_estaba_activo:
            self.timer.start(5000)
        
        self.verificar_todos()
    
    def verificar_todos(self):
        """Verifica el estado de todos los servidores en paralelo."""
        self.threads = [t for t in self.threads if t.isRunning()]
        
        for nombre, data in self.monitores.items():
            thread = ServerCheckThread(nombre, data["monitor"], data["widgets"])
            thread.finished.connect(self.actualizar_ui_servidor)
            thread.start()
            self.threads.append(thread)
    
    def actualizar_ui_servidor(self, estado, widgets):
        """Actualiza la UI de un servidor con su estado."""
        if estado["online"]:
            widgets["estado"].setText("🟢 Online")
            widgets["estado"].setStyleSheet("color: green;")
            
            # Mostrar latencia
            if estado['latencia'] == "?":
                widgets["ping"].setText("📶 ~ ms")
                widgets["ping"].setStyleSheet("color: orange;")
            else:
                widgets["ping"].setText(f"📶 {estado['latencia']} ms")
                widgets["ping"].setStyleSheet("color: black;")
            
            # Mostrar jugadores
            widgets["jugadores"].setText(f"👥 {estado['jugadores']}")
            widgets["jugadores"].setStyleSheet("color: black;")
            
            # Si tiene nota de Query OFF
            if estado.get("error") == "Query OFF":
                widgets["estado"].setText("🟡 Online (ping)")
                widgets["estado"].setStyleSheet("color: orange;")
        else:
            widgets["estado"].setText("🔴 Offline")
            widgets["estado"].setStyleSheet("color: red;")
            widgets["ping"].setText("📶 -- ms")
            widgets["ping"].setStyleSheet("color: gray;")
            widgets["jugadores"].setText("👥 --/--")
            widgets["jugadores"].setStyleSheet("color: gray;")
            
            if estado["error"]:
                error_text = estado["error"]
                if "Sin respuesta" in error_text:
                    error_text = "Sin respuesta"
                elif "Puerto cerrado" in error_text:
                    error_text = "Puerto cerrado"
                
                widgets["estado"].setText(f"🔴 {error_text}")
    
    def refrescar_manual(self):
        """Refresca manualmente todos los servidores."""
        self.verificar_todos()
    
    def agregar_servidor(self):
        """Agrega un nuevo servidor a monitorear."""
        nombre, ok = QInputDialog.getText(
            self,
            "Agregar Servidor",
            "Nombre del servidor:"
        )
        
        if not ok or not nombre:
            return
        
        if nombre in self.servidores:
            QMessageBox.warning(self, "Advertencia", f"'{nombre}' ya existe")
            return
        
        ip, ok = QInputDialog.getText(
            self,
            "Agregar Servidor",
            f"IP de '{nombre}':"
        )
        
        if not ok or not ip:
            return
        
        self.servidores[nombre] = ip
        self.guardar_config()
        self.actualizar_servidores()
        QMessageBox.information(self, "Éxito", f"Servidor '{nombre}' agregado")
    
    def eliminar_servidor(self):
        """Elimina un servidor del monitor."""
        if not self.servidores:
            QMessageBox.warning(self, "Advertencia", "No hay servidores para eliminar")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Eliminar Servidor")
        dialog.setFixedSize(350, 300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Selecciona el servidor a eliminar:")
        label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(label)
        
        #Lista de servidores
        lista = QListWidget()
        lista.addItems(self.servidores.keys())
        layout.addWidget(lista)

        btn_layout = QHBoxLayout()
        
        btn_eliminar = QPushButton("❌ Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        
        def confirmar_eliminar():
            item = lista.currentItem()
            if not item:
                QMessageBox.warning(dialog, "Advertencia", "Selecciona un servidor")
                return
            
            nombre = item.text()
            respuesta = QMessageBox.question(
                dialog,
                "Confirmar",
                f"¿Eliminar '{nombre}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                del self.servidores[nombre]
                self.guardar_config()
                self.actualizar_servidores()
                dialog.close()
                QMessageBox.information(self, "Éxito", f"Servidor '{nombre}' eliminado")
        
        btn_eliminar.clicked.connect(confirmar_eliminar)
        btn_layout.addWidget(btn_eliminar)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #757575; }
        """)
        btn_cancelar.clicked.connect(dialog.close)
        btn_layout.addWidget(btn_cancelar)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def mover_servidor_arriba(self, nombre):
        """Mueve un servidor una posición hacia arriba."""
        keys = list(self.servidores.keys())
        index = keys.index(nombre)
        
        if index == 0:
            return
        keys[index], keys[index - 1] = keys[index - 1], keys[index]
        
        nuevo_orden = {k: self.servidores[k] for k in keys}
        self.servidores = nuevo_orden
        
        self.guardar_config()
        self.actualizar_servidores()
    
    def mover_servidor_abajo(self, nombre):
        """Mueve un servidor una posición hacia abajo."""
        keys = list(self.servidores.keys())
        index = keys.index(nombre)
        
        if index == len(keys) - 1:
            return
        
        keys[index], keys[index + 1] = keys[index + 1], keys[index]
        
        nuevo_orden = {k: self.servidores[k] for k in keys}
        self.servidores = nuevo_orden
        
        self.guardar_config()
        self.actualizar_servidores()
