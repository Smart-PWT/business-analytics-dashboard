/**
 * UploadContext — shares the current upload_id across all pages
 * (Dashboard, Predictions, Export) after a file is uploaded on the
 * Upload page, without prop-drilling through routes.
 *
 * Persisted to localStorage so a page refresh doesn't lose it.
 */

import { createContext, useContext, useEffect, useState } from "react";

const STORAGE_KEY = "hisaabi_upload_id";

const UploadContext = createContext(null);

export function UploadProvider({ children }) {
  const [uploadId, setUploadIdState] = useState(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    return stored ? Number(stored) : null;
  });

  const [uploadMeta, setUploadMeta] = useState(null); // last upload's response (rows_ingested, etc.)

  useEffect(() => {
    if (uploadId !== null) {
      sessionStorage.setItem(STORAGE_KEY, String(uploadId));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, [uploadId]);

  function setUploadId(id, meta = null) {
    setUploadIdState(id);
    setUploadMeta(meta);
  }

  function clearUpload() {
    setUploadIdState(null);
    setUploadMeta(null);
  }

  return (
    <UploadContext.Provider value={{ uploadId, uploadMeta, setUploadId, clearUpload }}>
      {children}
    </UploadContext.Provider>
  );
}

/** Hook to read/set the current upload_id from any page. */
export function useUpload() {
  const context = useContext(UploadContext);
  if (!context) {
    throw new Error("useUpload must be used within an UploadProvider");
  }
  return context;
}
