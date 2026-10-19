SII Scraper 🇨🇱

API REST desarrollada en Python con FastAPI y Selenium para automatizar consultas al Servicio de Impuestos Internos (SII) de Chile.

El proyecto permite interactuar con los servicios del SII para consultar información tributaria, incluyendo el Registro de Compras y Ventas (RCV).

📋 Características

* API REST: endpoints desarrollados con FastAPI.
* Automatización web: Selenium y Chromium para interactuar con el portal del SII.
* Documentación interactiva: Swagger UI y OpenAPI.
* Encriptación: endpoint para encriptar textos mediante el mecanismo implementado en el proyecto.
* Consultas tributarias: operaciones relacionadas con el Registro de Compras y Ventas.
* Docker: ejecución mediante contenedores para simplificar la instalación.
* Desarrollo local: posibilidad de ejecutar la aplicación directamente con Python.

🛠️ Tecnologías

* Python 3.11
* FastAPI
* Uvicorn
* Selenium
* Chromium
* Docker
* Docker Compose

📦 Requisitos previos

Antes de comenzar, asegúrate de tener instalados:

* Git.
* Docker Desktop y Docker Compose, para ejecutar el proyecto mediante contenedores.
* Python 3.11, si deseas ejecutar el proyecto directamente.
* Acceso a Internet para interactuar con los servicios del SII.

🚀 Instalación

1. Clonar el repositorio

Abre una terminal y ejecuta:

git clone https://github.com/vitoxone/sii_scraper.git
cd sii_scraper

2. Revisar la estructura del proyecto

Identifica los archivos principales:

sii_scraper/
├── main.py
├── encription.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md

La estructura anterior es orientativa. Los archivos presentes pueden variar según la versión del repositorio.

3. Configurar las variables de entorno

Crea un archivo .env en la raíz del proyecto:

touch .env

Revisa el código para identificar las variables de entorno utilizadas:

grep -nE 'os.getenv|os.environ' *.py

Si el proyecto requiere una clave de encriptación, configura la variable correspondiente de acuerdo con la implementación de encription.py.

Para generar una clave aleatoria con Python:

python3 -c "import secrets; print(secrets.token_hex(32))"

Importante: antes de utilizar esta clave, verifica el algoritmo de encriptación y el formato que espera la aplicación. No agregues variables que no estén contempladas en el código.

No publiques el archivo .env ni compartas credenciales o secretos.

🐳 Ejecución con Docker

Docker es la opción recomendada para comenzar, ya que permite definir las dependencias del navegador y de Python en un entorno reproducible.

1. Construir e iniciar la aplicación

Desde la raíz del proyecto, ejecuta:

docker compose up --build

Docker construirá la imagen y levantará los servicios definidos en docker-compose.yml.

2. Verificar que la aplicación esté funcionando

Si la configuración publica el puerto 5001 del equipo local, podrás acceder a los siguientes recursos:

Recurso	Dirección
API	http://localhost:5001
Swagger UI	http://localhost:5001/docs
OpenAPI JSON	http://localhost:5001/openapi.json

Estas direcciones dependen de la configuración real de los puertos en docker-compose.yml.

Si Swagger UI carga correctamente, podrás consultar los endpoints disponibles y probarlos desde el navegador.

3. Consultar el estado de los contenedores

docker compose ps

4. Consultar los logs

docker compose logs -f

Para revisar un servicio específico:

docker compose logs -f <nombre_del_servicio>

Reemplaza <nombre_del_servicio> por el nombre definido en docker-compose.yml.

5. Detener la aplicación

Presiona Ctrl + C en la terminal.

También puedes ejecutar:

docker compose down

6. Reconstruir la imagen

Si modificas el código o las dependencias y necesitas reconstruir la imagen:

docker compose down
docker compose build --no-cache
docker compose up

🐍 Ejecución local con Python

También puedes ejecutar el proyecto directamente en tu equipo sin utilizar Docker.

1. Crear un entorno virtual

En macOS o Linux:

python3.11 -m venv .venv
source .venv/bin/activate

En Windows PowerShell:

py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1

2. Actualizar pip

python -m pip install --upgrade pip

3. Instalar las dependencias

pip install -r requirements.txt

4. Configurar las variables de entorno

Crea el archivo .env y agrega las variables requeridas por la aplicación.

Revisa los archivos de configuración y la implementación de encription.py para determinar los valores necesarios.

5. Configurar Selenium y Chromium

Verifica que Selenium pueda utilizar un navegador compatible.

Dependiendo de la configuración del proyecto, puede ser necesario instalar Chromium o Chrome y configurar el controlador correspondiente.

Si el proyecto utiliza Selenium Manager, la administración del controlador puede realizarse automáticamente, siempre que el entorno y la versión de Selenium lo permitan.

6. Iniciar el servidor

Si main.py contiene una instancia de FastAPI llamada app, ejecuta:

uvicorn main:app --reload --host 127.0.0.1 --port 8000

Accede a la documentación:

* Swagger UI: http://127.0.0.1:8000/docs
* OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Para detener el servidor, presiona Ctrl + C.

📚 Endpoints de la API

Los siguientes endpoints corresponden a las operaciones principales identificadas en el proyecto.

Para conocer los métodos HTTP, los parámetros obligatorios, los esquemas de entrada y las respuestas exactas, consulta la documentación generada por FastAPI.

POST /encrypt

Encripta un texto utilizando el mecanismo implementado por la aplicación.

Ejemplo ilustrativo de solicitud:

{
  "texto": "valor_de_prueba"
}

El nombre del campo y el formato de la respuesta deben confirmarse en el esquema real del endpoint.

POST /login

