"use client";

import React from 'react';
import { APIError } from '@/lib/api';

interface ErrorAlertProps {
  error: Error | APIError | string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

/**
 * Error Alert Component
 * Displays user-friendly error messages with retry option
 */
export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  onDismiss,
}) => {
  const getErrorMessage = (): string => {
    if (typeof error === 'string') {
      return error;
    }

    if (error instanceof APIError) {
      // Provide user-friendly messages for common errors
      switch (error.statusCode) {
        case 0:
          return 'Unable to connect to the server. Please check your internet connection.';
        case 400:
          return 'Invalid request. Please check your input and try again.';
        case 401:
          return 'Authentication required. Please log in and try again.';
        case 403:
          return 'You do not have permission to perform this action.';
        case 404:
          return 'The requested resource was not found.';
        case 408:
          return 'Request timeout. The server took too long to respond.';
        case 429:
          return 'Too many requests. Please wait a moment and try again.';
        case 500:
          return 'Server error. Our team has been notified.';
        case 502:
        case 503:
        case 504:
          return 'Service temporarily unavailable. Please try again in a moment.';
        default:
          return error.message || 'An unexpected error occurred.';
      }
    }

    return error.message || 'An unexpected error occurred.';
  };

  const getErrorTitle = (): string => {
    if (error instanceof APIError) {
      if (error.statusCode === 0) return 'Connection Error';
      if (error.statusCode && error.statusCode >= 500) return 'Server Error';
      if (error.statusCode === 408) return 'Timeout Error';
      if (error.statusCode === 429) return 'Rate Limit Exceeded';
    }
    return 'Error';
  };

  return (
    <div className="rounded-lg bg-red-50 border border-red-200 p-4 shadow-sm">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            {getErrorTitle()}
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{getErrorMessage()}</p>
          </div>
          {(onRetry || onDismiss) && (
            <div className="mt-4 flex gap-3">
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                >
                  <svg
                    className="mr-1.5 h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Try Again
                </button>
              )}
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                >
                  Dismiss
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorAlert;

// Made with Bob