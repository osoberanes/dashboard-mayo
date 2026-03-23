# SRE Listas — Automatización diaria

## Propósito
Script que cada mañana:
1. Abre SECO VPN Client (GUI) y se conecta con credenciales
2. Abre Chrome con Playwright y hace login en consolacitas.sre.gob.mx
3. Navega al menú de listas, busca por fecha de hoy y descarga el Excel
4. Configura la Hoja 2 del Excel: landscape, todas las columnas en 1 página de ancho
5. Manda a imprimir a "Dell Printer Driver v2 XL"

## Stack
- Python (Windows)
- Playwright (Chrome) — automatización web
- PyAutoGUI — control GUI del SECO VPN Client
- openpyxl — configuración de página del Excel
- pywin32 (win32print / win32api) — impresión en Windows
- python-dotenv — manejo de credenciales

## Estructura del proyecto
```
sre_automation/
├── CLAUDE.md
├── automatizacion_sre.py   ← script principal
├── calibrar_vpn.py         ← herramienta para obtener coordenadas del SECO Client
├── .env.template           ← plantilla de credenciales (copiar como .env)
├── .env                    ← credenciales reales (NO subir a git)
└── requirements.txt
```

## Setup inicial
```bash
pip install -r requirements.txt
playwright install chromium
# Copiar .env.template como .env y llenar credenciales
# Ejecutar calibrar_vpn.py para obtener coordenadas del SECO Client
```

## Variables de entorno (.env)
| Variable | Descripción |
|---|---|
| VPN_USUARIO | Usuario del SECO VPN Client |
| VPN_PASSWORD | Contraseña del SECO VPN Client |
| SECO_EXE | Ruta completa al ejecutable de SECO Client |
| VPN_COORD_USUARIO | Coordenadas X,Y del campo usuario en SECO (calibrar) |
| VPN_COORD_PASSWORD | Coordenadas X,Y del campo contraseña en SECO (calibrar) |
| VPN_COORD_CONECTAR | Coordenadas X,Y del botón conectar en SECO (calibrar) |
| SRE_USUARIO | Usuario del sitio consolacitas.sre.gob.mx |
| SRE_PASSWORD | Contraseña del sitio consolacitas.sre.gob.mx |

## XPATHs del sitio (consolacitas.sre.gob.mx)
Todos definidos en el dict XPATH dentro de automatizacion_sre.py.
Si el sitio cambia de estructura, actualizar esos XPATHs.

## Impresión
- Impresora: "Dell Printer Driver v2 XL"
- Hoja: Hoja 2 (índice 1, worksheets[1])
- Orientación: landscape
- Ajuste: fitToWidth=1, fitToHeight=0
  → Todas las columnas en 1 página de ancho
  → Filas se extienden en las páginas que hagan falta

## Ejecución automática
Programar en Windows Task Scheduler:
- Programa: python
- Argumento: C:\ruta\completa\automatizacion_sre.py
- Disparador: Diariamente a la hora deseada (ej. 8:00 AM)

## Notas importantes
- headless=False durante pruebas → cambiar a True en producción
- calibrar_vpn.py debe correrse UNA vez con SECO Client abierto
- El .env NUNCA debe subirse a ningún repositorio
```

---

### 📄 `requirements.txt`
```
playwright
pywin32
pyautogui
python-dotenv
openpyxl
keyboard