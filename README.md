# SII Scraper

API REST desarrollada en Python con FastAPI y Selenium para automatizar consultas al Servicio de Impuestos Internos (SII) de Chile.

El proyecto permite interactuar con los servicios del SII para consultar información tributaria, incluyendo registros de compras y ventas (RCV).

## Características

- **API REST:** endpoints desarrollados con FastAPI.
- **Automatización web:** Selenium y Chromium para interactuar con el portal del SII.
- **Documentación interactiva:** Swagger UI y OpenAPI.
- **Encriptación:** endpoint para encriptar contraseñas antes de utilizarlas en las operaciones que lo requieren.
- **Docker:** ejecución mediante contenedores para facilitar la instalación y configuración del entorno.

## Tecnologías

- Python 3.11
- FastAPI
- Uvicorn
- Selenium
- Chromium
- Docker
- Docker Compose

## Requisitos previos

Para ejecutar el proyecto necesitas:

- Git.
- Docker Desktop y Docker Compose, para la instalación recomendada.
- Python 3.11, si deseas ejecutarlo sin Docker.
- Acceso a Internet para interactuar con los servicios del SII.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/vitoxone/sii_scraper.git
cd sii_scraper