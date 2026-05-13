"""
Módulo de filtrado de logs de Minecraft
Integrado con la interfaz gráfica de Staff Tools
"""

import re
from collections import Counter
from datetime import datetime, timedelta

FRASES_IGNORADAS = [
    "¡Que bien me queda el LATAM+!",
    "Inicia sesión usando /login",
    "Ignoring player info update for unknown player",
    "Failed to retrieve profile key pair",
    "do head request",
    "textures",
    "RequestMetadata",
    "acaba de votar por el"
]

PATRONES_IGNORADOS = [
    r"\[Render thread/WARN\]: Ignoring player info update",
    r"\[Download-\d+/ERROR\]: Failed to retrieve",
    r"do head request ->",
    r"textures '.*' was added",
]


KEYWORDS_TPA_PEDIDO = [
    "ha pedido teletransportarse",
    "ha sido enviada a"
]

KEYWORDS_TPA_ACEPTADO = [
    "de teletransporte aceptada",
    "ha aceptado tu teletransportaci"
]

KEYWORDS_TPA_INFO = [
    "escribe /tpaccept",
    "para denegar la",
    "la solicitud ser"
]

KEYWORDS_MUERTE = [
    "fue asesinado",
    "muri",
    "slain",
    "burnt",
    "fell out of the world",
    "se quem",
    "explot", 
    "ctima de",
    "ha explotado por",
    "ha tirado a",
    "desde muy alto"
]

KEYWORDS_TPAKILL = [
    "teletransporte",
    "murió",
    "slain",
    "burnt",
    "se cayó al vacío",
    "se quemó",
    "explotó"
]


