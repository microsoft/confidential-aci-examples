from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/{anything:path}", response_class=PlainTextResponse)
async def index():
    return "Hello from workload A\n"


if __name__ == "__main__":
    print("Workload container started")
    print("Starting http server on port 8000", flush=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
