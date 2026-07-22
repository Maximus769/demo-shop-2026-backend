import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base
from routers import auth, products, cart, orders, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[startup] DB tables created OK")
    except Exception as e:
        print(f"[startup] DB init error (continuing): {e}")
    yield
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="Demo Shop 2026 — API",
    description="Backend e-commerce pour T-Shirts personnalisés (France)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/", tags=["system"])
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "service": "demo-shop-2026"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Ressource introuvable"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"detail": "Erreur serveur interne"})
