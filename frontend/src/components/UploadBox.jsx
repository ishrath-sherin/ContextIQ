import { useRef, useState } from "react";
import { Upload, CheckCircle2 } from "lucide-react";

function UploadBox() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  return (
    <div className="mt-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="text-xl font-bold text-slate-900">
        Upload Document
      </h2>

      <p className="mt-1 text-sm text-slate-500">
        Upload a PDF document to your private search engine.
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
        className="hidden"
      />

      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="mt-6 flex w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 transition hover:border-blue-500 hover:bg-blue-50"
      >
        {file ? (
          <>
            <CheckCircle2 size={42} className="text-green-500" />

            <p className="mt-4 font-semibold text-slate-800">
              {file.name}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </>
        ) : (
          <>
            <Upload size={42} className="text-blue-600" />

            <p className="mt-4 font-semibold text-slate-800">
              Click to choose a PDF
            </p>

            <p className="mt-1 text-sm text-slate-500">
              PDF files only
            </p>
          </>
        )}
      </button>

      {file && (
        <button
          type="button"
          className="mt-5 w-full rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
        >
          Upload Document
        </button>
      )}
    </div>
  );
}

export default UploadBox;