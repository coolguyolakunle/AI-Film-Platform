import { useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";

import UploadBox from "../components/UploadBox.jsx";
import Button from "../components/Button.jsx";
import { uploadScript } from "../services/scriptService";
import { useAuth } from "../hooks/useAuth";

export default function UploadScript() {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("project_id");
  const navigate = useNavigate();
  const { user } = useAuth();

  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | error | done
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file || !projectId) return;
    setStatus("uploading");
    setMessage("");
    try {
      const data = await uploadScript(projectId, file);
      setResult(data);
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setMessage(err?.response?.data?.message || "Upload failed. Please try again.");
    }
  };

  if (!projectId) {
    return (
      <div className="mx-auto max-w-xl px-4 py-8 text-center text-gray-500 sm:px-6 sm:py-10">
        No project selected. Go to your{" "}
        <Link to="/dashboard" className="text-brand-600 hover:underline">
          dashboard
        </Link>{" "}
        and choose a project first.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-6 sm:px-6 sm:py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Upload a Script</h1>
      <p className="mt-1 text-sm text-gray-500">
        Upload a screenplay (PDF or Word) to generate a production breakdown
        {user?.production_role_label ? ` focused on ${user.production_role_label}.` : "."}
      </p>

      <div className="mt-6">
        <UploadBox onFileSelected={setFile} disabled={status === "uploading"} />
      </div>

      {status === "error" && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{message}</div>
      )}

      {status === "done" && result && (
        <div className="mt-4 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
          Uploaded and parsed successfully. Estimated {result.scene_count_estimate} scene
          {result.scene_count_estimate === 1 ? "" : "s"} found.
        </div>
      )}

      {status === "done" ? (
        <Button className="mt-6 w-full" onClick={() => navigate(`/projects/${projectId}`)}>
          Back to project
        </Button>
      ) : (
        <Button
          className="mt-6 w-full"
          disabled={!file}
          loading={status === "uploading"}
          onClick={handleUpload}
        >
          Upload
        </Button>
      )}
    </div>
  );
}
