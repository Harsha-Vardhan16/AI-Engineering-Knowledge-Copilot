from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.search import router as search_router

app = FastAPI(
    title="AI Engineering Knowledge Copilot"
)

# ============================
# Enable CORS
# ============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# Routers
# ============================

app.include_router(upload_router)
app.include_router(search_router)

# ============================
# Home
# ============================

@app.get("/")
def home():
    return {
        "message": "AI Engineering Knowledge Copilot Backend Running"
    }