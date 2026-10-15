from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import os, sqlite3
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parent
DB = Path(os.getenv("DB_PATH", str(ROOT / "tareas.db")))

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tareas(
          id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL,
          descripcion TEXT DEFAULT '', responsable TEXT DEFAULT '',
          prioridad TEXT NOT NULL DEFAULT 'Media', estado TEXT NOT NULL DEFAULT 'Pendiente',
          fecha TEXT NOT NULL)""")
        if c.execute("SELECT COUNT(*) FROM tareas").fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.executemany("INSERT INTO tareas(titulo,descripcion,responsable,prioridad,estado,fecha) VALUES(?,?,?,?,?,?)", [
              ("Preparar informe académico","Organizar avances y anexos.","Equipo académico","Alta","Pendiente",now),
              ("Revisar documentación","Verificar que los documentos estén completos.","Secretaría","Media","En progreso",now),
              ("Coordinar reunión","Definir agenda y acuerdos.","Coordinación","Baja","Completada",now)])

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="TaskCloud - Gestión de tareas", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(ROOT/"static")), name="static")
templates = Jinja2Templates(directory=str(ROOT/"templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = "", estado: str = "Todos"):
    with connect() as c:
        sql = "SELECT * FROM tareas WHERE (titulo LIKE ? OR descripcion LIKE ? OR responsable LIKE ?)"
        args = [f"%{q}%"]*3
        if estado != "Todos":
            sql += " AND estado=?"; args.append(estado)
        sql += " ORDER BY id DESC"
        tasks = c.execute(sql, args).fetchall()
        stats = {
          "total": c.execute("SELECT COUNT(*) FROM tareas").fetchone()[0],
          "pendientes": c.execute("SELECT COUNT(*) FROM tareas WHERE estado='Pendiente'").fetchone()[0],
          "progreso": c.execute("SELECT COUNT(*) FROM tareas WHERE estado='En progreso'").fetchone()[0],
          "completadas": c.execute("SELECT COUNT(*) FROM tareas WHERE estado='Completada'").fetchone()[0]}
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "tareas": tasks,
        "q": q,
        "estado_filtro": estado,
        "total": stats["total"],
        "pendientes": stats["pendientes"],
        "progreso": stats["progreso"],
        "completadas": stats["completadas"],
    },
)

@app.post("/tareas")
def crear(titulo: str = Form(...), descripcion: str = Form(""), responsable: str = Form(""), prioridad: str = Form("Media")):
    titulo = titulo.strip()
    if not titulo: raise HTTPException(400, "El título es obligatorio")
    if prioridad not in {"Baja","Media","Alta"}: prioridad = "Media"
    with connect() as c:
        c.execute("INSERT INTO tareas(titulo,descripcion,responsable,prioridad,estado,fecha) VALUES(?,?,?,?,?,?)",
          (titulo,descripcion.strip(),responsable.strip(),prioridad,"Pendiente",datetime.now().strftime("%Y-%m-%d %H:%M")))
    return RedirectResponse("/", status_code=303)

@app.post("/tareas/{task_id}/estado")
def cambiar_estado(task_id: int, estado: str = Form(...)):
    if estado not in {"Pendiente","En progreso","Completada"}: raise HTTPException(400,"Estado no válido")
    with connect() as c:
        cur = c.execute("UPDATE tareas SET estado=? WHERE id=?", (estado,task_id))
        if not cur.rowcount: raise HTTPException(404,"Tarea no encontrada")
    return RedirectResponse("/", status_code=303)

@app.post("/tareas/{task_id}/eliminar")
def eliminar(task_id: int):
    with connect() as c:
        cur = c.execute("DELETE FROM tareas WHERE id=?", (task_id,))
        if not cur.rowcount: raise HTTPException(404,"Tarea no encontrada")
    return RedirectResponse("/", status_code=303)

@app.get("/api/tareas")
def api_tareas():
    with connect() as c: return [dict(r) for r in c.execute("SELECT * FROM tareas ORDER BY id DESC").fetchall()]

@app.get("/health")
def health(): return {"status":"ok","application":"TaskCloud","timestamp":datetime.now().isoformat(timespec="seconds")}
