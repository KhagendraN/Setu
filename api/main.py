from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import law_explanation, letter_generation, bias_detection, pdf_processing, supabase_auth, bias_detection_hitl
from api.core.config import settings

app = FastAPI(
    title="Nepal Justice Weaver API",
    description="API for Law Explanation and Letter Generation modules with Supabase Auth.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(supabase_auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(law_explanation.router, prefix="/api/v1", tags=["Law Explanation"])
app.include_router(letter_generation.router, prefix="/api/v1", tags=["Letter Generation"])
app.include_router(bias_detection.router, prefix="/api/v1", tags=["Bias Detection"])
app.include_router(bias_detection_hitl.router, prefix="/api/v1/bias-detection-hitl", tags=["Bias Detection HITL"])
app.include_router(pdf_processing.router, prefix="/api/v1", tags=["PDF Processing"])

@app.get("/")
async def root():
    return {"message": "Welcome to Nepal Justice Weaver API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

