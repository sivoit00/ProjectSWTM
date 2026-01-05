import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import keycloak from "./keycloak";
import { ThemeProvider } from "./context/ThemeContext";
import "./index.css";

keycloak
  .init({ onLoad: "login-required", checkLoginIframe: false })
  .then((authenticated) => {
    if (!authenticated) {
      keycloak.login();
    } else {
      console.log("Authenticated");
      createRoot(document.getElementById("root")!).render(
        <StrictMode>
          <ThemeProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ThemeProvider>
        </StrictMode>
      );
    }
  })
  .catch((err) => {
    console.error("Keycloak init error:", err);
  });
setInterval(() => {
  keycloak.updateToken(60).catch(() => keycloak.login());
}, 60000);
