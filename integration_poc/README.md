# MinerU + EthioQS (DigitalMehandis) Integration PoC

This folder contains a Proof-of-Concept for integrating the **MinerU** document parsing engine with the **EthioQS** quantity surveying tool.

## Integration Strategy: Asynchronous Microservice
We use an asynchronous microservice approach where MinerU runs as a standalone FastAPI service. EthioQS communicates with MinerU via its REST API to offload heavy document processing.

## Files
- `mineru_client.py`: A reusable Python wrapper for the MinerU API.
- `ethioqs_router_mock.py`: A mock FastAPI router showing how EthioQS can trigger document parsing in a background task.

## How to Run the PoC

### 1. Start the MinerU API
First, ensure you have MinerU installed, then start the API server:
```bash
mineru-api --port 8000
```

### 2. Run the EthioQS Mock Backend
In a separate terminal, start the mock EthioQS service:
```bash
uvicorn integration_poc.ethioqs_router_mock:app --port 8001
```

### 3. Test the Integration
You can now "upload" a construction drawing to the mock EthioQS endpoint:
```bash
curl -X POST "http://127.0.0.1:8001/upload-drawing" -F "file=@/path/to/your/drawing.pdf"
```

### 4. Observe the Workflow
1. The `upload-drawing` endpoint will return a `file_id` immediately.
2. Check the terminal where you ran `uvicorn`. You will see logs indicating:
   - File saved locally.
   - Task submitted to MinerU.
   - Waiting for completion (polling).
   - Final success message once MinerU finishes parsing the document.

## Benefits for EthioQS
- **Auto-BOQ:** Use MinerU's high-accuracy table extraction to automatically fill quantity takeoff forms.
- **Spec-RAG:** Convert project specifications to Markdown for AI-powered technical queries.
- **Handwritten Record OCR:** Digitize site journals and handwritten material receipts.
