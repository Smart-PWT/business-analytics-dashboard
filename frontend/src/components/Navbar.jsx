import { Link, useNavigate } from "react-router-dom";
import logo from "../assets/withoutbg.png";
import { useState, useEffect } from "react";
import { account } from "../config/appwrite";
import { useUpload } from "../context/UploadContext";

function Navbar() {
    const [username, setUsername] = useState(null);
    const { clearUpload } = useUpload();
    const navigate = useNavigate();

    useEffect(() => {
        account.get()
            .then((user) => {
                setUsername(user);
            })
            .catch(() => {
                setUsername(null);
            });
    }, []);

    const handleLogout = async () => {
        try {
            await account.deleteSession("current");
        } catch (err) {
            console.error("Failed to delete Appwrite session", err);
        }
        clearUpload(); // Clear current session storage upload info so next user doesn't see it
        setUsername(null);
        navigate("/login");
    };

    return (
        <div className="navbar">
            <div className="logo">
                <img src={logo} alt="" />
            </div>
            <div className="links">
                <ul>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                    <li><Link to="/upload">Upload</Link></li>
                    <li><Link to="/predictions">Predictions</Link></li>
                    <li><Link to="/export">Export</Link></li>
                </ul>
            </div>
            
            <div className="profile" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <h5>Welcome, {username?.name}</h5>
                <Link to="/login" className="navbar-account" title="Account">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
                    </svg>
                </Link>
                {username && (
                    <button 
                        onClick={handleLogout}
                        className="upload-btn"
                        style={{
                            padding: "6px 12px",
                            fontSize: "12px",
                            backgroundColor: "#BB1C1C",
                            boxShadow: "1px 2px 0px 0px black",
                            border: "2px solid black",
                            fontWeight: "bold",
                            color: "white",
                            cursor: "pointer",
                            display: "inline-block"
                        }}
                    >
                        LOGOUT
                    </button>
                )}
            </div>
        </div>
    );
}

export default Navbar;