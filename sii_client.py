import os
import time
import uuid

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = "https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi"
RCV_HOME_URL = "https://www4.sii.cl/consdcvinternetui/"
RCV_COMPRA_URL = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getDetalleCompraExport"
RCV_VENTA_URL = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getDetalleVentaExport"


def crear_driver(headless: bool = False) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    # Estas opciones van SIEMPRE, no solo en headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")

    # En contenedor (Render) se usan los binarios instalados por apt vía variables de entorno;
    # en local (Mac) caen ambos a None y se usa webdriver-manager + Chrome del sistema.
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin

    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(chromedriver_path) if chromedriver_path else Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def login_sii(rut: str, clave: str, headless: bool = False) -> dict:
    driver = crear_driver(headless)
    wait = WebDriverWait(driver, 20)
    session_data = {}

    try:
        print("🌐 Abriendo navegador...")
        driver.get(LOGIN_URL)
        print(f"📍 URL actual: {driver.current_url}")

        rut_sin_dv, dv = rut.strip().split("-")
        rut_sin_dv = rut_sin_dv.replace(".", "")

        print("✍️  Ingresando RUT...")
        campo_rut = wait.until(EC.presence_of_element_located((By.ID, "rutcntr")))
        campo_rut.clear()
        campo_rut.send_keys(rut_sin_dv + dv)

        print("✍️  Ingresando clave...")
        campo_clave = driver.find_element(By.ID, "clave")
        campo_clave.clear()
        campo_clave.send_keys(clave)

        print("🖱️  Haciendo click en ingresar...")
        btn = driver.find_element(By.ID, "bt_ingresar")
        btn.click()

        print("⏳ Esperando redirección...")
        wait.until(EC.url_contains("misiir.sii.cl"))
        time.sleep(2)

        # Navegar al RCV para que se seteen las cookies de www4.sii.cl
        # (TOKEN, CSESSIONID, NETSCAPE_LIVEWIRE.*, QueueITAccepted-*, TS3d*).
        # Sin este paso, los POST a getDetalleCompraExport/getDetalleVentaExport son rechazados.
        print("🌐 Navegando al RCV para completar cookies...")
        driver.get(RCV_HOME_URL)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)

        cookies = driver.get_cookies()
        session_data["cookies"] = {c["name"]: c["value"] for c in cookies}

        print(f"\n✅ Login exitoso. {len(cookies)} cookies obtenidas.")
        print(f"📍 URL final: {driver.current_url}")

        print("\n📋 Todas las cookies:")
        for nombre, valor in session_data["cookies"].items():
            print(f"  {nombre} = {valor}")

        print("\n🔑 Tokens relevantes:")
        for nombre, valor in session_data["cookies"].items():
            for t in ["JSESSIONID", "SII-session", "token", "auth"]:
                if t.lower() in nombre.lower():
                    print(f"  {nombre} = {valor}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"📍 URL al momento del error: {driver.current_url}")
        driver.save_screenshot("error_screenshot.png")
        print("📸 Screenshot guardado en error_screenshot.png")
        raise

    finally:
        driver.quit()

    return session_data


def cookies_para_requests(session_data: dict) -> dict:
    cookies = session_data.get("cookies", {})
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    return {
        "Cookie": cookie_str,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }


def _parsear_csv_rcv(data: list) -> list[dict]:
    if not data:
        return []
    headers = data[0].split(";")
    n = len(headers)
    filas = []
    for raw in data[1:]:
        valores = raw.split(";")
        if len(valores) < n:
            valores = valores + [""] * (n - len(valores))
        elif len(valores) > n:
            valores = valores[:n]
        filas.append(dict(zip(headers, valores)))
    return filas


def obtener_rcv(
    session_data: dict,
    rut_empresa_num: str,
    dv_empresa: str,
    periodo: str,
    operacion: str,
) -> list[dict]:
    if operacion not in ("COMPRA", "VENTA"):
        raise ValueError(f"operacion debe ser 'COMPRA' o 'VENTA', recibido: {operacion}")

    cookies = session_data.get("cookies", {})
    conversation_id = cookies.get("TOKEN") or cookies.get("CSESSIONID")
    if not conversation_id:
        raise RuntimeError("No se encontró TOKEN/CSESSIONID en las cookies de sesión")

    if operacion == "COMPRA":
        url = RCV_COMPRA_URL
        namespace_suffix = "getDetalleCompraExport"
        estado_contab = "REGISTRO"
        accion_recaptcha = "RCV_DDETC"
    else:
        url = RCV_VENTA_URL
        namespace_suffix = "getDetalleVentaExport"
        estado_contab = ""
        accion_recaptcha = "RCV_DDETV"

    body = {
        "metaData": {
            "namespace": f"cl.sii.sdi.lob.diii.consdcv.data.api.interfaces.FacadeService/{namespace_suffix}",
            "conversationId": conversation_id,
            "transactionId": str(uuid.uuid4()),
            "page": None,
        },
        "data": {
            "rutEmisor": rut_empresa_num,
            "dvEmisor": dv_empresa,
            "ptributario": periodo,
            "codTipoDoc": 0,
            "operacion": operacion,
            "estadoContab": estado_contab,
            "accionRecaptcha": accion_recaptcha,
            "tokenRecaptcha": "t-o-k-e-n-web",
        },
    }

    headers = cookies_para_requests(session_data)
    headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www4.sii.cl",
        "Referer": "https://www4.sii.cl/consdcvinternetui/",
    })

    print(f"📡 Consultando RCV {operacion} período {periodo} para {rut_empresa_num}-{dv_empresa}...")
    response = requests.post(url, json=body, headers=headers, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"SII RCV {operacion} respondió HTTP {response.status_code}: {response.text[:500]}"
        )
    payload = response.json()

    resp_estado = payload.get("respEstado") or {}
    cod = resp_estado.get("codRespuesta")
    if cod is not None and cod != 0:
        msg = resp_estado.get("msgeRespuesta") or resp_estado.get("codError") or "sin detalle"
        raise RuntimeError(f"SII RCV {operacion} devolvió codRespuesta={cod}: {msg}")

    return _parsear_csv_rcv(payload.get("data") or [])