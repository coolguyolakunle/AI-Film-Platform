import api from "./api";

export async function uploadScript(projectId, file) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_id", projectId);

  const { data } = await api.post("/scripts/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { script, scene_count_estimate }
}

export async function listScriptsForProject(projectId) {
  const { data } = await api.get(`/scripts/project/${projectId}`);
  return data.scripts;
}

export async function getScript(scriptId, { includeText = false } = {}) {
  const { data } = await api.get(`/scripts/${scriptId}`, {
    params: includeText ? { include_text: "true" } : {},
  });
  return data.script;
}

export async function deleteScript(scriptId) {
  await api.delete(`/scripts/${scriptId}`);
}
