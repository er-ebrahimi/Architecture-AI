import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./app/dashboard/page";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
