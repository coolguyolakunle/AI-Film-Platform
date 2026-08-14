import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { useFetch } from "../hooks/useFetch";
import { getProject } from "../services/projectService";
import { listScriptsForProject, deleteScript } from "../services/scriptService";
import { analyzeScript } from "../services/aiService";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import Button from "../components/Button.jsx";
import { formatDate } from "../utils/formatDate";

const STATUS_STYLES = {
  uploaded: "bg-gray-100 text-gray-600",
  parsed: "bg-blue-100 text-blue-700",
  processing: "bg-amber-100 text-amber-700",
  breakdown_ready: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

function StatusBadge({ status }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status] || "bg-gray-100 text-gray-600"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function ProjectDetail() {
  const { projectId } = useParams();

  const projectFetcher = useCallback(() => getProject(projectId), [projectId]);
  const { data: project, loading: projectLoading, error: projectError } = useFetch(projectFetcher, [projectId]);

  const scriptsFetcher = useCallback(() => listScriptsForProject(projectId), [projectId]);
  const { data: scripts, loading: scriptsLoading, refetch: refetchScripts } = useFetch(scriptsFetcher, [projectId]);

  const [deletingId, setDeletingId] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null);
  const [analyzeError, setAnalyzeError] = useState("");

  const pollRef = useRef(null);
  const hasProcessingScript = scripts?.some((s) => s.status === "processing");

  useEffect(() => {
    if (hasProcessingScript && !pollRef.current) {
      pollRef.current = setInterval(() => {
        refetchScripts();
      }, 3000);
    }
    if (!hasProcessingScript && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [hasProcessingScript, refetchScripts]);

  const handleDelete = async (scriptId) => {
    setDeletingId(scriptId);
    try {
      await deleteScript(scriptId);
      await refetchScripts();
    } finally {
      setDeletingId(null);
    }
  };

  const handleAnalyze = async (scriptId) => {
    setAnalyzingId(scriptId);
    setAnalyzeError("");
    try {
      await analyzeScript(scriptId);
      await refetchScripts();
    } catch (err) {
      setAnalyzeError(
        err?.response?.data?.message || "Analysis failed. You can try again."
      );
      await refetchScripts();
    } finally {
      setAnalyzingId(null);
    }
  };

  if (projectLoading) return <LoadingSpinner label="Loading project..." />;
  if (projectError || !project) {
    return <div className="px-4 py-8 text-center text-gray-500 sm:px-6 sm:py-10">Project not found.</div>;
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-10">
      <h1 className="text-2xl font-semibold text-gray-900">{project.title}</h1>
      {project.description && <p className="mt-2 text-gray-600">{project.description}</p>}
      <p className="mt-1 text-xs text-gray-400">Created {formatDate(project.created_at)}</p>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-medium text-gray-900">Scripts</h2>
        <Link to={`/upload?project_id=${project.id}`}>
          <Button className="w-full sm:w-auto">Upload Script</Button>
        </Link>
      </div>

      {analyzeError && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{analyzeError}</div>
      )}

      {scriptsLoading ? (
        <LoadingSpinner label="Loading scripts..." />
      ) : !scripts || scripts.length === 0 ? (
        <div className="mt-4 rounded-lg border border-dashed border-gray-300 px-4 py-12 text-center text-gray-500 sm:py-16">
          No scripts uploaded yet.
        </div>
      ) : (
        <ul className="mt-4 divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
          {scripts.map((script) => (
            <li key={script.id} className="flex flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
              <div className="min-w-0">
                <p className="truncate font-medium text-gray-900">{script.original_filename}</p>
                <p className="mt-1 text-xs text-gray-400">Uploaded {formatDate(script.created_at)}</p>
                {script.analysis_error && (
                  <p className="mt-1 max-w-xl text-xs text-red-600">{script.analysis_error}</p>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2 sm:justify-end">
                <StatusBadge status={script.status} />

                {(script.status === "parsed" || script.status === "failed") && (
                  <Button
                    variant="secondary"
                    loading={analyzingId === script.id}
                    onClick={() => handleAnalyze(script.id)}
                    className="flex-1 sm:flex-none"
                  >
                    {script.status === "failed" ? "Retry analysis" : "Analyze"}
                  </Button>
                )}

                {script.status === "processing" && (
                  <span className="text-xs text-gray-400">Analyzing...</span>
                )}

                {script.status === "breakdown_ready" && (
                  <Link to={`/breakdown/${script.id}`} className="rounded-lg bg-brand-50 px-3 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100">
                    View breakdown
                  </Link>
                )}

                <Button
                  variant="ghost"
                  loading={deletingId === script.id}
                  onClick={() => handleDelete(script.id)}
                  className="flex-1 sm:flex-none"
                >
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
