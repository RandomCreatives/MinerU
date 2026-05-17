from fastapi import FastAPI, UploadFile, File, BackgroundTasks
import os
import shutil
import uuid
from .mineru_client import MinerUClient

from contextlib import asynccontextmanager

# Assume MinerU is running on a different port or server
MINERU_SERVICE_URL = os.getenv("MINERU_API_URL", "http://127.0.0.1:8000")
mineru_client = MinerUClient(base_url=MINERU_SERVICE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: client is initialized on first use
    yield
    # Shutdown: cleanup the client
    await mineru_client.close()

app = FastAPI(
    title="EthioQS Mock Backend with MinerU Integration",
    lifespan=lifespan
)

# Local storage for documents in EthioQS
UPLOAD_DIR = "./ethioqs_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-drawing")
async def upload_construction_drawing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Simulates an EthioQS endpoint where a user uploads a drawing.
    The drawing is saved locally, and then a MinerU task is triggered.
    """
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    local_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # In a real app, we would save the initial 'processing' status to the DB here
    # Then we trigger the async processing in the background
    background_tasks.add_task(handle_mineru_processing, local_path, file_id)

    return {
        "message": "Drawing uploaded and processing started.",
        "file_id": file_id,
        "status": "processing"
    }

async def handle_mineru_processing(file_path: str, file_id: str):
    """
    Background worker that communicates with MinerU.
    """
    try:
        # 1. Submit to MinerU
        result = await mineru_client.process_document_sync(file_path)

        # 2. Extract specific data (e.g., BOQ tables)
        # Here we would parse the JSON/Markdown to find construction data
        # For this PoC, we just log that we got the result
        print(f"Successfully processed {file_id}. Result keys: {result.keys()}")

        # 3. Update EthioQS Database
        # update_db_status(file_id, "completed", result['results'])

    except Exception as e:
        print(f"Failed to process {file_id}: {e}")
        # update_db_status(file_id, "failed", str(e))

@app.get("/drawing/{file_id}")
async def get_drawing_status(file_id: str):
    """
    Endpoint for the EthioQS frontend to check if the parsing is done.
    """
    # In a real app, this would query the PostgreSQL database
    return {
        "file_id": file_id,
        "status": "See server logs for PoC background progress",
        "note": "In a real integration, the background task would update a DB record."
    }

if __name__ == "__main__":
    print("This is a mock router demonstrating integration.")
    print("To run as a real service: uvicorn integration_poc.ethioqs_router_mock:app --port 8001")
