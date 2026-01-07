#!/usr/bin/env python3
"""
Minecraft Staff Tools
Punto de entrada principal de la aplicación
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_app import MinecraftStaffToolsApp


def main():
    """Función principal de la aplicación."""
    # Habilitar high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Estilo global de la aplicación
    app.setStyle("Fusion")
    
    # Crear y mostrar ventana principal
    window = MinecraftStaffToolsApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
