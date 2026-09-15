from fastapi import FastAPI

app = FastAPI()

metadata = []

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/metadata")
def new_metadata(metadata: str):
    metadata.append(metadata)
    return metadata