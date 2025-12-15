import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import OnboardingLayout from "./layouts/OnboardingLayout";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Profile from "./pages/Profile";
import Onboarding from "./pages/Onboarding";
import Start from "./pages/Start";

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Start />} />
        <Route path="/home" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      <Route element={<OnboardingLayout />}>
        <Route path="/onboarding" element={<Onboarding />} />
      </Route>
    </Routes>
  );
}