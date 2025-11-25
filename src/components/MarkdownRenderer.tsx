import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Headings
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold mb-4 mt-6 text-navy-800">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-bold mb-3 mt-5 text-navy-800">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold mb-2 mt-4 text-navy-700">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-base font-semibold mb-2 mt-3 text-navy-700">{children}</h4>
        ),

        // Paragraphs with spacing
        p: ({ children }) => (
          <p className="mb-4 leading-relaxed text-navy-600">{children}</p>
        ),

        // Lists
        ul: ({ children }) => (
          <ul className="list-disc list-inside mb-4 space-y-2 ml-4">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside mb-4 space-y-2 ml-4">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="ml-4 text-navy-600">{children}</li>
        ),

        // Bold and italic
        strong: ({ children }) => (
          <strong className="font-semibold text-navy-800">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="italic text-navy-600">{children}</em>
        ),

        // Code blocks
        code: ({ inline, children }: any) =>
          inline ? (
            <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-navy-700">
              {children}
            </code>
          ) : (
            <code className="block bg-gray-900 text-white p-4 rounded-lg my-4 overflow-x-auto font-mono text-sm">
              {children}
            </code>
          ),

        // Pre (for code blocks)
        pre: ({ children }) => (
          <pre className="bg-gray-900 text-white p-4 rounded-lg my-4 overflow-x-auto">
            {children}
          </pre>
        ),

        // Links
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            {children}
          </a>
        ),

        // Blockquotes
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4 text-gray-600">
            {children}
          </blockquote>
        ),

        // Tables
        table: ({ children }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full border-collapse border border-gray-300">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-gray-100">{children}</thead>
        ),
        tbody: ({ children }) => (
          <tbody>{children}</tbody>
        ),
        tr: ({ children }) => (
          <tr className="border-b border-gray-300">{children}</tr>
        ),
        th: ({ children }) => (
          <th className="border border-gray-300 px-4 py-2 text-left font-semibold text-navy-800">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="border border-gray-300 px-4 py-2 text-navy-600">
            {children}
          </td>
        ),

        // Horizontal rule
        hr: () => (
          <hr className="my-6 border-t border-gray-300" />
        ),
      }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
