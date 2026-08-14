import api from "./api";

export async function listProjects() {
  const { data } = await api.get("/projects");
  return data.projects;
}

export async function createProject({ title, description }) {
  const { data } = await api.post("/projects", { title, description });
  return data.project;
}

export async function getProject(projectId) {
  const { data } = await api.get(`/projects/${projectId}`);
  return data.project;
}

export async function deleteProject(projectId) {
  await api.delete(`/projects/${projectId}`);
}
