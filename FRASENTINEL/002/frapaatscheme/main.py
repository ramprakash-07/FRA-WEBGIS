from fastapi import FastAPI
from digitization import patta_module

app = FastAPI()

# Routers
app.include_router(patta_module.router, prefix="/digitization", tags=["Digitization"])

@app.get("/")
def root():
    return {"message": "Welcome to the Smart Campus API"}
