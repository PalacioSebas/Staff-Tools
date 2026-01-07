"""
Módulo de filtrado de logs de Minecraft
Integrado con la interfaz gráfica de Staff Tools
"""

import re
from collections import Counter


FRASES_IGNORADAS = [
    "¡Que bien me queda el LATAM+!",
    "Inicia sesión usando /login",
    "Ignoring player info update for unknown player",
    "Failed to retrieve profile key pair",
    "do head request",
    "textures",
    "RequestMetadata",
]

PATRONES_IGNORADOS = [
    r"\[Render thread/WARN\]: Ignoring player info update",
    r"\[Download-\d+/ERROR\]: Failed to retrieve",
    r"do head request ->",
    r"textures '.*' was added",
]


class FiltroLogs:
    """Clase para filtrar logs de Minecraft por jugadores."""
    
    def __init__(self, archivo_log):
        self.archivo_log = archivo_log
        self.lineas_filtradas = []
        self.lineas_ignoradas = 0
    
    def debe_ignorar_linea(self, linea):
        """Verifica si una línea contiene frases o patrones ignorados."""
        for frase in FRASES_IGNORADAS:
            if frase in linea:
                return True
        
        for patron in PATRONES_IGNORADOS:
            if re.search(patron, linea):
                return True
        
        return False
    
    def extraer_timestamp(self, linea):
        """Extrae el timestamp de una línea del log."""
        match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]', linea)
        return match.group(1) if match else None
    
    def filtrar_por_jugadores(self, jugadores, case_sensitive=False):
        """Filtra líneas que contienen nombres de jugadores."""
        self.lineas_filtradas = []
        self.lineas_ignoradas = 0
        
        with open(self.archivo_log, 'r', encoding='utf-8', errors='ignore') as f:
            for linea in f:
                linea_limpia = linea.rstrip('\n\r')
                
                encontrado = False
                if case_sensitive:
                    encontrado = any(jugador in linea_limpia for jugador in jugadores)
                else:
                    encontrado = any(jugador.lower() in linea_limpia.lower() for jugador in jugadores)
                
                if encontrado:
                    if self.debe_ignorar_linea(linea_limpia):
                        self.lineas_ignoradas += 1
                        continue
                    
                    self.lineas_filtradas.append(linea_limpia)
        
        return self.lineas_filtradas
    
    def filtrar_por_tiempo(self, hora_inicio=None, hora_fin=None):
        """Filtra las líneas por rango de tiempo."""
        if not hora_inicio and not hora_fin:
            return self.lineas_filtradas
        
        lineas_en_rango = []
        for linea in self.lineas_filtradas:
            timestamp = self.extraer_timestamp(linea)
            if timestamp:
                if hora_inicio and timestamp < hora_inicio:
                    continue
                if hora_fin and timestamp > hora_fin:
                    continue
                lineas_en_rango.append(linea)
        
        self.lineas_filtradas = lineas_en_rango
        return lineas_en_rango
    
    def obtener_estadisticas(self, jugadores):
        """Genera estadísticas sobre las menciones de jugadores."""
        stats = {jugador: 0 for jugador in jugadores}
        tipos_mensaje = Counter()
        
        for linea in self.lineas_filtradas:
            for jugador in jugadores:
                if jugador.lower() in linea.lower():
                    stats[jugador] += 1
            
            if "[CHAT]" in linea:
                if any(f"[{tag}]" in linea for tag in ["LATAM+", "BoSS", "U"]):
                    tipos_mensaje["Mensaje de chat"] += 1
                elif "se ha conectado" in linea or "acaba de unirse" in linea:
                    tipos_mensaje["Conexión"] += 1
                elif "Entrando a la zona" in linea or "Saliendo de la zona" in linea:
                    tipos_mensaje["Movimiento de zona"] += 1
                else:
                    tipos_mensaje["Sistema"] += 1
        
        return stats, tipos_mensaje
    
    def guardar_resultados(self, archivo_salida, incluir_stats=True, jugadores=None):
        """Guarda los resultados en un archivo."""
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            if incluir_stats and jugadores:
                stats, tipos = self.obtener_estadisticas(jugadores)
                
                f.write("="*80 + "\n")
                f.write("ESTADÍSTICAS DE FILTRADO\n")
                f.write("="*80 + "\n\n")
                
                f.write("Menciones por jugador:\n")
                for jugador, count in stats.items():
                    f.write(f"  • {jugador}: {count} líneas\n")
                
                f.write("\nTipos de mensajes:\n")
                for tipo, count in tipos.most_common():
                    f.write(f"  • {tipo}: {count}\n")
                
                if self.lineas_ignoradas > 0:
                    f.write(f"\n⚠️  Líneas ignoradas (basura del servidor): {self.lineas_ignoradas}\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write(f"TOTAL: {len(self.lineas_filtradas)} líneas encontradas\n")
                f.write("="*80 + "\n\n")
            
            for linea in self.lineas_filtradas:
                f.write(linea + '\n')
