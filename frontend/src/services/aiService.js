import api from "./api";

export async function analyzeScript(scriptId) {
  const { data } = await api.post(`/ai/analyze/${scriptId}`);
  return data.breakdown;
}
