/** Central API client. */

const API_BASE_URL = "http://127.0.0.1:8000";

/** Uploads file, returns JSON. */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    // FastAPI error response format
    throw new Error(data.detail || "Upload failed. Please try again.");
  }

  return data; // Returns upload data.
}

/** Fetches dashboard analysis views. */
export async function getDashboard(uploadId, { startDate, endDate } = {}) {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);

  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_BASE_URL}/api/dashboard/${uploadId}${query}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not load dashboard.");
  }
  return data;
}

/** Fetches predictions for upload. */
export async function getPredictions(uploadId) {
  const response = await fetch(`${API_BASE_URL}/api/predictions/${uploadId}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not load predictions.");
  }
  return data;
}

/** Forces predictions re-run. */
export async function rerunPredictions(uploadId) {
  const response = await fetch(`${API_BASE_URL}/api/predictions/${uploadId}/run`, {
    method: "POST",
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Could not run predictions.");
  }
  return data;
}

/** Lists all past uploads. */
export async function listUploads() {
  const response = await fetch(`${API_BASE_URL}/api/uploads`);
  if (!response.ok) {
    throw new Error("Could not load upload history.");
  }
  return response.json();
}
