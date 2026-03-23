"""
automatizacion_sre.py
Automatización de descarga e impresión de listas diarias
Sitio: consolacitas.sre.gob.mx
"""

import subprocess, time, os, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ── Cargar .env ──────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"ERROR: No se encontró .env en {env_path}")
    print("Copia .env.template como .env y llena tus credenciales.")
    sys.exit(1)
load_dotenv(env_path)

# ── Configuración ─────────────────────────────────────────
SECO_EXE     = os.getenv("SECO_EXE", r"C:\Program Files\SECO\SECOClient.exe")
VPN_USUARIO  = os.getenv("VPN_USUARIO")
VPN_PASSWORD = os.getenv("VPN_PASSWORD")

_u = os.getenv("VPN_COORD_USUARIO", "760,400").split(",")
_p = os.getenv("VPN_COORD_PASSWORD", "760,450").split(",")
_b = os.getenv("VPN_COORD_CONECTAR", "760,510").split(",")
VPN_COORD_USUARIO  = (int(_u[0]), int(_u[1]))
VPN_COORD_PASSWORD = (int(_p[0]), int(_p[1]))
VPN_COORD_CONECTAR = (int(_b[0]), int(_b[1]))

SRE_URL      = "https://consolacitas.sre.gob.mx/ingresar"
SRE_USUARIO  = os.getenv("SRE_USUARIO")
SRE_PASSWORD = os.getenv("SRE_PASSWORD")
IMPRESORA    = "Dell Printer Driver v2 XL"
DOWNLOAD_DIR = Path.home() / "Downloads" / "SRE_Listas"

# Validar credenciales
faltantes = [n for n, v in [
    ("VPN_USUARIO", VPN_USUARIO), ("VPN_PASSWORD", VPN_PASSWORD),
    ("SRE_USUARIO", SRE_USUARIO), ("SRE_PASSWORD", SRE_PASSWORD),
] if not v]
if faltantes:
    print(f"ERROR: Faltan en .env: {faltantes}")
    sys.exit(1)

# ── XPATHs ───────────────────────────────────────────────
XPATH = {
    "login_usuario"  : "/html/body/div[1]/div/div/div[2]/form/div[1]/div/div[1]/div/div/input",
    "login_password" : "/html/body/div[1]/div/div/div[2]/form/div[1]/div/div[2]/div/div/input",
    "login_boton"    : "/html/body/div[1]/div/div/div[2]/form/div[2]/div/div/div/button",
    "menu_listas"    : "/html/body/section/section/div/aside/ul/li/ul/li[2]",
    "abrir_busqueda" : "/html/body/section/section/main/div/div/section/div/div[3]/div[1]/div[2]/button",
    "campo_fecha"    : "/html/body/section/section/main/div/div/section/div/div[4]/div/div/section/div[2]/div[2]/div/input",
    "btn_buscar"     : "/html/body/section/section/main/div/div/section/div/div[4]/div/div/section/div[2]/div[8]/center/button",
    "btn_descargar"  : "/html/body/section/section/main/div/div/section/div/div[2]/div[2]/button[1]",
}


def seco_ya_corriendo():
    """Devuelve True si el proceso SecoClient.exe ya está en memoria."""
    result = subprocess.run(
        ['tasklist', '/fi', 'imagename eq SecoClient.exe'],
        capture_output=True, text=True
    )
    return 'SecoClient.exe' in result.stdout


def activar_vpn():
    import pyautogui
    pyautogui.FAILSAFE = True

    if seco_ya_corriendo():
        print("[VPN] SECO Client ya está corriendo — se asume conectado, continuando.")
        return

    if not os.path.exists(SECO_EXE):
        print(f"[VPN] ERROR: No se encontró SECO Client en: {SECO_EXE}")
        sys.exit(1)

    print("[VPN] Abriendo SECO Client...")
    subprocess.Popen(SECO_EXE)
    time.sleep(3)

    # Confirmar popup de ejecución (si aparece) presionando Enter
    print("[VPN] Confirmando popup de ejecución (si existe)...")
    pyautogui.press('enter')
    time.sleep(4)

    print("[VPN] Ingresando usuario...")
    pyautogui.click(*VPN_COORD_USUARIO)
    time.sleep(0.4)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.write(VPN_USUARIO, interval=0.05)
    print("[VPN] Ingresando contraseña...")
    pyautogui.click(*VPN_COORD_PASSWORD)
    time.sleep(0.4)
    pyautogui.write(VPN_PASSWORD, interval=0.05)
    print("[VPN] Conectando... (espera ~15 seg)")
    pyautogui.click(*VPN_COORD_CONECTAR)
    time.sleep(15)
    print("[VPN] ✓ VPN activado")


