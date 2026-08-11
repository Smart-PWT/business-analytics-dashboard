import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboard } from "../api/client";
import { useUpload } from "../context/UploadContext";
import Loader from "../components/Loader.jsx";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";

import square from "../assets/square.png";
import circle from "../assets/circle.png";
import triangle from "../assets/triangle.png";

function Dashboard() {
    const navigate = useNavigate();
    const { uploadId } = useUpload();
    
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (uploadId) {
            setLoading(true);
            getDashboard(uploadId)
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
                <div className="top"></div>
                <div className="body">
                    <div className="left">
                        <h1>SYSTEM DORMANT</h1>
                        <p>Waiting for the data input. The architectural grid requires a file to generate the predictive landscape</p>
                    </div>
                    <div className="middle">
                        <Loader />
                        <div className="middle-content">
                            <h2>ENGINE OFFLINE</h2>
                            <p>Upload your first file to see your dashboard<br/>come to life.</p>
                            <button className="upload-btn" onClick={() => navigate("/upload")}>
                                <svg stroke="currentColor" fill="currentColor" strokeWidth="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path fill="none" d="M0 0h24v24H0z"></path><path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"></path></svg>
                                UPLOAD CSV FILE
                            </button>
                        </div>
                    </div>
                    <div className="right">
                        <p>Symbology</p>
                        <hr />
                        <div className="list">
                            <li><img src={square} />Market Stabilty</li>
                            <li><img src={circle} />Risk Variance</li>
                            <li><img src={triangle} />Critical Assets</li>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (loading) {
        return <div className="layout"><div className="middle"><Loader /><p>Loading Insights...</p></div></div>;
    }

    if (error) {
        return <div className="layout"><div className="middle"><p className="error">{error}</p></div></div>;
    }

    if (!data) return null;

    return (
        <div className="dashboard-container active">
            <div className="kpi-grid">
                <div className="kpi-card">
                    <h3>Total Revenue</h3>
                    <p>${data.kpi_summary.total_revenue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                </div>
                <div className="kpi-card">
                    <h3>Average Order Value</h3>
                    <p>${data.kpi_summary.average_order_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                </div>
                <div className="kpi-card">
                    <h3>Total Pending</h3>
                    <p>${data.kpi_summary.total_pending_dues.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                </div>
                <div className="kpi-card">
                    <h3>Total Orders</h3>
                    <p>{data.kpi_summary.total_orders}</p>
                </div>
            </div>

            <div className="charts-grid">
                <div className="chart-card">
                    <h3>Sales Trend</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={data.sales_trend}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#000" vertical={false} />
                                <XAxis dataKey="date" stroke="#000" tick={{ fill: '#000', fontWeight: 'bold', fontSize: 12 }} axisLine={{ stroke: '#000', strokeWidth: 2 }} tickLine={{ stroke: '#000', strokeWidth: 2 }} />
                                <YAxis stroke="#000" tick={{ fill: '#000', fontWeight: 'bold', fontSize: 12 }} axisLine={{ stroke: '#000', strokeWidth: 2 }} tickLine={{ stroke: '#000', strokeWidth: 2 }} />
                                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '2px solid black', color: '#000', borderRadius: '0px', boxShadow: '4px 4px 0px 0px black' }} itemStyle={{ color: '#000', fontWeight: 'bold' }} />
                                <Legend wrapperStyle={{ paddingTop: '10px', fontWeight: 'bold' }} />
                                <Line type="stepAfter" dataKey="total_sales" name="Total Sales" stroke="#0b2d69" strokeWidth={3} dot={{ r: 4, fill: '#fff', stroke: '#000', strokeWidth: 2 }} activeDot={{ r: 6, fill: '#000' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="chart-card">
                    <h3>Top Products by Revenue</h3>
                    <div className="chart-wrapper">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.top_products}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#000" vertical={false} />
                                <XAxis dataKey="item_name" stroke="#000" tick={{ fill: '#000', fontWeight: 'bold', fontSize: 12 }} axisLine={{ stroke: '#000', strokeWidth: 2 }} tickLine={{ stroke: '#000', strokeWidth: 2 }} />
                                <YAxis stroke="#000" tick={{ fill: '#000', fontWeight: 'bold', fontSize: 12 }} axisLine={{ stroke: '#000', strokeWidth: 2 }} tickLine={{ stroke: '#000', strokeWidth: 2 }} />
                                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '2px solid black', color: '#000', borderRadius: '0px', boxShadow: '4px 4px 0px 0px black' }} cursor={{fill: '#F0EDEC'}} />
                                <Bar dataKey="revenue" name="Revenue" fill="#0b2d69" stroke="#000" strokeWidth={2} radius={[0, 0, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="tables-grid">
                <div className="table-card">
                    <h3>Party Wise Dues</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Party Name</th>
                                    <th>Pending Amount</th>
                                    <th>Overdue Days</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.party_wise_dues.map((party, idx) => (
                                    <tr key={idx}>
                                        <td>{party.party_name}</td>
                                        <td className="amount">${party.amount_pending.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                        <td>{party.overdue_days} <span className="days-label">days</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;