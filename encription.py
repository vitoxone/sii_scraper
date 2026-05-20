import os
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

MASTER_KEY = os.getenv("ENCRYPTION_KEY").encode()  # 32 bytes

def encriptar(texto: str) -> str:
    iv = secrets.token_bytes(16)
    cipher = Cipher(
        algorithms.AES(MASTER_KEY),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptador = cipher.encryptor()
    
    # AES-CBC requiere padding a múltiplos de 16 bytes
    texto_bytes = texto.encode()
    padding = 16 - len(texto_bytes) % 16
    texto_bytes += bytes([padding] * padding)
    
    encriptado = encryptador.update(texto_bytes) + encryptador.finalize()
    
    return f"{iv.hex()}:{encriptado.hex()}"


def desencriptar(texto_encriptado: str) -> str:
    iv_hex, encriptado_hex = texto_encriptado.split(":")
    iv = bytes.fromhex(iv_hex)
    encriptado = bytes.fromhex(encriptado_hex)
    
    cipher = Cipher(
        algorithms.AES(MASTER_KEY),
        modes.CBC(iv),
        backend=default_backend()
    )
    desencryptador = cipher.decryptor()
    
    texto_bytes = desencryptador.update(encriptado) + desencryptador.finalize()
    
    # Remover padding
    padding = texto_bytes[-1]
    texto_bytes = texto_bytes[:-padding]
    
    return texto_bytes.decode()


# --- Uso ---
if __name__ == "__main__":
    clave_original = "mi_clave_sii_secreta"
    
    encriptado = encriptar(clave_original)
    print(f"Encriptado:    {encriptado}")
    
    desencriptado = desencriptar(encriptado)
    print(f"Desencriptado: {desencriptado}")
    
    assert clave_original == desencriptado
    print("✅ Encriptación y desencriptación correctas")