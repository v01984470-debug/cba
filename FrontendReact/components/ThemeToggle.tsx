import React from "react";
import { useTheme } from "./ThemeContext";

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center p-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      {/* Toggle Switch Container */}
      <div className="relative w-14 h-7 bg-gray-300 dark:bg-gray-600 rounded-full transition-colors duration-200">
        {/* Toggle Switch Slider */}
        <div
          className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-200 ${
            theme === "dark" ? "translate-x-7" : "translate-x-0"
          }`}
        >
          {/* Icons inside the toggle */}
          <div className="flex items-center justify-center h-full w-full">
            {theme === "dark" ? (
              <span className="text-xs">🌙</span>
            ) : (
              <span className="text-xs">☀️</span>
            )}
          </div>
        </div>
      </div>
      {/* Text label */}
      <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:inline">
        {theme === "dark" ? "Dark" : "Light"}
      </span>
    </button>
  );
};
