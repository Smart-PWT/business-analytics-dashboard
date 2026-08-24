/** Central API client. */

const API_BASE_URL = "http://127.0.0.1:8000";

/** Uploads file, returns JSON. */
export async function uploadFile(file, userId = null) {
  const formData = new FormData();
  formData.append("file", file);
  if (userId) {
    formData.append("user_id", userId);
  }

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
export async function listUploads(userId = null) {
  const url = userId 
    ? `${API_BASE_URL}/api/uploads?user_id=${encodeURIComponent(userId)}`
    : `${API_BASE_URL}/api/uploads`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Could not load upload history.");
  }
  return response.json();
}

/** Deletes a specific upload by ID. */
export async function deleteUpload(uploadId) {
  const response = await fetch(`${API_BASE_URL}/api/uploads/${uploadId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Could not delete upload.");
  }
  return response.json();
}

/** Fetches a three-part preview (first / middle / last) of the cleaned dataset. */
export async function getCleanedPreview(uploadId, n = 10) {
  const response = await fetch(
    `${API_BASE_URL}/api/export/${uploadId}/preview?n=${n}`
  );
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Could not load dataset preview.");
  }
  return data;
}

/** Triggers a browser download of the full cleaned dataset as a CSV file. */
export async function exportCleanedCsv(uploadId) {
  const response = await fetch(`${API_BASE_URL}/api/export/${uploadId}/csv`);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Export failed. Please try again.");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cleaned_data_${uploadId}.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
