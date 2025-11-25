import React from 'react';
import { FiFile, FiCheckCircle } from 'react-icons/fi';

interface FileMessageProps {
  fileName: string;
  fileSize?: number;
  rowsProcessed?: number;
  timestamp: Date;
}

const FileMessage: React.FC<FileMessageProps> = ({
  fileName,
  fileSize,
  rowsProcessed,
  timestamp,
}) => {
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return 'Unknown size';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatTime = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const seconds = Math.floor(diff / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return new Date(date).toLocaleDateString();
  };

  return (
    <div className="mb-6 flex items-start">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3 max-w-md">
        {/* Icon */}
        <div className="flex-shrink-0 mt-1">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <FiFile className="text-green-600 text-xl" />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Success indicator */}
          <div className="flex items-center gap-2 mb-2">
            <FiCheckCircle className="text-green-600 text-sm" />
            <span className="text-xs font-medium text-green-700">File Uploaded Successfully</span>
          </div>

          {/* File name */}
          <div className="text-sm font-semibold text-navy-700 mb-1 truncate" title={fileName}>
            {fileName}
          </div>

          {/* File details */}
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-gray-600">
            {fileSize && (
              <span>{formatFileSize(fileSize)}</span>
            )}
            {rowsProcessed && (
              <span>• {rowsProcessed.toLocaleString()} rows</span>
            )}
            <span>• {formatTime(timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileMessage;