class FiltroLogs:
    """Clase para filtrar logs de Minecraft por jugadores."""
    
    def __init__(self, archivo_log):
        self.archivo_log = archivo_log
        self.lineas_filtradas = []
        self.lineas_ignoradas = 0
        self.tpakills_detectados = 0
        self.modo_tpakill_activo = False
        self.regex_ignorados = re.compile('|'.join(PATRONES_IGNORADOS)) if PATRONES_IGNORADOS else None
    
    def debe_ignorar_linea(self, linea):
        """Verifica si una línea contiene frases o patrones ignorados."""
        for frase in FRASES_IGNORADAS:
            if frase in linea:
                return True
        
        for patron in PATRONES_IGNORADOS:
            if re.search(patron, linea):
                return True
        
        return False
    
    def extraer_datetime(self, linea):
            """Extrae el timestamp [HH:MM:SS] y lo convierte en objeto datetime."""
            match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]', linea)
            if match:
                # Usamos strptime para convertir el texto en tiempo real
                return datetime.strptime(match.group(1), "%H:%M:%S")
            return None

    def extraer_timestamp(self, linea):
        """Extrae el timestamp de una línea del log."""
        match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]', linea)
        return match.group(1) if match else None
    
    def filtrar_por_jugadores(self, jugadores, case_sensitive=False, modo_tpakill=False):
        self.lineas_filtradas = []
        self.lineas_ignoradas = 0
        self.tpakills_detectados = 0
        self.modo_tpakill_activo = modo_tpakill
        
        jugadores_lower = [j.lower() for j in jugadores]
        ultimo_tpa_time = None
        idx_inicio_tpa = 0
        buffer_tpa = [] 
        
        with open(self.archivo_log, 'r', encoding='utf-8', errors='ignore') as f:
            for linea in f:
                linea_limpia = linea.rstrip('\n\r')
                linea_lower = linea_limpia.lower()
                
                encontrado_jugador = False
                if case_sensitive:
                    encontrado_jugador = any(jugador in linea_limpia for jugador in jugadores)
                else:
                    encontrado_jugador = any(jugador in linea_lower for jugador in jugadores_lower)
                
                #Detección de tpakill
                if modo_tpakill and "[chat]" in linea_lower:
                    es_pedido = any(kw in linea_lower for kw in KEYWORDS_TPA_PEDIDO)
                    es_aceptado = any(kw in linea_lower for kw in KEYWORDS_TPA_ACEPTADO)
                    es_info = any(kw in linea_lower for kw in KEYWORDS_TPA_INFO)
                    es_muerte = any(kw in linea_lower for kw in KEYWORDS_MUERTE) and encontrado_jugador
                    
                    hora_actual = self.extraer_datetime(linea_limpia)
                    

                    if es_pedido and hora_actual:                       #Alguien PIDE un TPA
                        ultimo_tpa_time = hora_actual
                        tpa_aceptado = False
                        idx_inicio_tpa = len(self.lineas_filtradas)

                        if not self.debe_ignorar_linea(linea_limpia) and linea_limpia not in self.lineas_filtradas:
                            self.lineas_filtradas.append(linea_limpia)
                        continue
                    elif es_aceptado and ultimo_tpa_time:               #El jugador ACEPTA el TPA
                        tpa_aceptado = True
                        if not self.debe_ignorar_linea(linea_limpia) and linea_limpia not in self.lineas_filtradas:
                            self.lineas_filtradas.append(linea_limpia)
                        continue
                    elif es_info:
                        if not self.debe_ignorar_linea(linea_limpia) and linea_limpia not in self.lineas_filtradas:
                            self.lineas_filtradas.append(linea_limpia)
                        continue
                    elif es_muerte and hora_actual and ultimo_tpa_time: #Hay muerte
                        if tpa_aceptado:
                            if hora_actual < ultimo_tpa_time:
                                hora_actual += timedelta(days=1)
                                
                            diferencia = hora_actual - ultimo_tpa_time
                            
                            if diferencia <= timedelta(minutes=3):
                                self.tpakills_detectados += 1
                                self.lineas_filtradas.insert(idx_inicio_tpa, "")
                                self.lineas_filtradas.insert(idx_inicio_tpa + 1, ">>>>>>>>>> ⚠️ ALERTA: POSIBLE TPAKILL DETECTADO ⚠️ <<<<<<<<<<")
                                if not self.debe_ignorar_linea(linea_limpia):
                                    self.lineas_filtradas.append(linea_limpia)
                                self.lineas_filtradas.append(">>>>>>>>>> ------------------------------------------------ <<<<<<<<<<")
                                self.lineas_filtradas.append("")
                                ultimo_tpa_time = None
                                tpa_aceptado = False
                                continue
                        ultimo_tpa_time = None
                        tpa_aceptado = False
                        
                        # Guardamos la muerte normalmente si era del jugador
                        if encontrado_jugador and not self.debe_ignorar_linea(linea_limpia):
                            self.lineas_filtradas.append(linea_limpia)
                        continue

                    elif es_muerte and hora_actual and ultimo_tpa_time:
                        if hora_actual < ultimo_tpa_time:
                            hora_actual += timedelta(days=1)                            
                        diferencia = hora_actual - ultimo_tpa_time
                        if diferencia <= timedelta(minutes=3):
                            self.tpakills_detectados += 1

                            #Marcador visual
                            self.lineas_filtradas.append("")
                            self.lineas_filtradas.append(">>>>>>>>>> ⚠️ ALERTA: POSIBLE TPAKILL DETECTADO AQUÍ ⚠️ <<<<<<<<<<")
                            
                            for linea_tpa in buffer_tpa:
                                if linea_tpa not in self.lineas_filtradas and not self.debe_ignorar_linea(linea_tpa):
                                    self.lineas_filtradas.append(linea_tpa)
                            buffer_tpa.clear() 
                            
                            if not self.debe_ignorar_linea(linea_limpia):
                                self.lineas_filtradas.append(linea_limpia)
                            self.lineas_filtradas.append(">>>>>>>>>> ------------------------------------------------ <<<<<<<<<<")
                            self.lineas_filtradas.append("")
                            ultimo_tpa_time = None
                            
                        else:
                            ultimo_tpa_time = None
                            buffer_tpa.clear()
                            
                            if encontrado_jugador and not self.debe_ignorar_linea(linea_limpia):
                                self.lineas_filtradas.append(linea_limpia)
                        continue

                if encontrado_jugador:
                    if self.debe_ignorar_linea(linea_limpia):
                        self.lineas_ignoradas += 1
                        continue
                    
                    if linea_limpia not in self.lineas_filtradas:
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
                
                # --- NUEVO: VEREDICTO DE TPAKILL ---
                if self.modo_tpakill_activo:
                    f.write("🔍 ESTADO DE INVESTIGACIÓN TPAKILL:\n")
                    if self.tpakills_detectados > 0:
                        f.write(f"  [⚠️ ALERTA] Se detectaron {self.tpakills_detectados} posible(s) caso(s) de TPAKILL.\n")
                        f.write("             (Muerte registrada en menos de 3 minutos tras un TPA)\n\n")
                    else:
                        f.write("  [✅ LIMPIO] El sistema no considera TPAKILL (Por favor revisa manualmente ♡).\n")
                        f.write("             (No hubo muertes dentro de los 3 minutos posteriores a un TPA)\n\n")

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