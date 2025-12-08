import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Chat from "./pages/Chat/index";
import { NotificationProvider } from "./context/NotificationContext";


export default function App() {
  return (
    <NotificationProvider>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
        </Route>
      </Routes>
    </NotificationProvider>
  );
}
