import httpx
from config import COMFYUI_URL, logger

class ComfyUIClient:
    def __init__(self, base_url=COMFYUI_URL):
        self.base_url = base_url

    async def request_generation(self, message: str, nick: str):
        """
        Request image generation from the ComfyUI service.
        """
        url = f"{self.base_url}/request"
        payload = {"message": message, "nick": nick}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"ComfyUI API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling ComfyUI: {e}")
                raise

    async def get_job_status(self, job_id: str):
        """
        Get the current status of a generation job.
        """
        url = f"{self.base_url}/job/{job_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error getting job status for {job_id}: {e}")
                raise

    async def wait_for_job(self, job_id: str, timeout: float = 300.0):
        """
        Wait until the generation job is completed.
        """
        url = f"{self.base_url}/wait/{job_id}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error waiting for job {job_id}: {e}")
                raise

    async def list_models(self):
        """
        List available models in the ComfyUI service.
        """
        url = f"{self.base_url}/models"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error listing ComfyUI models: {e}")
                raise
