from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import law_explanation, letter_generation, bias_detection

app = FastAPI(
    title="Nepal Justice Weaver API",
    description="API for Law Explanation and Letter Generation modules.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(law_explanation.router, prefix="/api/v1", tags=["Law Explanation"])
app.include_router(letter_generation.router, prefix="/api/v1", tags=["Letter Generation"])
app.include_router(bias_detection.router, prefix="/api/v1", tags=["Bias Detection"])

@app.get("/")
async def root():
    return {"message": "Welcome to Nepal Justice Weaver API"}
