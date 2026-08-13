import { useState } from "react";
import { useNavigate } from "react-router-dom";
import tick from "../assets/tick.png";
import cross from "../assets/cross.png";
import { uploadFile } from "../api/client";
import { useUpload } from "../context/UploadContext";

function Upload() {
    const [status, setStatus] = useState("idle");
    const [errorText, setErrorText] = useState("");
    const [result, setResult] = useState(null);

    const { setUploadId } = useUpload();
    const navigate = useNavigate();

    async function handleFileChange(event) {
        const file = event.target.files[0];
        if (!file) return;

        setStatus("uploading");
        setErrorText("");

        try {
            const data = await uploadFile(file);
            setResult(data);
            setUploadId(data.upload_id, data);
            setStatus("success");
        } catch (err) {
            setErrorText(err.message);
            setStatus("error");
        }
    }

    function navigateToDashboard() {
        navigate("/");
    }

    function navigateToExport(){
        navigate("/export");
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
        </>
    );
}

export default Upload;