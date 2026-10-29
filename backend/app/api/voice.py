"""
Voice Transcription API Blueprint (Sarvam AI Saaras Engine)
Provides high-fidelity speech-to-text conversion for voice prompts and reality seed text.
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
    is_sarvam_configured = bool(sarvam_key and sarvam_key.strip() and sarvam_key.strip() != "your_sarvam_api_key")

    return jsonify({
        "success": True,
        "configured": is_sarvam_configured,
        "model": Config.SARVAM_MODEL or "saaras:v4"
    }), 200


@voice_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Convert speech audio into text using Sarvam AI Saaras model.
    
    Accepts:
        - JSON: { "audio": "<base64_wav>", "language": "en-IN" (optional), "mode": "transcribe" }
        - multipart/form-data: file field "audio" or "file"
    
    Returns:
        {
            "success": True,
            "text": "Transcribed speech...",
            "detected_language": "en-IN"
        }
    """
    try:
        sarvam_key = Config.SARVAM_API_KEY or os.environ.get('SARVAM_API_KEY')
        
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

        if not sarvam_key or sarvam_key.strip() in ("", "your_sarvam_api_key"):
            return jsonify({
                "success": False,
                "error": "SARVAM_API_KEY is not configured in .env.",
                "is_configured": False
            }), 400

        # Call Sarvam AI REST endpoint
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

        logger.info(f"Connecting to speech transcription service ({model_name})...")
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(sarvam_url, headers=headers, files=files, data=form_data)

        if resp.status_code == 200:
            result = resp.json()
            text = (result.get('transcript') or '').strip()
            detected_lang = result.get('language_code') or language or 'en-IN'
            return jsonify({
                "success": True,
                "text": text,
                "detected_language": detected_lang
            })
        else:
            err_body = resp.text
            logger.warning(f"Voice API error ({resp.status_code}): {err_body}")
            return jsonify({
                "success": False,
                "error": f"Transcription error ({resp.status_code}): {err_body}",
                "status_code": resp.status_code
            }), resp.status_code

    except Exception as e:
        logger.exception("Voice transcription exception")
        return jsonify({
            "success": False,
            "error": f"Transcription request failed: {str(e)}"
        }), 500
