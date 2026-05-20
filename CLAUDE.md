# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito

API FastAPI que expone el login del SII (Servicio de Impuestos Internos de Chile) como endpoint HTTP. El endpoint `POST /login` recibe RUT y clave **encriptada con AES-256-CBC**, la desencripta con la `ENCRYPTION_KEY` del servidor, automatiza el login en el portal con Selenium, y devuelve las cookies de sesión que el cliente puede reutilizar contra `misiir.sii.cl`.

## Comandos

```bash
# Activar entorno virtual (ya existe en ./venv)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar la API en desarrollo (auto-reload)
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

Docs interactivas en `http://localhost:8000/docs` (Swagger) y `/redoc`.

No hay tests ni linters configurados en el repo.

## Variables de entorno

- `ENCRYPTION_KEY` — **exactamente 32 caracteres** (AES-256 requiere 32 bytes). Compartida entre el cliente que encripta la clave y el servidor que la desencripta. Si la longitud es incorrecta, AES revienta con error críptico.

`.env` se carga con `load_dotenv()` **antes** de importar `encription`, porque `encription.py` lee `ENCRYPTION_KEY` al cargar el módulo. No invertir el orden de imports en `main.py`.

## Endpoints

- `POST /login` — body `{ "rut": "12345678-9", "password": "<iv_hex>:<ciphertext_hex>" }` → `{ "cookies": { ... } }`. El campo `password` viene encriptado con `encriptar(...)` de `encription.py` usando la misma `ENCRYPTION_KEY`. El RUT debe traer guión y DV.
- `POST /encrypt` — body `{ "texto": "..." }` → `{ "encriptado": "<iv_hex>:<ciphertext_hex>" }`. Utilidad para encriptar usando la `ENCRYPTION_KEY` del servidor. **Ojo:** cualquiera con acceso al endpoint puede encriptar arbitrariamente con la key del server; protégelo con auth/red interna si es ambiente productivo.
- `GET /health` — liveness check.

## Arquitectura

Tres archivos:

1. **`encription.py` — AES-256-CBC simétrica.** `encriptar(texto)` genera un IV aleatorio de 16 bytes, aplica padding PKCS-like (rellena con bytes del valor del padding), encripta con `Cipher(AES, CBC)` y devuelve `"<iv_hex>:<ciphertext_hex>"`. `desencriptar(...)` invierte el proceso. `MASTER_KEY` se lee de `ENCRYPTION_KEY` **al importar el módulo** — por eso `main.py` llama `load_dotenv()` antes de importar.

2. **`sii_client.py` — login con navegador (Selenium + Chrome).**
   - `crear_driver(headless)` instancia Chrome con flags anti-detección: `--disable-blink-features=AutomationControlled`, `excludeSwitches=["enable-automation"]`, `useAutomationExtension=False`, y un script post-carga que sobrescribe `navigator.webdriver`. Estos flags son **necesarios** — sin ellos el SII bloquea el login. No los quites al "limpiar".
   - `login_sii(rut, clave, headless)` navega a `LOGIN_URL` (host `zeusr.sii.cl` con redirect a `misiir.sii.cl`), rellena `#rutcntr` y `#clave`, hace click en `#bt_ingresar`, espera la redirección a `misiir.sii.cl` y extrae todas las cookies. Cierra el driver en `finally`. Si falla guarda `error_screenshot.png`.
   - `cookies_para_requests(session_data)` arma el header `Cookie: k=v; ...` más un `User-Agent` para reutilizar la sesión con `requests` desde el lado del cliente.

3. **`main.py` — FastAPI app.** Carga `.env`, define `LoginRequest`, valida que el RUT incluya `-`, **desencripta** `payload.password` con `desencriptar()`, y llama a `login_sii` vía `run_in_threadpool` porque Selenium es síncrono y bloqueante (no usar `async def` para llamarlo directamente — bloquearía el event loop). Errores de desencriptación → `HTTP 422`, errores de login → `HTTP 502`.

## Deploy (Render)

Se despliega como **Docker web service** en Render. El `Dockerfile` instala `chromium` + `chromium-driver` vía apt (Render no trae Chrome preinstalado) y setea dos env vars: `CHROME_BIN=/usr/bin/chromium` y `CHROMEDRIVER_PATH=/usr/bin/chromedriver`. `sii_client.crear_driver` las lee — si están presentes usa los binarios del sistema, si no caen ambos a `None` y vuelve a `webdriver-manager` (para correr en Mac local).

En el dashboard de Render, el servicio debe tener:
- **Environment:** Docker (no Python nativo)
- **Env vars adicionales:** `ENCRYPTION_KEY` (igual a la del cliente que encripta). `CHROME_BIN` y `CHROMEDRIVER_PATH` ya vienen del Dockerfile.
- Puerto: Render inyecta `$PORT`; el CMD del Dockerfile lo respeta.

## Notas operacionales

- Selenium arranca un Chrome real por cada request a `/login`. Esto es lento (varios segundos) y costoso en RAM. No es seguro para alta concurrencia tal como está — si llega tráfico, considerar pool de drivers o cola async.
- ChromeDriver lo gestiona `webdriver-manager` en local; en Docker viene del paquete apt `chromium-driver`.
- El `time.sleep(2)` tras la redirección post-login existe porque algunas cookies se setean después del primer load; reducirlo puede dar sesiones incompletas.
- Las credenciales del SII ya no se leen de `.env` — vienen en el body del request. `.env` ahora se usa solo para `ENCRYPTION_KEY`.
