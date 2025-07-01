from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from minio import Minio
from datetime import timedelta
import urllib3

urllib3.disable_warnings()

app = FastAPI()

class PresignRequest(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    filename: str
    expires_minutes: int = 10
    secure: bool = False

@app.post("/presign")
def generate_presigned_url(req: PresignRequest):
    try:
        client = Minio(
            endpoint=req.endpoint.replace("http://", "").replace("https://", ""),
            access_key=req.access_key,
            secret_key=req.secret_key,
            secure=req.secure
        )

        if not client.bucket_exists(req.bucket):
            raise HTTPException(status_code=404, detail="El bucket no existe")

        url = client.presigned_put_object(
            req.bucket,
            req.filename,
            expires=timedelta(minutes=req.expires_minutes)
        )
        return {"url": url}
    except Exception as e:
    import traceback
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
