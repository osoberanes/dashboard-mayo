"""
Herramienta para encontrar las coordenadas X,Y de los elementos
del SECO VPN Client en tu pantalla.

Instrucciones:
1. Abre SECO Client manualmente
2. Ejecuta: python calibrar_vpn.py
3. Mueve el mouse sobre cada elemento y anota las coordenadas
4. Escribe esas coordenadas en tu .env
"""

import pyautogui
import time

print("=" * 50)
print(" CALIBRADOR — SECO VPN Client")
print("=" * 50)
print()
print("Mueve el mouse sobre los elementos de SECO Client.")
print("Las coordenadas se actualizan en tiempo real.")
print("Presiona Ctrl+C para salir.")
print()

try:
    while True:
        x, y = pyautogui.position()
        print(f"\r  Mouse: X={x:4d}, Y={y:4d}   ", end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print(f"\n\nÚltima posición capturada: X={x}, Y={y}")
    print("\nFormato para .env:")
    print(f"  VPN_COORD_USUARIO={x},{y}   ← si estabas sobre el campo usuario")
    print(f"  VPN_COORD_PASSWORD={x},{y}  ← si estabas sobre el campo contraseña")
    print(f"  VPN_COORD_CONECTAR={x},{y}  ← si estabas sobre el botón conectar")
```

---

**Estructura final en Claude Code:**
```
sre_automation/
├── CLAUDE.md
├── automatizacion_sre.py
├── calibrar_vpn.py
├── .env.template
├── requirements.txt
└── .env              ← lo creas tú copiando .env.template