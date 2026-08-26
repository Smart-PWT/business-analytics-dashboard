import { useState, useEffect, Fragment } from "react";
import { useNavigate } from "react-router-dom";
import { getCleanedPreview, exportCleanedCsv, listUploads, deleteUpload } from "../api/client";
import { useUpload } from "../context/UploadContext";
import Loader from "../components/Loader.jsx";
import { account } from "../config/appwrite";

function Export() {
    const navigate = useNavigate();
    const { uploadId, setUploadId, clearUpload } = useUpload();

    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notFound, setNotFound] = useState(false);
    const [error, setError] = useState(null);
    const [exporting, setExporting] = useState(false);
    const [exportError, setExportError] = useState(null);
    const [history, setHistory] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(false);

    useEffect(() => {
        if (uploadId) {
            setLoading(true);
            setNotFound(false);
            setError(null);
            getCleanedPreview(uploadId, 10)
                .then((res) => {
                    setPreview(res);
                    setLoading(false);
                })
                .catch((err) => {
                    if (
                        err.message?.toLowerCase().includes("not found") ||
                        err.message?.toLowerCase().includes("upload not found")
                    ) {
                        clearUpload();
                        setNotFound(true);
                    } else {
                        setError(err.message);
                    }
                    setLoading(false);
                });
        }
    }, [uploadId]);

    // Fetch user history on component mount or when uploadId changes
    useEffect(() => {
        async function fetchHistory() {
            setLoadingHistory(true);
            try {
                let email = null;
                try {
                    const user = await account.get();
                    email = user.email;
                } catch (err) {}
                const list = await listUploads(email);
                setHistory(list);
            } catch (err) {
                console.error("Error fetching history:", err);
            } finally {
                setLoadingHistory(false);
            }
        }
        fetchHistory();
    }, [uploadId]);

    async function handleExport() {
        setExporting(true);
        setExportError(null);
        try {
            await exportCleanedCsv(uploadId);
        } catch (err) {
            setExportError(err.message);
        } finally {
            setExporting(false);
        }
    }

    function handleSelectHistory(id) {
        setUploadId(id);
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

    const renderHistorySection = () => (
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
    );

    if (!uploadId || notFound) {
        return (
            <div className="dashboard-container active export-page">
                <div className="layout" style={{ minHeight: "auto", border: "1.5px solid rgb(80, 79, 79)", backgroundColor: "#B9B7B6", padding: "40px 20px" }}>
                    <div className="middle" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                        <Loader />
                        <div className="middle-content" style={{ textAlign: "center" }}>
                            <h2>NO ACTIVE DATA</h2>
                            <p>
                                {notFound
                                    ? "Your previous session has expired. Please upload a new file."
                                    : "Upload a file first to export your cleaned dataset."}
                            </p>
                            <button className="upload-btn" onClick={() => navigate("/Upload")} style={{ margin: "0 auto" }}>
                                UPLOAD CSV FILE
                            </button>
                        </div>
                    </div>
                </div>
                {renderHistorySection()}
            </div>
        );
    }

    if (loading) {
        return (
            <div className="layout">
                <div className="middle" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                    <Loader />
                    <p>Loading Dataset Preview...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="layout">
                <div className="middle" style={{ width: "100%", display: "flex", justifyContent: "center" }}>
                    <p className="error">{error}</p>
                </div>
            </div>
        );
    }

    if (!preview) return null;

    const rows = [
        ...preview.first.map((r) => ({ ...r, __group: "first" })),
        ...preview.middle.map((r) => ({ ...r, __group: "middle" })),
        ...preview.last.map((r) => ({ ...r, __group: "last" })),
    ];

    const groupLabel = {
        first: "FIRST 10 ROWS",
        middle: "RANDOM 10 FROM MIDDLE",
        last: "LAST 10 ROWS",
    };

    return (
        <div className="dashboard-container active export-page">
            <h1 className="page-title">Export Cleaned Dataset</h1>
            <p className="page-subtitle">
                <br />
                Total Rows: {preview.total_rows.toLocaleString()}  
                <br /><br />
            </p>

            <div className="table-card export-preview-card">
                <h3>Dataset Preview ({rows.length} of {preview.total_rows.toLocaleString()} rows)</h3>
                <div className="export-scroller">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Party</th>
                                <th>Item</th>
                                <th>Qty</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                                <th>Paid</th>
                                <th>Pending</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row, idx) => {
                                const isSectionStart = idx === 0 || rows[idx - 1].__group !== row.__group;
                                return (
                                    <Fragment key={idx}>
                                        {isSectionStart && (
                                            <tr className="export-section-row">
                                                <td colSpan={9}>{groupLabel[row.__group]}</td>
                                            </tr>
                                        )}
                                        <tr>
                                            <td>{row.transaction_date}</td>
                                            <td>{row.party_name}</td>
                                            <td>{row.item_name}</td>
                                            <td>{row.quantity}</td>
                                            <td className="amount">
                                                Rs. {row.unit_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                Rs. {row.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                Rs. {row.amount_paid.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                Rs. {row.amount_pending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td>{row.transaction_type}</td>
                                        </tr>
                                    </Fragment>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
            <br />
            <div className="export-actions">
                <button className="upload-btn export-secondary-btn" onClick={() => navigate("/dashboard")}>
                    EXPLORE DATASET MORE
                </button>
                <br />
                <button className="upload-btn export-primary-btn" onClick={handleExport} disabled={exporting}>
                    {exporting ? "PREPARING EXPORT..." : "EXPORT CLEANED CSV"}
                </button>
            </div>

            {exportError && <p className="error export-error">{exportError}</p>}
            
            {renderHistorySection()}
        </div>
    );
}

export default Export;