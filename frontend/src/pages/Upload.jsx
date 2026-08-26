import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import tick from "../assets/tick.png";
import cross from "../assets/cross.png";
import { uploadFile, listUploads, deleteUpload } from "../api/client";
import { useUpload } from "../context/UploadContext";
import { account } from "../config/appwrite";

function Upload() {
    const [status, setStatus] = useState("idle");
    const [errorText, setErrorText] = useState("");
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [userEmail, setUserEmail] = useState(null);

    const { uploadId, setUploadId, clearUpload } = useUpload();
    const navigate = useNavigate();

    // Fetch user history on component mount or when upload status changes
    useEffect(() => {
        async function fetchHistory() {
            setLoadingHistory(true);
            try {
                let email = null;
                try {
                    const user = await account.get();
                    email = user.email;
                    setUserEmail(email);
                } catch (err) {
                    // Ignore if not logged in
                }
                const list = await listUploads(email);
                setHistory(list);
            } catch (err) {
                console.error("Error fetching history:", err);
            } finally {
                setLoadingHistory(false);
            }
        }
        fetchHistory();
    }, [status]);

    async function handleFileChange(event) {
        const file = event.target.files[0];
        if (!file) return;

        setStatus("uploading");
        setErrorText("");

        try {
            const data = await uploadFile(file, userEmail);
            setResult(data);
            setUploadId(data.upload_id, data);
            setStatus("success");
        } catch (err) {
            setErrorText(err.message);
            setStatus("error");
        }
    }

    function navigateToDashboard() {
        navigate("/dashboard");
    }

    function navigateToExport() {
        navigate("/export");
    }

    function handleSelectHistory(id) {
        setUploadId(id);
        navigate("/dashboard");
    }

    async function handleDeleteHistory(id) {
        if (!window.confirm("Are you sure you want to delete this upload? This will remove all associated transactions and predictions.")) {
            return;
        }
        try {
            await deleteUpload(id);
            if (uploadId === id) {
                clearUpload();
            }
            // Refresh history
            let email = null;
            try {
                const user = await account.get();
                email = user.email;
            } catch (err) {}
            const list = await listUploads(email);
            setHistory(list);
        } catch (err) {
            alert(err.message || "Failed to delete upload.");
        }
    }

    return (
        <>
            <div className="container">
                <div className="dotted-container">
                    <div className="content">
                        <h1>Upload your CSV Files here</h1>
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            disabled={status === "uploading"}
                        />
                        {status === "uploading" && <p>Uploading and processing...</p>}
                    </div>
                </div>
            </div>

            <div className="error-message-container">
                {status === "error" && (
                    <div className="error-message">
                        <div className="message">
                            <img src={cross} alt="" />
                            <div className="message-content">
                                <h3>VALIDATION ERROR</h3>
                                <p>{errorText}</p>
                            </div>
                        </div>
                    </div>
                )}

                {status === "success" && result && (
                    <div className="success-message">
                        <div className="message">
                            <img src={tick} alt="" />
                            <div className="message-content">
                                <h3>INGESTION COMPLETE</h3>
                                <p>
                                    {result.rows_ingested} rows processed
                                    {result.rows_flagged > 0
                                        ? ` (${result.rows_flagged} rows flagged/cleaned)`
                                        : ""}
                                </p>
                                <button onClick={navigateToDashboard}>VIEW ANALYTICS</button>
                                <br />
                                <button onClick={navigateToExport}>VIEW CLEANED DATASET</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* History Section */}
            <div className="error-message-container" style={{ marginTop: "40px", padding: "20px" }}>
                <h2 style={{ fontFamily: "Space Grotesk, sans-serif", borderBottom: "2px solid black", paddingBottom: "10px", marginBottom: "20px" }}>
                    YOUR UPLOAD HISTORY
                </h2>
                
                {loadingHistory ? (
                    <p>Loading history...</p>
                ) : history.length === 0 ? (
                    <p style={{ color: "#666" }}>No files uploaded yet.</p>
                ) : (
                    <div className="table-container">
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr>
                                    <th style={{ padding: "10px", textAlign: "left" }}>File Name</th>
                                    <th style={{ padding: "10px", textAlign: "left" }}>Upload Date</th>
                                    <th style={{ padding: "10px", textAlign: "left" }}>Status</th>
                                    <th style={{ padding: "10px", textAlign: "right" }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((item) => (
                                    <tr key={item.id}>
                                        <td style={{ padding: "10px", fontWeight: "bold" }}>{item.file_name}</td>
                                        <td style={{ padding: "10px" }}>
                                            {new Date(item.upload_date).toLocaleString(undefined, {
                                                dateStyle: "medium",
                                                timeStyle: "short"
                                            })}
                                        </td>
                                        <td style={{ padding: "10px" }}>
                                            <span style={{
                                                padding: "4px 8px",
                                                border: "1px solid black",
                                                backgroundColor: item.status === "cleaned" ? "#e6ffe6" : item.status === "failed" ? "#ffe6e6" : "#fffde6",
                                                fontWeight: "bold",
                                                fontSize: "11px",
                                                textTransform: "uppercase"
                                            }}>
                                                {item.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: "10px", textAlign: "right" }}>
                                            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                                                {item.status === "cleaned" && (
                                                    <button
                                                        onClick={() => handleSelectHistory(item.id)}
                                                        className="upload-btn"
                                                        style={{ padding: "6px 12px", fontSize: "12px", boxShadow: "1px 2px 0px 0px black", display: "inline-block" }}
                                                    >
                                                        VIEW
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => handleDeleteHistory(item.id)}
                                                    className="upload-btn"
                                                    style={{
                                                        padding: "6px 12px",
                                                        fontSize: "12px",
                                                        backgroundColor: "#BB1C1C",
                                                        boxShadow: "1px 2px 0px 0px black",
                                                        display: "inline-block"
                                                    }}
                                                >
                                                    DELETE
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </>
    );
}

export default Upload;
