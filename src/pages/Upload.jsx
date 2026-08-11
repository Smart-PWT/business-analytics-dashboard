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

            <div className="error-message-container">
                <div className="error-message">
                    <div className="message">
                        <img src={cross} alt="" />
                        <div className="message-content">
                            <h3>VALIDATION ERROR</h3>
                            <p>Wrong file type or missing required columns</p>
                        </div>
                    </div>
                </div>

                <div className="success-message">
                    <div className="message">
                        <img src={tick} alt="" />
                        <div className="message-content">
                            <h3>INGESTION COMPLETE</h3>
                            <p>File Processed</p>
                            <button>VIEW CLEANED DATASET</button>
                        </div>
                    </div>
                </div>
            </div>
            <hr />
            <h1 className="message">
                THANKS FOR CHOOSING OUR SERVICES...
            </h1>
        </>
    );
}

export default Upload;