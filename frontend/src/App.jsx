import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar.jsx"
import Dashboard from "./pages/Dashboard.jsx";
import Upload from "./pages/Upload.jsx";
import Predictions from "./pages/Predictions.jsx";
import Export from "./pages/Export.jsx";
import Layout from "./layout.jsx";
import NotFound from "./components/NotFound.jsx";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element = {<Layout />}>
          <Route path="/" element={<Dashboard />}></Route>
          <Route path="/Upload" element={<Upload />}></Route>
          <Route path="/Predictions" element={<Predictions />}></Route>
          <Route path="/Export" element={<Export />}></Route>
          <Route path="*" element={<NotFound />}></Route>
        </Route>
      </Routes>
    </BrowserRouter>

  );
}

export default App;