import React from "react";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Report from "./pages/Report";
import Simulation from "./pages/Simulation";
import { ToastProvider } from "./components/Toast";
import { ThemeProvider } from "./components/ThemeContext";
import { ThemeToggle } from "./components/ThemeToggle";
import ErrorBoundary from "./components/ErrorBoundary";

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans">
            <header className="bg-gray-100 dark:bg-black shadow-md border-b border-gray-200 dark:border-gray-800">
              <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  <div className="flex items-center">
                    <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-amber-500">
                      Payment Refund Investigations
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </header>
            <main className="container mx-auto p-4 sm:p-6 lg:p-8 bg-white dark:bg-gray-800 min-h-[calc(100vh-4rem)]">
              <HashRouter>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route
                    path="/dashboard"
                    element={<Navigate to="/" replace />}
                  />
                  <Route path="/report/:runId" element={<Report />} />
                  <Route path="/simulation" element={<Simulation />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </HashRouter>
            </main>
          </div>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
