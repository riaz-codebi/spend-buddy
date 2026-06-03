from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def verify_whatsapp_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode != "subscribe" or not hub_challenge:
        raise HTTPException(status_code=403, detail="Invalid webhook verification request")

    if hub_verify_token != settings.meta_verify_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")

    return Response(content=hub_challenge, media_type="text/plain")
