import { Link } from "react-router-dom";
import logo from "../assets/withoutbg.png";

function Navbar() {
    return (
        <div className="navbar">
            <div className="logo">
                <img src={logo} alt="" />
            </div>
            <div className="links">
                <ul>
                    <li><Link to="/">Dashboard</Link></li>
                    <li><Link to="/upload">Upload</Link></li>
                    <li><Link to="/predictions">Predictions</Link></li>
                    <li><Link to="/export">Export</Link></li>
                </ul>
            </div>
        </div>
    );
}

export default Navbar;