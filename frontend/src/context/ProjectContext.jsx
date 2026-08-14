import { createContext, useState, useCallback } from "react";
import * as projectService from "../services/projectService";

export const ProjectContext = createContext(null);

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const refreshProjects = useCallback(async () => {
    setLoading(true);
    try {
      const data = await projectService.listProjects();
      setProjects(data);
    } finally {
      setLoading(false);
    }
  }, []);

  const addProject = useCallback(async (payload) => {
    const project = await projectService.createProject(payload);
    setProjects((prev) => [project, ...prev]);
    return project;
  }, []);

  const removeProject = useCallback(async (projectId) => {
    await projectService.deleteProject(projectId);
    setProjects((prev) => prev.filter((p) => p.id !== projectId));
  }, []);

  const value = { projects, loading, refreshProjects, addProject, removeProject };

  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>;
}
