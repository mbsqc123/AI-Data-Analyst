import React from 'react';
import { FiFile } from 'react-icons/fi';
import { AiOutlineCheckCircle } from 'react-icons/ai';

interface FileMessageProps {
  fileName: string;
  fileSize: number;
  rowsProcessed?: number;
  timestamp: Date;
  dataSourceId?: string;
  tableName?: string;
}

export const FileMessage: React.FC<FileMessageProps> = ({
  fileName,
  fileSize,
  rowsProcessed,
  timestamp,
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="file-upload-message bg-green-50 border border-green-200 rounded-lg p-4 mb-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center">
        <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mr-3 flex-shrink-0">
          <FiFile className="text-2xl text-green-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center mb-1">
            <AiOutlineCheckCircle className="text-green-600 mr-2 flex-shrink-0" />
            <span className="font-semibold text-gray-800">File Uploaded Successfully</span>
          </div>
          <div className="text-sm text-gray-700 font-medium truncate" title={fileName}>
            {fileName}
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
            <span>{formatFileSize(fileSize)}</span>
            {rowsProcessed !== undefined && (
              <>
                <span>•</span>
                <span>{rowsProcessed.toLocaleString()} rows</span>
              </>
            )}
          </div>
        </div>
        <div className="text-xs text-gray-400 ml-3 flex-shrink-0">
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
};

export default FileMessage;
