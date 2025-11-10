import React, { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-white dark:bg-gray-800 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 border border-red-200 dark:border-red-800">
            <h1 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
              Something went wrong
            </h1>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              An error occurred while rendering this page. Please try refreshing
              or go back to the dashboard.
            </p>
            {this.state.error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-4 mb-4">
                <p className="text-sm font-mono text-red-800 dark:text-red-300">
                  {this.state.error.message}
                </p>
              </div>
            )}
            <div className="flex gap-4">
              <button
                onClick={() => (window.location.href = "/#/")}
                className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black rounded-md font-semibold"
              >
                Go to Dashboard
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md font-semibold"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

