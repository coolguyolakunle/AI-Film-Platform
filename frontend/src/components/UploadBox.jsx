import { useRef, useState } from "react";
import { ACCEPTED_SCRIPT_TYPES } from "../utils/constants";

export default function UploadBox({ onFileSelected, disabled = false }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleFiles = (files) => {
    const file = files?.[0];
    if (!file) return;
    setFileName(file.name);
    onFileSelected?.(file);
  };

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (!disabled) handleFiles(e.dataTransfer.files);
      }}
      className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-8 text-center transition-colors sm:p-10 ${
        disabled
          ? "cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400"
          : isDragging
          ? "border-brand-500 bg-brand-50"
          : "border-gray-300 hover:border-brand-400"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_SCRIPT_TYPES.join(",")}
        className="hidden"
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <p className="text-sm font-medium text-gray-700">
        {fileName ? fileName : "Drag & drop your script here, or click to browse"}
      </p>
      <p className="text-xs text-gray-400">Accepted formats: {ACCEPTED_SCRIPT_TYPES.join(", ")}</p>
    </div>
  );
}
