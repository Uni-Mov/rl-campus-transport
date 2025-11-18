import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";
import { AuthProvider } from "../context/auth-context";
import { RouterProvider } from "../context/router-context";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <RouterProvider>
          <App />
        </RouterProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
