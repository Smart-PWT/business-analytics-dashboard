import { Link } from "react-router-dom";
import logo from "./assets/withoutbg.png";

function Navbar() {
    return (
        <div className="navbar">
            <div className="logo">
                <img src={logo} alt="" />
            </div>
            <div className="links">
                <ul>
                    <li><Link to="/">Dashboard</Link></li>
                    <li><Link to="/Upload">Upload</Link></li>
                    <li><Link to="/Predictions">Predictions</Link></li>
                    <li><Link to="/Export">Export</Link></li>
                </ul>
            </div>
        </div>
    );
}

export default Navbar;