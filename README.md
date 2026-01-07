# ⚒️ Minecraft Staff Tools

<p align="center">
  <img src="icon.png" alt="Staff Tools Logo" width="128" height="128">
</p>

<p align="center">
  <strong>Herramientas de administración para staff de servidores Minecraft</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/versión-1.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/plataforma-Windows-lightgrey.svg" alt="Platform">
</p>

---

## 📋 Descripción

**Minecraft Staff Tools** es una aplicación de escritorio diseñada para facilitar las tareas de administración y moderación en servidores de Minecraft. Proporciona una interfaz gráfica intuitiva con múltiples herramientas útiles para el staff.

---

## ✨ Características

### 🔍 Filtrador de Logs
- Filtra archivos de log por nickname de jugador
- Exporta resultados filtrados a archivos separados
- Soporta múltiples formatos de log de Minecraft

### 🌐 Monitor de Servidores
- Monitoreo en tiempo real del estado de servidores
- Muestra jugadores online, latencia y estado
- Auto-refresh cada 5 segundos
- Agregar/eliminar servidores personalizados
- Reordenar servidores con flechas
- Click para copiar IP al portapapeles

### ⚖️ Generador de Sanciones
- Genera comandos de sanción listos para usar
- Soporta: Kick, Warn, Mute, Ban, Ban IP, y más
- Tiempos preconfigurados por tipo de infracción
- Motivos personalizables
- Selector de modalidad/servidor
- Copiar comando al portapapeles con un click

### 🎨 Temas Personalizables
- 10 temas de colores disponibles
- Opción de texto claro/oscuro
- Vista previa en tiempo real
- Configuración persistente

---

## 🚀 Instalación

### Opción 1: Ejecutable (Recomendado)
1. Descarga `Minecraft Staff Tools v1.1.0.exe` desde [Releases](https://github.com/PalacioSebas/Staff-Tools/releases)
2. Coloca el ejecutable junto con la carpeta `core/` en el mismo directorio
3. ¡Ejecuta y listo!

### Opción 2: Desde el código fuente
```bash
# Clonar el repositorio
git clone https://github.com/PalacioSebas/Staff-Tools.git
cd Staff-Tools

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python run.py
```

---

## 📁 Estructura del Proyecto

```
Staff-Tools/
├── run.py                    # Punto de entrada de la aplicación
├── icon.png                  # Ícono de la aplicación
├── icon.ico                  # Ícono para el ejecutable
├── requirements.txt          # Dependencias de Python
├── README.md
│
├── core/                     # Lógica de negocio
│   ├── __init__.py
│   ├── filtro_logs.py        # Motor de filtrado de logs
│   ├── monitor_servidor.py   # Cliente de monitoreo de servidores
│   ├── theme_manager.py      # Gestor de temas
│   ├── sanciones_config.json # Configuración de sanciones
│   ├── monitor_config.json   # Configuración de servidores
│   ├── theme_config.json     # Configuración del tema
│   └── LOGS/                 # Carpeta para logs a filtrar
│
├── ui/                       # Interfaces gráficas
│   ├── main_app.py           # Menú principal
│   ├── log_filter_ui.py      # UI del filtrador de logs
│   ├── monitor_servidores_ui.py  # UI del monitor
│   ├── generador_sanciones_ui.py # UI del generador
│   └── theme_dialog.py       # Diálogo de selección de tema
│
└── LOGS Filtrados/           # Salida de logs filtrados
```

---

## ⚙️ Configuración

### Sanciones (`core/sanciones_config.json`)
Podés personalizar los tipos de sanciones, motivos, tiempos y modalidades editando este archivo JSON.

### Servidores (`core/monitor_config.json`)
Los servidores monitoreados se guardan automáticamente. También podés editarlos manualmente.

### Tema (`core/theme_config.json`)
```json
{
    "theme": "Púrpura Violeta",
    "text_dark": false
}
```

---

## 🎨 Temas Disponibles

| Tema | Descripción |
|------|-------------|
| 🌌 Púrpura Violeta | Gradiente púrpura (por defecto) |
| 🌊 Océano Azul | Tonos azules oceánicos |
| 🔥 Fuego Naranja | Gradiente cálido rojo-naranja |
| 🌿 Verde Menta | Tonos verdes frescos |
| 🌅 Atardecer | Rojo a amarillo |
| 🌃 Noche Oscura | Tema oscuro elegante |
| 🍇 Uva Morada | Púrpura intenso |
| 🌈 Arcoíris | Multicolor vibrante |
| 🎮 Gaming | Verde neón |
| 🌌 Galaxia | Púrpura a turquesa |

---

## 🛠️ Requisitos

- **Sistema Operativo:** Windows 10/11
- **Python:** 3.9 o superior (solo si ejecutás desde código)
- **Dependencias:** PySide6

---

## 📦 Compilar Ejecutable

Para generar tu propio ejecutable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Minecraft Staff Tools v1.1.0" --icon=icon.ico run.py
```

El ejecutable se generará en la carpeta `dist/`.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encontrás un bug o tenés una sugerencia:

1. Abrí un [Issue](https://github.com/PalacioSebas/Staff-Tools/issues)
2. O enviá un Pull Request

---

## 📝 Changelog

### v1.1.0
- ✅ Arreglo de visibilidad en dropdowns con texto blanco
- ✅ Tips ahora siguen el color del tema
- ✅ Código de sanciones movido completamente a JSON
- ✅ Limpieza general del código

### v1.0.0
- 🎉 Lanzamiento inicial
- ✨ Filtrador de logs
- ✨ Monitor de servidores
- ✨ Generador de sanciones
- ✨ Sistema de temas

---

## 👤 Autor

**PalacioSebas**

- GitHub: [@PalacioSebas](https://github.com/PalacioSebas)
- LinkedIn: [@PalacioSebas](https://www.linkedin.com/in/palaciosebas)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

<p align="center">
  Hecho con ❤️ para la comunidad de Minecraft
</p>
