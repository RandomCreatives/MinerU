import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
import os

class MinerUClient:
    """
    A lightweight client to interact with the MinerU FastAPI service.
    Designed for integration into construction management tools like EthioQS.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def get_http_client(self) -> httpx.AsyncClient:
        """Returns a reused AsyncClient instance for connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def close(self):
        """Closes the internal HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def submit_task(self, file_path: str, backend: str = "hybrid-auto-engine") -> str:
        """
        Submits a document to MinerU for parsing.
        Returns the task_id.
        """
        url = f"{self.base_url}/tasks"

        # We use 'auto' parse_method and enable formulas/tables by default for construction docs
        data = {
            "backend": backend,
            "parse_method": "auto",
            "formula_enable": "true",
            "table_enable": "true",
            "image_analysis": "true",
            "return_md": "true",
            "return_content_list": "true"
        }

        filename = os.path.basename(file_path)
        client = await self.get_http_client()

        with open(file_path, "rb") as f:
            files = {"files": (filename, f, "application/pdf")}
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            result = response.json()
            return result["task_id"]

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Checks the status of a specific task.
        """
        url = f"{self.base_url}/tasks/{task_id}"
        client = await self.get_http_client()
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieves the structured parsing results.
        """
        url = f"{self.base_url}/tasks/{task_id}/result"
        client = await self.get_http_client()
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

    async def process_document_sync(self, file_path: str, poll_interval: int = 2) -> Dict[str, Any]:
        """
        Helper method that submits, polls until finished, and returns the result.
        Useful for simple integration scripts.
        """
        print(f"Submitting {file_path} to MinerU...")
        task_id = await self.submit_task(file_path)
        print(f"Task created: {task_id}. Waiting for completion...")

        while True:
            status_data = await self.get_task_status(task_id)
            status = status_data.get("status")

            if status == "completed":
                print("Processing complete!")
                return await self.get_task_result(task_id)
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                raise Exception(f"MinerU task failed: {error}")

            # Still pending or processing
            await asyncio.sleep(poll_interval)

if __name__ == "__main__":
    # Example usage (standalone)
    async def main():
        client = MinerUClient()
        # Ensure you have a test.pdf in the directory or update this path
        try:
            # result = await client.process_document_sync("sample.pdf")
            # print("Successfully parsed document!")
            # print(f"Markdown snippet: {result['results']['sample']['md_content'][:200]}...")
            print("Client initialized. Usage: python mineru_client.py <path_to_pdf>")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
