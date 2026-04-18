import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import AudioRecorder from '../../components/ui/AudioRecorder';
import FileUpload from '../../components/ui/FileUpload';
import { Clock } from 'lucide-react';

const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/dashboard-data?role=patient&user_id=${user?.id}`)
      .then(res => res.json())
      .then(res => {
        if(res.status === 'success') {
          setData(res.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [user]);

  const handleAudio = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.wav');
    formData.append('patient_id', user?.id || 'guest');
    
    // Call multi-modal endpoint
    try {
      const res = await fetch('http://localhost:5000/api/upload-audio', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      alert(`Transcription: ${data.transcription}\nProcessed! See history.`);
      window.location.reload();
    } catch (e) {
      console.error(e);
      alert('Upload failed');
    }
  };

  const handleImage = async (file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('patient_id', user?.id || 'guest');
    
    try {
      const res = await fetch('http://localhost:5000/api/upload-prescription', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      alert(`Data Extracted. Detected Drugs: ${data?.extracted_data?.drugs?.join(', ')}`);
      window.location.reload();
    } catch (e) {
      console.error(e);
      alert('Upload failed');
    }
  };

  if(loading) return <div className="text-white p-8">Loading Patient Dashboard...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Patient Portal - Welcome, {user?.name}
        </h1>
        <p className="text-sm text-white/70 mt-1">Manage your health records and input symptoms.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AudioRecorder onAudioReady={handleAudio} />
        <FileUpload onFileSelect={handleImage} label="Upload Prescription (Image)" accept="image/*" />
      </div>

      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Clock size={18}/> Recent Predictions</h2>
        {data?.predictions?.length > 0 ? (
          <div className="space-y-4">
            {data.predictions.map((p: any, i: number) => (
              <div key={i} className="flex justify-between items-center p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium capitalize">{p.disease} Risk: {p.risk}</p>
                  <p className="text-xs text-white/50">{new Date(p.timestamp).toLocaleString()}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${p.risk === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                  {(p.confidence * 100).toFixed(1)}% Confidence
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-white/50 text-sm">No predictions found.</p>
        )}
      </div>
    </div>
  );
};

export default PatientDashboard;
