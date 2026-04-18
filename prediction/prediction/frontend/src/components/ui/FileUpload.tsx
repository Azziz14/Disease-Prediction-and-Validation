import React, { useCallback, useState } from 'react';
import { UploadCloud, Loader2 } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing?: boolean;
  accept?: string;
  label?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onFileSelect, 
  isProcessing = false,
  accept = "image/*",
  label = "Upload Image"
}) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`relative flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-xl transition-colors
        ${dragActive ? 'border-cyan-400 bg-cyan-400/10' : 'border-white/20 bg-white/5'}
      `}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleChange}
        disabled={isProcessing}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      
      <div className="flex flex-col items-center text-center pointer-events-none">
        {isProcessing ? (
          <Loader2 className="w-10 h-10 text-cyan-400 mb-3 animate-spin" />
        ) : (
          <UploadCloud className="w-10 h-10 text-cyan-400 mb-3" />
        )}
        <p className="text-lg font-medium text-white/90">{isProcessing ? 'Processing...' : label}</p>
        <p className="text-sm text-white/50 mt-1">Drag & Drop or Click to Select</p>
      </div>
    </div>
  );
};

export default FileUpload;
