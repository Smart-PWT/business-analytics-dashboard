import tick from "../assets/tick.png";
import cross from "../assets/cross.png";

function Upload() {
    return (
        <>
            <div className="container">
                <div className="dotted-container">
                    <div className="content">
                        <h1>Upload your CSV and Excel Files here</h1>
                        <input type="file" />
                    </div>
                </div>
            </div>

            <div className="error-message">
                <div className="message">
                    <img src={cross} alt="" />
                    <div className="message-content">
                        <h3>VALIDATION ERROR</h3>
                        <p>Missing required Columns</p>
                    </div>
                </div>
            </div>

            <div className="success-message">
                <div className="message">
                    <img src={tick} alt="" />
                    <div className="message-content">
                        <h3>INGESTION COMPLETE</h3>
                        <p>Missing required Columns</p>
                        <button>VIEW CLEANED DATASET</button>
                    </div>
                </div>
            </div>
            <hr />
        </>
    );
}

export default Upload;