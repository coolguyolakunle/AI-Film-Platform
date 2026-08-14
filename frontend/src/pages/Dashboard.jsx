import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ProjectContext } from "../context/ProjectContext.jsx";
import { useAuth } from "../hooks/useAuth";
import Button from "../components/Button.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { formatDate } from "../utils/formatDate";

export default function Dashboard() {
  const { projects, loading, refreshProjects, addProject } = useContext(ProjectContext);
  const { user } = useAuth();
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");

  useEffect(() => {
    refreshProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    await addProject({ title: title.trim(), description: "" });
    setTitle("");
    setCreating(false);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-10">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Your Projects</h1>
          {user?.production_role_label && (
            <p className="mt-1 text-sm text-gray-500">
              Breakdowns will open in your {user.production_role_label} view first.
            </p>
          )}
        </div>
        <Button onClick={() => setCreating((v) => !v)} className="w-full sm:w-auto">
          {creating ? "Cancel" : "New Project"}
        </Button>
      </div>

      {creating && (
        <form onSubmit={handleCreate} className="mb-8 flex flex-col gap-3 sm:flex-row">
          <input
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Project title, e.g. 'Midnight in Lagos'"
            className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          <Button type="submit" className="sm:w-auto">Create</Button>
        </form>
      )}

      {loading ? (
        <LoadingSpinner label="Loading projects..." />
      ) : projects.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 px-4 py-12 text-center text-gray-500 sm:py-16">
          No projects yet. Create your first one to get started.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md sm:p-5"
            >
              <h2 className="font-medium text-gray-900">{project.title}</h2>
              <p className="mt-1 text-sm text-gray-500">
                {project.script_count} script{project.script_count === 1 ? "" : "s"}
              </p>
              <p className="mt-3 text-xs text-gray-400">Created {formatDate(project.created_at)}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
