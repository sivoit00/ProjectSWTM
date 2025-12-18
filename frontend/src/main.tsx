import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import keycloak from "./keycloak";
import "./index.css";

keycloak
  .init({ onLoad: "login-required", checkLoginIframe: false })
  .then((authenticated) => {
    if (!authenticated) {
      keycloak.login();
    } else {
      console.log("Authenticated");

      fetch("http://localhost:8000/customers/me", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${keycloak.token}`,
          "Content-Type": "application/json"
        }
      })
      .then(response => {
        if (response.ok) console.log("Backend User Sync: Success");
        else console.error("Backend User Sync: Failed", response.status);
      })
      .catch(err => console.error("Backend User Sync: Network Error", err))

      createRoot(document.getElementById("root")!).render(
        <StrictMode>
          <BrowserRouter>
            <App />
          </BrowserRouter>
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
