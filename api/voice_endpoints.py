from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from services.bhashini_service import BhashiniService, BhashiniError

router = APIRouter()

class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data
    source_language: str
    target_language: str
    include_speech: bool = False

class TextRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    include_speech: bool = False

@router.post("/process-voice")
async def process_voice(
    request: VoiceRequest,
    bhashini_service: BhashiniService = Depends()
) -> Dict:
    """
    Process voice input with translation and optional speech output
    """
    try:
        result = await bhashini_service.process_voice_input(
            audio_data=request.audio_data,
            source_language=request.source_language,
            target_language=request.target_language,
            include_speech=request.include_speech
        )
        return result
    except BhashiniError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-text")
async def process_text(
    request: TextRequest,
    bhashini_service: BhashiniService = Depends()
) -> Dict:
    """
    Process text input with translation and optional speech output
    """
    try:
        # Translate text
        translated_text = await bhashini_service.translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )
        
        result = {
            "source_text": request.text,
            "translated_text": translated_text,
            "audio": None
        }
        
        # Generate speech if requested
        if request.include_speech:
            audio = await bhashini_service.text_to_speech(
                text=translated_text,
                target_language=request.target_language
            )
            result["audio"] = audio
            
        return result
        
    except BhashiniError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speech-to-text")
async def speech_to_text(
    audio_data: str,
    language: str,
    bhashini_service: BhashiniService = Depends()
) -> Dict:
    """
    Convert speech to text
    """
    try:
        text = await bhashini_service.speech_to_text(
            audio_data=audio_data,
            source_language=language
        )
        return {"text": text}
    except BhashiniError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(
    text: str,
    language: str,
    bhashini_service: BhashiniService = Depends()
) -> Dict:
    """
    Convert text to speech
    """
    try:
        audio = await bhashini_service.text_to_speech(
            text=text,
            target_language=language
        )
        return {"audio": audio}
    except BhashiniError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 