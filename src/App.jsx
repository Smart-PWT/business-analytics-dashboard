import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./navbar"
import Dashboard from "./pages/Dashboard.jsx";
import Upload from "./pages/Upload.jsx";
import Predictions from "./pages/Predictions.jsx";
import Export from "./pages/Export.jsx";



function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/Upload" element={<Upload />} />
        <Route path="/Predictions" element={<Predictions />} />
        <Route path="/Export" element={<Export />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
