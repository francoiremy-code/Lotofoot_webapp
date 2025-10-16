from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    conn = sqlite3.connect("lotofoot.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        mise REAL,
        gain REAL,
        statut TEXT,
        notes TEXT
    )""")
    return conn

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets ORDER BY date")
    rows = cur.fetchall()
    conn.close()

    total_mise = sum(r[3] for r in rows)
    total_gain = sum(r[4] for r in rows)
    net = total_gain - total_mise

    return templates.TemplateResponse("index.html", {
        "request": request,
        "rows": rows,
        "total_mise": total_mise,
        "total_gain": total_gain,
        "net": net,
    })

@app.post("/add")
def add_ticket(date: str = Form(...), type: str = Form(...),
               mise: float = Form(...), gain: float = Form(0),
               statut: str = Form(...), notes: str = Form("")):
    conn = get_db()
    conn.execute("INSERT INTO tickets (date, type, mise, gain, statut, notes) VALUES (?,?,?,?,?,?)",
                 (date, type, mise, gain, statut, notes))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/update/{ticket_id}")
def update(ticket_id: int, statut: str = Form(...), gain: float = Form(...)):
    conn = get_db()
    conn.execute("UPDATE tickets SET statut=?, gain=? WHERE id=?",
                 (statut, gain, ticket_id))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)
