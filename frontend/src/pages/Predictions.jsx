import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getPredictions } from "../api/client";
import { useUpload } from "../context/UploadContext";
import Loader from "../components/Loader.jsx";

function Predictions() {
    const navigate = useNavigate();
    const { uploadId } = useUpload();
    
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (uploadId) {
            setLoading(true);
            getPredictions(uploadId)
                .then(res => {
                    setData(res);
                    setLoading(false);
                })
                .catch(err => {
                    setError(err.message);
                    setLoading(false);
                });
        }
    }, [uploadId]);

    if (!uploadId) {
        return (
            <div className="layout">
                <div className="middle" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <Loader />
                    <div className="middle-content">
                        <h2>NO ACTIVE DATA</h2>
                        <p>Upload a file first to generate predictions and forecasts.</p>
                        <button className="upload-btn" onClick={() => navigate("/upload")}>
                            UPLOAD CSV FILE
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (loading) {
        return <div className="layout"><div className="middle" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}><Loader /><p>Running Predictive Models...</p></div></div>;
    }

    if (error) {
        return <div className="layout"><div className="middle" style={{ width: '100%', display: 'flex', justifyContent: 'center'}}><p className="error">{error}</p></div></div>;
    }

    if (!data) return null;

    return (
        <div className="dashboard-container active predictions-page">
            <h1 className="page-title">Predictive Intelligence</h1>
            <p className="page-subtitle">AI-driven forecasts and risk assessment based on your historical data.</p>
            
            <div className="predictions-grid">
                <div className="prediction-section">
                    <div className="section-header">
                        <h3>Demand Forecast (30 Days)</h3>
                        <p>Expected unit sales for the upcoming month.</p>
                    </div>
                    <div className="forecast-cards">
                        {data.demand_forecast.map((item, idx) => (
                            <div className="forecast-card" key={idx}>
                                <div className="item-name">{item.item_name}</div>
                                <div className="predicted-units">
                                    <span className="value">{Math.round(item.predicted_units)}</span>
                                    <span className="label">units</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="prediction-section">
                    <div className="section-header">
                        <h3>Payment Risk Assessment</h3>
                        <p>Risk of late payments based on party history.</p>
                    </div>
                    <div className="risk-list">
                        {data.payment_risk.map((party, idx) => {
                            const riskClass = party.risk_label.toLowerCase();
                            return (
                                <div className="risk-item" key={idx}>
                                    <div className="party-name">{party.party_name}</div>
                                    <div className={`risk-badge ${riskClass}`}>
                                        {party.risk_label} Risk
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Predictions;