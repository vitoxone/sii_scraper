import sys

from dotenv import load_dotenv

load_dotenv()  # Debe ir antes de importar encription (lee ENCRYPTION_KEY al cargar el módulo)

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from encription import desencriptar, encriptar
from sii_client import login_sii

app = FastAPI(title="SII Scraper API")


class LoginRequest(BaseModel):
    rut: str = Field(..., description="RUT con guión y dígito verificador, ej: 12345678-9")
    password: str = Field(..., description="Clave del SII encriptada (formato 'iv_hex:ciphertext_hex')")


class LoginResponse(BaseModel):
    cookies: dict[str, str]


class EncryptRequest(BaseModel):
    texto: str = Field(..., description="Texto plano a encriptar")


class EncryptResponse(BaseModel):
    encriptado: str = Field(..., description="Texto encriptado en formato 'iv_hex:ciphertext_hex'")


@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt(payload: EncryptRequest) -> EncryptResponse:
    try:
        return EncryptResponse(encriptado=encriptar(payload.texto))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo encriptar: {exc}") from exc


@app.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    if "-" not in payload.rut:
        raise HTTPException(status_code=422, detail="El RUT debe incluir guión y dígito verificador")

    try:
        clave = desencriptar(payload.password)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"No se pudo desencriptar la clave: {exc}") from exc

    try:
        session = await run_in_threadpool(login_sii, payload.rut, clave, True)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Login en SII falló: {exc}") from exc

    cookies = session.get("cookies") or {}
    if not cookies:
        raise HTTPException(status_code=502, detail="Login en SII no devolvió cookies")

    return LoginResponse(cookies=cookies)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
