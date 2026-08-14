import api from "./api";

export async function getBreakdown(scriptId) {
  const { data } = await api.get(`/breakdowns/${scriptId}`);
  return data.breakdown; // { id, script_id, status, ai_output_json, created_at }
}

export async function downloadBreakdownExport(scriptId, format, suggestedFilename) {
  const response = await api.get(`/breakdowns/${scriptId}/export`, {
    params: { format },
    responseType: "blob",
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = suggestedFilename || `breakdown.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
