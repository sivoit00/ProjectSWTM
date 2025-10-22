from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Input model
class TextInput(BaseModel):
    text: str
    action: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/process")
async def process_text(data: TextInput):
    text = data.text
    action = data.action

    if action == 'echo':
        result = text
    elif action == 'uppercase':
        result = text.upper()
    elif action == 'ai':
        result = f"Pseudo-KI-Antwort auf: '{text}' — [Hier könnte Ihre KI stehen]"
    else:
        result = "Ungültige Aktion."

    return JSONResponse(content={"result": result})

# Nur nötig, wenn du direkt startest
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
