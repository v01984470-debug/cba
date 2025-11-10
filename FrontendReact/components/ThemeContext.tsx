import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Check localStorage first, then system preference, default to dark
    const storedTheme = localStorage.getItem("theme") as Theme | null;
    if (storedTheme && (storedTheme === "light" || storedTheme === "dark")) {
      return storedTheme;
    }
    // Check system preference
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: light)").matches
    ) {
      return "light";
    }
    return "dark"; // Default to dark mode
  });

  useEffect(() => {
    const root = document.documentElement;
    // Apply theme to html element for Tailwind's class-based dark mode
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    // Store in localStorage
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Listen for system theme changes (optional enhancement)
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-update if user hasn't set a preference
      const storedTheme = localStorage.getItem("theme");
      if (!storedTheme) {
        setThemeState(e.matches ? "dark" : "light");
      }
    };
    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  const toggleTheme = () => {
    setThemeState((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  };

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
