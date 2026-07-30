import square from "../assets/square.png";
import circle from "../assets/circle.png";
import triangle from "../assets/triangle.png";

import Loader from "../loader";

function Body() {
    return (
        <div className="layout">
            <div className="top">
            </div>
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
                        <button className="upload-btn">
                            <svg stroke="currentColor" fill="currentColor" strokeWidth="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path fill="none" d="M0 0h24v24H0z"></path><path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"></path></svg>
                            UPLOAD CSV OR EXCEL FILE
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

export default Body;