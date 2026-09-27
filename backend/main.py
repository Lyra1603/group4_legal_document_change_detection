from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline import run_pipeline

app = FastAPI(title="Legal Document Change Detection API")

class CompareRequest(BaseModel):
    doc_v1: str
    doc_v2: str

@app.post("/api/compare")
def compare_documents(req: CompareRequest):
    results = run_pipeline(req.doc_v1, req.doc_v2)
    return {"status": "success", "data": results}