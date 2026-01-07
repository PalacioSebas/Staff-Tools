"""
Módulo de monitoreo de servidores Minecraft
Verifica estado, ping y jugadores online
"""

from mcstatus import JavaServer
import socket
import subprocess
import platform


class MonitorServidor:
    """Clase para monitorear servidores de Minecraft."""
    
    def __init__(self, ip, puerto=25565, timeout=3):
        self.ip = ip
        self.puerto = puerto
        self.timeout = timeout
        self.estado = {
            "online": False,
            "latencia": None,
            "jugadores": "0/0",
            "error": None
        }
    
    def ping_simple(self):
        """Ping simple como fallback."""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '-w', '2000', self.ip]
            startupinfo = None
            creationflags = 0
            if platform.system().lower() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=3,
                text=True,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            if result.returncode == 0:
                output = result.stdout
                if 'time=' in output or 'tiempo=' in output:
                    try:
                        if 'time=' in output:
                            time_str = output.split('time=')[1].split('ms')[0].strip()
                        else:
                            time_str = output.split('tiempo=')[1].split('ms')[0].strip()
                        ping_time = float(time_str)
                        return True, ping_time
                    except:
                        return True, None
                return True, None
            return False, None
        except:
            return False, None
    
    def verificar(self):
        """Verifica el estado del servidor."""
        try:
            server = JavaServer.lookup(f"{self.ip}:{self.puerto}", timeout=self.timeout)
            status = server.status()
            
            self.estado = {
                "online": True,
                "latencia": round(status.latency, 1),
                "jugadores": f"{status.players.online}/{status.players.max}",
                "error": None
            }
            return self.estado
            
        except socket.timeout:
            online, ping_time = self.ping_simple()
            if online:
                self.estado = {
                    "online": True,
                    "latencia": round(ping_time, 1) if ping_time else "?",
                    "jugadores": "?/?",
                    "error": "Query OFF"
                }
            else:
                self.estado = {
                    "online": False,
                    "latencia": None,
                    "jugadores": "0/0",
                    "error": "Sin respuesta"
                }
                
        except ConnectionRefusedError:
            online, ping_time = self.ping_simple()
            if online:
                self.estado = {
                    "online": True,
                    "latencia": round(ping_time, 1) if ping_time else "?",
                    "jugadores": "?/?",
                    "error": "Query OFF"
                }
            else:
                self.estado = {
                    "online": False,
                    "latencia": None,
                    "jugadores": "0/0",
                    "error": "Puerto cerrado"
                }
                
        except OSError:
            online, ping_time = self.ping_simple()
            if online:
                self.estado = {
                    "online": True,
                    "latencia": round(ping_time, 1) if ping_time else "?",
                    "jugadores": "?/?",
                    "error": "Query OFF"
                }
            else:
                self.estado = {
                    "online": False,
                    "latencia": None,
                    "jugadores": "0/0",
                    "error": "No alcanzable"
                }
                
        except Exception as e:
            online, ping_time = self.ping_simple()
            if online:
                self.estado = {
                    "online": True,
                    "latencia": round(ping_time, 1) if ping_time else "?",
                    "jugadores": "?/?",
                    "error": "Query OFF"
                }
            else:
                error_msg = str(e)[:20] if str(e) else type(e).__name__
                self.estado = {
                    "online": False,
                    "latencia": None,
                    "jugadores": "0/0",
                    "error": error_msg
                }
        
        return self.estado
    
    def obtener_estado(self):
        """Retorna el último estado verificado."""
        return self.estado
