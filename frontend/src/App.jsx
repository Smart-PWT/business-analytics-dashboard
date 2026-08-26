import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar.jsx"
import Dashboard from "./pages/Dashboard.jsx";
import Upload from "./pages/Upload.jsx";
import Predictions from "./pages/Predictions.jsx";
import Export from "./pages/Export.jsx";
import Signup from  "./pages/signup.jsx";
import Login from "./pages/login.jsx";
import Layout from "./layout.jsx";
import NotFound from "./components/NotFound.jsx";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth pages — no Navbar */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* App pages — with Navbar */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/export" element={<Export />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>

  );
}

export default App;
