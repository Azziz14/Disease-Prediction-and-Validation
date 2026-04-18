import React, { useState, useRef } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';

interface AudioRecorderProps {
  onAudioReady: (audioBlob: Blob) => void;
  isProcessing?: boolean;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onAudioReady, isProcessing = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : '';
      const mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const actualMime = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: actualMime });
        onAudioReady(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      alert('Could not access microphone.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-4 bg-white/5 border border-white/10 rounded-xl">
      <h3 className="text-lg font-semibold text-white/90 mb-4">Voice Input</h3>
      
      <div className="flex items-center gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isProcessing}
            className={`p-4 rounded-full bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/40 transition-colors border border-cyan-500/30 ${isProcessing && 'opacity-50 cursor-not-allowed'}`}
          >
            {isProcessing ? <Loader2 className="w-6 h-6 animate-spin" /> : <Mic className="w-6 h-6" />}
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="p-4 rounded-full bg-red-500/20 text-red-500 hover:bg-red-500/40 transition-colors border border-red-500/30 animate-pulse"
          >
            <Square className="w-6 h-6" />
          </button>
        )}
      </div>
      
      <p className="mt-4 text-sm text-white/60">
        {isRecording ? "Listening... click stop when done." : "Click microphone to record symptoms"}
      </p>
    </div>
  );
};

export default AudioRecorder;
