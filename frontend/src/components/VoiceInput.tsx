import React, { useState, useRef } from 'react';
import { Button, Box, CircularProgress, Typography } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';

interface VoiceInputProps {
    onAudioCapture: (audioData: string) => void;
    isProcessing: boolean;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onAudioCapture, isProcessing }) => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64Audio = reader.result as string;
                    // Remove the data URL prefix
                    const base64Data = base64Audio.split(',')[1];
                    onAudioCapture(base64Data);
                };
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Error accessing microphone:', error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
                variant="contained"
                color={isRecording ? "error" : "primary"}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing}
                startIcon={isRecording ? <StopIcon /> : <MicIcon />}
                sx={{ minWidth: 150 }}
            >
                {isRecording ? "Stop Recording" : "Start Recording"}
            </Button>
            
            {isProcessing && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                        Processing audio...
                    </Typography>
                </Box>
            )}
        </Box>
    );
};

export default VoiceInput; 