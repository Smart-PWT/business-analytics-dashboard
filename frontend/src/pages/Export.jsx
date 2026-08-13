import { useState, useEffect, Fragment } from "react";
import { useNavigate } from "react-router-dom";
import { getCleanedPreview, exportCleanedCsv } from "../api/client";
import { useUpload } from "../context/UploadContext";
import Loader from "../components/Loader.jsx";

function Export() {
    const navigate = useNavigate();
    const { uploadId, clearUpload } = useUpload();

    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notFound, setNotFound] = useState(false);
    const [error, setError] = useState(null);
    const [exporting, setExporting] = useState(false);
    const [exportError, setExportError] = useState(null);

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
                    // If the server says "not found" the uploadId is stale
                    // (e.g. backend restarted). Clear it so the user is
                    // prompted to re-upload rather than seeing a raw error.
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

    if (!uploadId || notFound) {
        return (
            <div className="layout">
                <div className="middle" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                    <Loader />
                    <div className="middle-content">
                        <h2>NO ACTIVE DATA</h2>
                        <p>
                            {notFound
                                ? "Your previous session has expired. Please upload a new file."
                                : "Upload a file first to export your cleaned dataset."}
                        </p>
                        <button className="upload-btn" onClick={() => navigate("/Upload")}>
                            UPLOAD CSV FILE
                        </button>
                    </div>
                </div>
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
                                                ${row.unit_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                ${row.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                ${row.amount_paid.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="amount">
                                                ${row.amount_pending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                <button className="upload-btn export-secondary-btn" onClick={() => navigate("/")}>
                    EXPLORE DATASET MORE
                </button>
                <br />
                <button className="upload-btn export-primary-btn" onClick={handleExport} disabled={exporting}>
                    {exporting ? "PREPARING EXPORT..." : "EXPORT CLEANED CSV"}
                </button>
            </div>

            {exportError && <p className="error export-error">{exportError}</p>}
        </div>
    );
}

export default Export;