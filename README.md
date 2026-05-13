# Minecraft Staff Tools v1.2 - PySide6

Versión migrada a PySide6 para mejor personalización y rendimiento.

## 📦 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python run.py
```

## 📁 Estructura del Proyecto

```
minecraft-staff-tools-pyside6/
├── run.py                          # Punto de entrada
├── requirements.txt                # Dependencias
├── ui/
│   ├── __init__.py
│   ├── main_app.py                 # Ventana principal
│   ├── log_filter_ui.py            # Filtro de logs
│   ├── monitor_servidores_ui.py    # Monitor de servidores
│   └── generador_sanciones_ui.py   # Generador de sanciones
└── core/
    ├── __init__.py
    ├── filtro_logs.py              # Lógica de filtrado
    └── monitor_servidor.py         # Lógica de monitoreo
```

## ✨ Mejoras de PySide6

- ✅ Estilos CSS nativos más potentes
- ✅ Mejor manejo de threading con QThread
- ✅ High DPI support automático
- ✅ Tooltips y animaciones nativas
- ✅ Mejor arquitectura con Signals/Slots

## 🔧 Generar Ejecutable

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name "MinecraftStaffTools" run.py
```

El .exe estará en `dist/MinecraftStaffTools.exe`

## 🆕 Cambios vs v1.1

- Se agregó opción de filtrado de logs con detección de tpakill automatizada
- se agrego Easter Egg de Abo therian
- se corrigió la interfaz gráfica para hacerla más adaptable a modificaciones futuras
- corrección de textos cortados
