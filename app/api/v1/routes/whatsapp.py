import json
import logging

from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

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


@router.post("/webhook")
async def receive_whatsapp_webhook(request: Request):
    """
    Receive incoming WhatsApp messages from Meta Cloud API.
    Defensively parse the payload and return quickly.
    """
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        logger.warning("Received invalid JSON in webhook request")
        return {"status": "received"}

    logger.info(f"Received webhook payload: {json.dumps(payload, indent=2)}")

    # Defensive parsing: extract fields safely
    sender = None
    message_id = None
    message_type = None
    message_text = None
    timestamp = None

    try:
        # Navigate through the nested Meta payload structure
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                if messages:
                    msg = messages[0]
                    sender = msg.get("from")
                    message_id = msg.get("id")
                    message_type = msg.get("type")
                    timestamp = msg.get("timestamp")
                    
                    # Extract text body if present
                    if message_type == "text":
                        text_obj = msg.get("text", {})
                        message_text = text_obj.get("body")
                    
                    # Log extracted fields
                    logger.info(
                        f"Extracted message: from={sender}, id={message_id}, "
                        f"type={message_type}, text={message_text}, timestamp={timestamp}"
                    )
                    break
            if sender:
                break
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {e}", exc_info=True)

    # Return quickly
    return {"status": "received"}