def descargar_lista():
    from playwright.sync_api import sync_playwright
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    print(f"\n[WEB] Iniciando Playwright — fecha: {fecha_hoy}")

    # Leer proxy del sistema Windows (si la VPN configura uno)
    proxy_cfg = None
    try:
        import winreg
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        proxy_enable, _ = winreg.QueryValueEx(reg, "ProxyEnable")
        if proxy_enable:
            proxy_server, _ = winreg.QueryValueEx(reg, "ProxyServer")
            if proxy_server:
                proxy_cfg = {"server": f"http://{proxy_server}"}
                print(f"[WEB] Proxy detectado: {proxy_server}")
    except Exception:
        pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx_args = {"accept_downloads": True}
        if proxy_cfg:
            ctx_args["proxy"] = proxy_cfg
        context = browser.new_context(**ctx_args)
        page = context.new_page()

        print("[WEB] Abriendo página de login...")
        page.goto(SRE_URL, wait_until="load", timeout=60000)
        print("[WEB] Ingresando credenciales SRE...")
        page.locator(f"xpath={XPATH['login_usuario']}").fill(SRE_USUARIO)
        page.locator(f"xpath={XPATH['login_password']}").fill(SRE_PASSWORD)
        page.locator(f"xpath={XPATH['login_boton']}").click()
        page.wait_for_load_state("load")
        print("[WEB] ✓ Login exitoso")

        print("[WEB] Navegando al menú de listas...")
        page.locator(f"xpath={XPATH['menu_listas']}").click()
        page.wait_for_load_state("load")
        time.sleep(1)

        print("[WEB] Abriendo menú de búsqueda...")
        page.locator(f"xpath={XPATH['abrir_busqueda']}").click()
        time.sleep(1)

        print(f"[WEB] Ingresando fecha: {fecha_hoy}")
        campo = page.locator(f"xpath={XPATH['campo_fecha']}")
        campo.click()
        campo.fill(fecha_hoy)
        time.sleep(0.5)

        print("[WEB] Ejecutando búsqueda...")
        page.locator(f"xpath={XPATH['btn_buscar']}").click()
        page.wait_for_load_state("load")
        time.sleep(2)

        print("[WEB] Descargando Excel...")
        with page.expect_download(timeout=30000) as dl:
            page.locator(f"xpath={XPATH['btn_descargar']}").click()
        download = dl.value
        nombre = f"lista_sre_{datetime.now().strftime('%Y%m%d')}.xlsx"
        ruta = DOWNLOAD_DIR / nombre
        download.save_as(ruta)
        print(f"[WEB] ✓ Guardado: {ruta}")
        browser.close()

    return ruta


def preparar_para_impresion(ruta_archivo: Path) -> Path:
    from openpyxl import load_workbook
    from openpyxl.worksheet.page import PageMargins

    print("\n[EXCEL] Configurando Hoja 2 para impresión...")
    wb = load_workbook(ruta_archivo)

    if len(wb.sheetnames) < 2:
        print(f"[EXCEL] AVISO: Solo hay {len(wb.sheetnames)} hoja(s). Usando la primera.")
        hoja = wb.worksheets[0]
    else:
        hoja = wb.worksheets[1]  # Hoja 2

    print(f"[EXCEL] Hoja: '{hoja.title}'")

    # Todas las columnas en 1 página de ancho / filas sin límite
    hoja.page_setup.orientation = "landscape"
    hoja.page_setup.paperSize   = 9       # Letter
    hoja.page_setup.fitToPage   = True
    hoja.page_setup.fitToWidth  = 1       # ← columnas en 1 página
    hoja.page_setup.fitToHeight = 0       # ← filas sin límite
    hoja.sheet_properties.pageSetUpPr.fitToPage = True
    hoja.page_margins = PageMargins(
        left=0.5, right=0.5, top=0.75, bottom=0.75,
        header=0.3, footer=0.3
    )

    ruta_print = ruta_archivo.parent / (ruta_archivo.stem + "_print.xlsx")
    wb.save(ruta_print)
    print(f"[EXCEL] ✓ Listo: {ruta_print}")
    return ruta_print


def imprimir_archivo(ruta_archivo: Path):
    import win32print, win32api
    print(f"\n[PRINT] Verificando impresora: {IMPRESORA}")

    if not ruta_archivo.exists():
        print(f"[PRINT] ERROR: Archivo no encontrado: {ruta_archivo}")
        return

    disponibles = [p[2] for p in win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    )]
    if IMPRESORA not in disponibles:
        print(f"[PRINT] ERROR: '{IMPRESORA}' no encontrada. Disponibles: {disponibles}")
        return

    anterior = win32print.GetDefaultPrinter()
    try:
        win32print.SetDefaultPrinter(IMPRESORA)
        win32api.ShellExecute(0, "print", str(ruta_archivo), None, ".", 0)
        time.sleep(8)
        print("[PRINT] ✓ Documento enviado a impresora")
    finally:
        win32print.SetDefaultPrinter(anterior)


if __name__ == "__main__":
    print("=" * 55)
    print("  AUTOMATIZACIÓN LISTAS SRE — CONSULADO KC")
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y  %H:%M')}")
    print("=" * 55)

    activar_vpn()
    archivo_original = descargar_lista()

    if archivo_original:
        archivo_para_imprimir = preparar_para_impresion(archivo_original)
        imprimir_archivo(archivo_para_imprimir)
        print("\n✅ Proceso completado exitosamente")
        print(f"   Original:   {archivo_original}")
        print(f"   Imprimido:  {archivo_para_imprimir}")
    else:
        print("\n❌ Error: no se pudo descargar el archivo")