from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import run_agent
import os

app = FastAPI(title="GitHub Dev Card Generator")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated cards as static files
os.makedirs("static/cards", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    username: str

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    print(f"INFO: Received generation request for user: {request.username}")
    try:
        result = await run_agent(request.username)
        return {
            "message": result["message"],
            "url": f"/static/cards/{request.username}.html"
        }
    except Exception as e:
        import traceback
        error_detail = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(f"ERROR: Generation failed for {request.username}:\n{error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