Permite iniciar el proceso de autenticación en el SII.

La solicitud utiliza las credenciales y el formato definidos en la implementación.

Antes de realizar una solicitud, revisa el esquema del endpoint para determinar qué campos debes enviar y cómo deben representarse las credenciales.

POST /rcv

Permite consultar información relacionada con el Registro de Compras y Ventas.

Según la implementación, la solicitud puede requerir datos como:

* RUT del contribuyente.
* Credenciales de autenticación.
* RUT de la empresa consultada.
* Período tributario.

El período tributario suele representarse mediante el formato YYYYMM.

Ejemplo:

202609

Este valor corresponde a septiembre de 2026.

Nota: los campos anteriores son orientativos. Confirma los parámetros obligatorios en Swagger UI antes de ejecutar una consulta.

🔄 Flujo general de funcionamiento

El flujo de trabajo de la aplicación es el siguiente:

1. El cliente envía una solicitud HTTP a la API.
2. FastAPI recibe y procesa la solicitud.
3. La aplicación valida los datos y prepara los parámetros necesarios.
4. Selenium interactúa con el portal del SII mediante el navegador configurado.
5. La aplicación procesa el resultado de la operación.
6. FastAPI devuelve una respuesta HTTP al cliente.

El resultado depende de la disponibilidad del SII, la validez de las credenciales y la compatibilidad de la automatización con el portal.

🧪 Pruebas de la API

La forma más sencilla de probar los endpoints es utilizar Swagger UI.

Paso 1. Abrir Swagger

Si ejecutas la aplicación mediante Docker:

http://localhost:5001/docs

Si ejecutas la aplicación directamente con Python:

http://127.0.0.1:8000/docs

Paso 2. Seleccionar un endpoint

Expande el endpoint que deseas probar.

Paso 3. Revisar el esquema de entrada

Selecciona Try it out y revisa los campos obligatorios.

Paso 4. Enviar la solicitud

Introduce los datos de prueba y ejecuta la operación.

Paso 5. Revisar la respuesta

Comprueba el código HTTP, el contenido de la respuesta y los logs de la aplicación si se produce un error.

Recomendación: utiliza credenciales propias y autorizadas. Evita realizar consultas repetitivas innecesarias contra los servicios del SII.

🔧 Solución de problemas

Docker no está disponible

Comprueba la instalación:

docker --version
docker compose version

Si Docker Desktop no está iniciado, ábrelo antes de ejecutar el proyecto.

Error al construir la imagen

Prueba una reconstrucción sin caché:

docker compose build --no-cache
docker compose up

Si el problema continúa, revisa los mensajes de error de la construcción.

La API no responde

Comprueba el estado de los servicios:

docker compose ps

Consulta los logs:

docker compose logs -f

Verifica que el puerto publicado coincida con el configurado en docker-compose.yml.

Error de dependencias de Python

Comprueba la versión instalada:

python --version

Si utilizas un entorno virtual, asegúrate de que esté activado antes de instalar las dependencias o iniciar el servidor.

Puedes reinstalar las dependencias con:

python -m pip install -r requirements.txt

Selenium no encuentra Chromium o ChromeDriver

Verifica que el navegador y su controlador sean compatibles con la configuración del proyecto.

Si utilizas Docker, revisa las instrucciones del Dockerfile para comprobar cómo se instalan y configuran estas dependencias.

Error al iniciar sesión en el SII

Comprueba:

* Que las credenciales sean correctas.
* Que los datos se envíen en el formato esperado.
* Que el mecanismo de encriptación esté configurado correctamente.
* Que el portal del SII esté disponible.
* Que no hayan cambiado los mecanismos de autenticación o la estructura de las páginas.

Los cambios en los servicios externos pueden requerir ajustes en el código de Selenium.

Error relacionado con las variables de entorno

Comprueba que el archivo .env exista en la ubicación esperada y que contenga las variables requeridas.

Recuerda que crear el archivo .env no garantiza que sus variables se carguen automáticamente: eso depende de la configuración de Docker y del código de la aplicación.

🔐 Seguridad

Este proyecto interactúa con credenciales e información tributaria.

Se recomienda seguir estas prácticas:

* No almacenar contraseñas directamente en el código fuente.
* No subir el archivo .env al repositorio.
* No registrar contraseñas ni claves de encriptación en los logs.
* Utilizar credenciales autorizadas.
* Restringir el acceso a la API cuando se ejecute en un servidor.
* No exponer endpoints sensibles directamente a Internet sin controles de autenticación y autorización.
* Utilizar HTTPS cuando la API se exponga fuera del entorno local.
* Proteger los datos tributarios obtenidos.
* Mantener actualizadas las dependencias y revisar sus vulnerabilidades.

La encriptación de una contraseña no sustituye el uso de HTTPS, la gestión segura de secretos ni los controles de acceso.

⚠️ Limitaciones

* La disponibilidad de las consultas depende de los servicios del SII.
* Los cambios en el portal pueden afectar la automatización.
* Selenium requiere un navegador compatible con el entorno de ejecución.
* La validez de las consultas depende de las credenciales y los permisos correspondientes.
* No se garantiza la compatibilidad futura si cambian los mecanismos de autenticación o las interfaces del SII.

📄 Licencia

Consulta la licencia disponible en el repositorio para conocer las condiciones de uso, modificación y distribución del código.

Si el repositorio no incluye un archivo de licencia, no debe asumirse que el código está disponible para cualquier uso sin restricciones.

👨‍💻 Autor y repositorio

Repositorio: vitoxone/sii_scraper

⸻

Desarrollado para facilitar la integración con servicios tributarios del SII mediante una API REST y automatización web.