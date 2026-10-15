# Trabajo N.º 3 — TaskCloud
**Curso:** Sistemas Distribuidos y Cloud Computing  
**Tema:** Desarrollo y despliegue de una aplicación web en Microsoft Azure.

## Funcionalidades
- Crear tareas con título, descripción, responsable y prioridad.
- Buscar y filtrar por estado.
- Actualizar estado: Pendiente, En progreso, Completada.
- Eliminar tareas.
- Resumen de tareas y base de datos SQLite.
- API JSON en `/api/tareas`, documentación automática en `/docs` y comprobación `/health`.

## Tecnologías
Python, FastAPI, Uvicorn, Jinja2, HTML/CSS, SQLite y Azure App Service.

## Ejecutar en Windows
En PowerShell, abre esta carpeta en VS Code y ejecuta:
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Si PowerShell bloquea la activación, en CMD usa `venv\Scripts\activate.bat`.

Prueba local:
- Aplicación: http://127.0.0.1:8000
- API: http://127.0.0.1:8000/docs
- Estado: http://127.0.0.1:8000/health
- Datos JSON: http://127.0.0.1:8000/api/tareas

## Despliegue en Azure App Service
1. Inicia sesión en el portal de Azure y crea un recurso **App Service / Web App**.
2. Elige publicar **Code**, sistema **Linux** y un runtime de Python ofrecido por el portal (preferentemente Python 3.11 si está disponible).
3. Asigna un nombre globalmente único a la Web App.
4. Instala en VS Code la extensión oficial **Azure App Service** e inicia sesión.
5. Abre esta carpeta en VS Code. Desde el panel Azure, clic derecho en el App Service y elige **Deploy to Web App**. Publica el contenido de esta carpeta, sin `venv/`.
6. En la configuración del App Service, define el comando de inicio:
   `gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app`
   No uses `--reload` en producción. Si el portal exige otro procedimiento de inicio, sigue la configuración recomendada para el runtime elegido.
7. Espera el despliegue y abre la URL HTTPS real que Azure asigne.
8. Verifica la URL principal, `/health`, `/docs` y `/api/tareas`. Si hay errores, revisa **Log stream** del App Service.

**Importante sobre SQLite:** este proyecto usa SQLite para facilitar la práctica. La persistencia del sistema de archivos local puede variar en App Service y no es adecuada para producción o múltiples instancias. Para una solución real, se recomienda Azure Database for PostgreSQL o Azure SQL y credenciales en variables de entorno. No afirmes que se desplegó correctamente hasta probar la URL pública real.

## Pruebas para el docente
1. Registrar una tarea.
2. Buscar por título o responsable.
3. Filtrar por estado.
4. Cambiar estado a En progreso y luego Completada.
5. Eliminar una tarea de prueba.
6. Mostrar `/docs`, ejecutar `GET /api/tareas` y abrir `/health`.
7. Abrir la URL desde otro dispositivo conectado a Internet.
