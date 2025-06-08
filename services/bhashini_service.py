import aiohttp
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class BhashiniService:
    def __init__(self):
        """Initialize Bhashini service"""
        self.base_url = "https://bhashini.gov.in/api"
        self.api_key = os.getenv("BHASHINI_API_KEY")
        self.pipeline_id = os.getenv("BHASHINI_PIPELINE_ID")
        self.session = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def search_pipeline(self, task_sequence: List[str], source_language: str, 
                            target_language: str) -> Dict:
        """
        Search for available pipelines based on task sequence and languages
        :param task_sequence: List of tasks (ASR, NMT, TTS)
        :param source_language: Source language code (ISO-639)
        :param target_language: Target language code (ISO-639)
        :return: Pipeline search results
        """
        try:
            url = f"{self.base_url}/v1/pipeline/search"
            
            payload = {
                "taskSequence": task_sequence,
                "sourceLanguage": source_language,
                "targetLanguage": target_language
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            session = await self.get_session()
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
        except Exception as e:
            self.logger.error(f"Pipeline search failed: {str(e)}")
            raise BhashiniError(f"Pipeline search failed: {str(e)}")

    async def get_pipeline_config(self, task_sequence: List[str], source_language: str,
                                target_language: str) -> Dict:
        """
        Get pipeline configuration
        :param task_sequence: List of tasks (ASR, NMT, TTS)
        :param source_language: Source language code
        :param target_language: Target language code
        :return: Pipeline configuration
        """
        try:
            url = f"{self.base_url}/v1/pipeline/config"
            
            payload = {
                "pipelineId": self.pipeline_id,
                "taskSequence": task_sequence,
                "sourceLanguage": source_language,
                "targetLanguage": target_language
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            session = await self.get_session()
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
        except Exception as e:
            self.logger.error(f"Pipeline config failed: {str(e)}")
            raise BhashiniError(f"Pipeline config failed: {str(e)}")

    async def compute_pipeline(self, config: Dict, input_data: str) -> Dict:
        """
        Execute pipeline computation
        :param config: Pipeline configuration
        :param input_data: Input data (text or audio base64)
        :return: Pipeline computation results
        """
        try:
            url = f"{self.base_url}/v1/pipeline/compute"
            
            payload = {
                "pipelineId": self.pipeline_id,
                "config": config,
                "input": input_data
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            session = await self.get_session()
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
            
        except Exception as e:
            self.logger.error(f"Pipeline computation failed: {str(e)}")
            raise BhashiniError(f"Pipeline computation failed: {str(e)}")

    async def speech_to_text(self, audio_data: str, source_language: str) -> str:
        """
        Convert speech to text using ASR
        :param audio_data: Base64 encoded audio data
        :param source_language: Source language code
        :return: Transcribed text
        """
        try:
            # Get pipeline config for ASR
            config = await self.get_pipeline_config(
                task_sequence=["ASR"],
                source_language=source_language,
                target_language=source_language
            )
            
            # Compute ASR
            result = await self.compute_pipeline(config, audio_data)
            
            return result.get("text", "")
            
        except Exception as e:
            self.logger.error(f"Speech to text failed: {str(e)}")
            raise BhashiniError(f"Speech to text failed: {str(e)}")

    async def translate_text(self, text: str, source_language: str, 
                           target_language: str) -> str:
        """
        Translate text using NMT
        :param text: Text to translate
        :param source_language: Source language code
        :param target_language: Target language code
        :return: Translated text
        """
        try:
            # Get pipeline config for NMT
            config = await self.get_pipeline_config(
                task_sequence=["NMT"],
                source_language=source_language,
                target_language=target_language
            )
            
            # Compute translation
            result = await self.compute_pipeline(config, text)
            
            return result.get("translation", "")
            
        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            raise BhashiniError(f"Translation failed: {str(e)}")

    async def text_to_speech(self, text: str, target_language: str) -> str:
        """
        Convert text to speech using TTS
        :param text: Text to convert
        :param target_language: Target language code
        :return: Base64 encoded audio data
        """
        try:
            # Get pipeline config for TTS
            config = await self.get_pipeline_config(
                task_sequence=["TTS"],
                source_language=target_language,
                target_language=target_language
            )
            
            # Compute TTS
            result = await self.compute_pipeline(config, text)
            
            return result.get("audio", "")
            
        except Exception as e:
            self.logger.error(f"Text to speech failed: {str(e)}")
            raise BhashiniError(f"Text to speech failed: {str(e)}")

    async def process_voice_input(self, audio_data: str, source_language: str,
                                target_language: str, include_speech: bool = False) -> Dict:
        """
        Process voice input through complete pipeline (ASR + NMT + optional TTS)
        :param audio_data: Base64 encoded audio data
        :param source_language: Source language code
        :param target_language: Target language code
        :param include_speech: Whether to include speech output
        :return: Processing results
        """
        try:
            # Define task sequence
            task_sequence = ["ASR", "NMT"]
            if include_speech:
                task_sequence.append("TTS")
            
            # Get pipeline config
            config = await self.get_pipeline_config(
                task_sequence=task_sequence,
                source_language=source_language,
                target_language=target_language
            )
            
            # Compute pipeline
            result = await self.compute_pipeline(config, audio_data)
            
            return {
                "source_text": result.get("text", ""),
                "translated_text": result.get("translation", ""),
                "audio": result.get("audio", "") if include_speech else None
            }
            
        except Exception as e:
            self.logger.error(f"Voice input processing failed: {str(e)}")
            raise BhashiniError(f"Voice input processing failed: {str(e)}")

class BhashiniError(Exception):
    """Custom exception for Bhashini-related errors"""
    pass 