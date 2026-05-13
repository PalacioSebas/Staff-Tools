"""
Gestor de temas para la aplicación
Maneja la carga y guardado de preferencias de color e integra el easter egg de fondo.
"""
import json
import os
import sys
class ThemeManager:
    """Gestiona los temas de color de la aplicación y el easter egg de imagen."""
    def __init__(self):
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      
        self.config_file = os.path.join(app_dir, "core", "theme_config.json")
        self.easter_egg_image_path = os.path.join(os.path.dirname(__file__), "tu_foto_con_filtro.png")
        self.themes = {
            "Púrpura Violeta": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)",
                "emoji": "🌌"
            },
            "Océano Azul": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2193b0, stop:1 #6dd5ed)",
                "emoji": "🌊"
            },
            "Fuego Naranja": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f857a6, stop:1 #ff5858)",
                "emoji": "🔥"
            },
            "Verde Menta": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #56ab2f, stop:1 #a8e063)",
                "emoji": "🌿"
            },
            "Atardecer": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff6b6b, stop:1 #feca57)",
                "emoji": "🌅"
            },
            "Arcoíris": {
                "gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fa709a, stop:0.5 #fee140, stop:1 #30cfd0)",
                "emoji": "🌈"
            },
        }
        
        # Cargar configuración
        config = self.load_config()
        self.current_theme = config["theme"]
        self.text_color_dark = config["text_dark"]
        self.observers = []
        self.easter_egg_active = False #Indica si la imagen de fondo está activa
        self.click_count = 0           #Contador de clics del botón "proximamente!""
    
    def load_config(self):
        """Carga el tema y configuración de color de texto desde el archivo."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme_name = config.get("theme", "Púrpura Violeta")
                    text_dark = config.get("text_dark", False)
                    
                    if theme_name in self.themes:
                        return {"theme": theme_name, "text_dark": text_dark}
        except:
            pass
        
        return {"theme": "Púrpura Violeta", "text_dark": False}
    

    def register_window(self, window):
        """Registra una ventana para recibir actualizaciones de tema."""
        if window not in self.observers:
            self.observers.append(window)

    def unregister_window(self, window):
        """Desregistra una ventana."""
        if window in self.observers:
            self.observers.remove(window)

    def notify_all(self):
        """Notifica a todas las ventanas registradas que apliquen el tema."""
        for window in self.observers[:]:  # copia para evitar problemas si se modifica
            try:
                window.aplicar_tema()
            except RuntimeError:
                # La ventana fue destruida, la removemos
                self.observers.remove(window)
    def save_config(self, theme_name=None, text_dark=None):
        """Guarda el tema y color de texto seleccionado."""
        try:
            if theme_name is not None:
                self.current_theme = theme_name
            if text_dark is not None:
                self.text_color_dark = text_dark
            
            config = {
                "theme": self.current_theme,
                "text_dark": self.text_color_dark
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error al guardar tema: {e}")
            return False
    
    def get_current_gradient(self):
        """Obtiene el gradiente del tema actual."""
        return self.themes[self.current_theme]["gradient"]
    
    def get_theme_list(self):
        """Obtiene la lista de temas disponibles."""
        return [(name, data["emoji"]) for name, data in self.themes.items()]
    
    def get_text_color(self):
        """Obtiene el color de texto actual."""
        return "black" if self.text_color_dark else "white"
    
    def get_text_alpha(self, alpha=1.0):
        """Obtiene el color de texto con alpha específico."""
        if self.text_color_dark:
            return f"rgba(0, 0, 0, {alpha})"
        else:
            return f"rgba(255, 255, 255, {alpha})"
    
    def activar_easter_egg(self, ruta_imagen):
        """Activa el fondo de imagen personalizado y guarda la ruta."""
        import os
        if os.path.exists(ruta_imagen):
            self.easter_egg_active = True
            self.easter_egg_image_path = ruta_imagen.replace("\\", "/")
            return True
        return False
    
    def get_background_style(self):
        if self.easter_egg_active:
            image_path_css = self.easter_egg_image_path.replace('\\', '/')
            return f"""
                QWidget#centralWidget {{
                    border-image: url('{image_path_css}') 0 0 0 0 stretch stretch;
                }}
            """
        
        return f"""
            QWidget#centralWidget {{
                background: {self.get_current_gradient()};
            }}
        """
        
    def get_button_style(self):
        """Genera el estilo CSS para los botones (sin propiedades web incompatibles)."""
        text_color = self.get_text_color()
        # Se elimina backdrop-filter porque Qt no lo soporta en QSS.
        return f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 10px;
                color: {text_color};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """

    # --- NUEVO: MANEJADOR DE CLICS DEL BOTÓN ---
    def on_proximamente_clicked(self, window):
        """Maneja los clics en el botón 'Proximamente' para activar/desactivar el easter egg."""
        self.click_count += 1
        if self.click_count < 3:
            return
        elif self.click_count == 3:
            self.easter_egg_active = True
            window.setStyleSheet(self.get_background_style())
        elif self.click_count == 4:
            self.easter_egg_active = False
            self.click_count = 0
            window.setStyleSheet(self.get_background_style())

    
    
# Instancia global del gestor de temas
theme_manager = ThemeManager()

