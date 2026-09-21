from fastapi import FastAPI
from app.api.questions import router as questions_router

app = FastAPI(
	title="OA intelligence",
	version="0.1.0",

)


app.include_router(questions_router)

@app.get("/health")
def health_check():
	return{
		"status":"healthy",
		"service":"oa-intelligence",
}
