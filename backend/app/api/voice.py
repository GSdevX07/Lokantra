"""
Voice Transcription API Blueprint (Sarvam AI Saaras Engine - Primary)
Provides high-fidelity speech-to-text conversion for voice prompts and reality seed text,
with native support for Indian languages (Hindi, Kannada, Tamil, Telugu, Marathi, Bengali, etc.)
and English using Sarvam AI Saaras v4.
"""

import os
import base64
import logging
import httpx
from flask import Blueprint, request, jsonify
from ..config import Config

logger = logging.getLogger('lokantra.voice')
voice_bp = Blueprint('voice', __name__)


@voice_bp.route('/status', methods=['GET'])
@voice_bp.route('/warmup', methods=['GET', 'POST'])
def voice_status():
    """
    Check voice transcription engine status and readiness.
    """
    sarvam_key = Config.SARVAM_API_KEY or os.environ.get('SARVAM_API_KEY')
    wispr_key = Config.WISPR_FLOW_API_KEY or os.environ.get('WISPR_FLOW_API_KEY')
    
    is_sarvam_configured = bool(sarvam_key and sarvam_key.strip() and sarvam_key.strip() != "your_sarvam_api_key")
    is_wispr_configured = bool(wispr_key and wispr_key.strip() and wispr_key.strip() != "your_wispr_flow_api_key")

    return jsonify({
        "success": True,
        "primary_provider": "sarvam_ai",
        "sarvam_configured": is_sarvam_configured,
        "model": Config.SARVAM_MODEL or "saaras:v4",
        "wispr_configured": is_wispr_configured,
        "message": "Sarvam AI Saaras engine active" if is_sarvam_configured else "Voice engine awaiting API key"
    }), 200


@voice_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Convert speech audio into text using Sarvam AI (Primary) with fallback to Wispr Flow.
    
    Accepts:
        - JSON: { "audio": "<base64_wav>", "language": "en-IN" (optional), "mode": "transcribe" }
        - multipart/form-data: file field "audio" or "file"
    
    Returns:
        {
            "success": True,
            "text": "Transcribed speech...",
            "detected_language": "en-IN",
            "provider": "sarvam_ai",
            "model": "saaras:v4"
        }
    """
    try:
        sarvam_key = Config.SARVAM_API_KEY or os.environ.get('SARVAM_API_KEY')
        wispr_key = Config.WISPR_FLOW_API_KEY or os.environ.get('WISPR_FLOW_API_KEY')
        
        # 1. Parse audio input
        audio_b64 = None
        raw_bytes = None
        language = None
        mode = "transcribe"
        
        if request.is_json:
            data = request.get_json(silent=True) or {}
            audio_b64 = data.get('audio') or data.get('audio_base64')
            language = data.get('language') or data.get('language_code')
            mode = data.get('mode') or "transcribe"
        elif 'audio' in request.files:
            file = request.files['audio']
            raw_bytes = file.read()
            language = request.form.get('language') or request.form.get('language_code')
            mode = request.form.get('mode') or "transcribe"
        elif 'file' in request.files:
            file = request.files['file']
            raw_bytes = file.read()
            language = request.form.get('language') or request.form.get('language_code')
            mode = request.form.get('mode') or "transcribe"
        elif 'audio' in request.form:
            audio_b64 = request.form.get('audio')
            language = request.form.get('language') or request.form.get('language_code')
            mode = request.form.get('mode') or "transcribe"

        if not raw_bytes and audio_b64:
            # Strip data URL prefix if present (e.g. data:audio/wav;base64,...)
            if "," in audio_b64:
                audio_b64 = audio_b64.split(",", 1)[1]
            raw_bytes = base64.b64decode(audio_b64)

        if not raw_bytes:
            return jsonify({
                "success": False,
                "error": "No audio payload provided. Please record and send audio data."
            }), 400

        # ====================================================================
        # PRIMARY PROVIDER: Sarvam AI Saaras v4
        # ====================================================================
        if sarvam_key and sarvam_key.strip() and sarvam_key.strip() != "your_sarvam_api_key":
            sarvam_url = Config.SARVAM_API_URL or "https://api.sarvam.ai/speech-to-text"
            model_name = Config.SARVAM_MODEL or "saaras:v4"
            
            headers = {
                "api-subscription-key": sarvam_key.strip()
            }
            files = {
                "file": ("recording.wav", raw_bytes, "audio/wav")
            }
            form_data = {
                "model": model_name,
                "mode": mode
            }
            if language and language not in ("auto", "unknown", "all"):
                form_data["language_code"] = language

            logger.info(f"Sending audio to Sarvam AI ({model_name}, mode={mode})...")
            with httpx.Client(timeout=45.0) as client:
                resp = client.post(sarvam_url, headers=headers, files=files, data=form_data)

            if resp.status_code == 200:
                result = resp.json()
                text = (result.get('transcript') or '').strip()
                detected_lang = result.get('language_code') or language or 'en-IN'
                request_id = result.get('request_id', '')
                logger.info(f"Sarvam AI transcription success (req={request_id}): {text[:60]}...")
                return jsonify({
                    "success": True,
                    "text": text,
                    "detected_language": detected_lang,
                    "provider": "sarvam_ai",
                    "model": model_name,
                    "request_id": request_id
                })
            else:
                err_body = resp.text
                logger.warning(f"Sarvam AI API error ({resp.status_code}): {err_body}")
                # If Wispr is not configured, return Sarvam error directly
                if not wispr_key or wispr_key.strip() in ("", "your_wispr_flow_api_key"):
                    return jsonify({
                        "success": False,
                        "error": f"Sarvam AI API returned ({resp.status_code}): {err_body}",
                        "status_code": resp.status_code
                    }), resp.status_code

        # ====================================================================
        # FALLBACK PROVIDER: Wispr Flow
        # ====================================================================
        if wispr_key and wispr_key.strip() and wispr_key.strip() != "your_wispr_flow_api_key":
            wispr_b64 = base64.b64encode(raw_bytes).decode('utf-8')
            wispr_url = Config.WISPR_FLOW_API_URL or "https://platform-api.wisprflow.ai/api/v1/dash/api"
            headers = {
                "Authorization": f"Bearer {wispr_key.strip()}",
                "Content-Type": "application/json"
            }
            payload = {
                "audio": wispr_b64,
                "language": [language] if language else ["en"],
                "context": {
                    "app": {"name": "Lokantra", "type": "ai"},
                    "dictionary_context": ["Lokantra", "swarm", "simulation", "reality", "agents"]
                }
            }
            logger.info("Falling back to Wispr Flow...")
            with httpx.Client(timeout=45.0) as client:
                resp = client.post(wispr_url, json=payload, headers=headers)

            if resp.status_code == 200:
                result = resp.json()
                text = result.get('text', '').strip()
                return jsonify({
                    "success": True,
                    "text": text,
                    "detected_language": result.get('detected_language', language or 'en'),
                    "provider": "wispr_flow"
                })

        # Neither provider succeeded or configured
        return jsonify({
            "success": False,
            "error": "SARVAM_API_KEY is not configured in .env. Please set your Sarvam AI API subscription key.",
            "is_configured": False
        }), 400

    except Exception as e:
        logger.exception("Voice transcription exception")
        return jsonify({
            "success": False,
            "error": f"Transcription request failed: {str(e)}"
        }), 500
