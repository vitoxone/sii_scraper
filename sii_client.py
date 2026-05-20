import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = "https://zeusr.sii.cl//AUT2000/InicioAutenticacion/IngresoRutClave.html?https://misiir.sii.cl/cgi_misii/siihome.cgi"


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