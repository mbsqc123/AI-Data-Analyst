interface HighlightTextProps {
    text: string;
  }

  const HighlightText: React.FC<HighlightTextProps> = ({ text }) => {
    // Split text into paragraphs and process each one
    const paragraphs = text.split(/\n\n+/);

    const processLine = (line: string, lineIndex: number) => {
      // Check if it's a bullet point
      const isBullet = line.trim().match(/^[-•*]\s+/);

      // Split by bold markers
      const parts = line.split(/(\*\*.*?\*\*)/g);

      const processedParts = parts.map((part, index) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          // Remove the asterisks and highlight the text
          const highlightedText = part.slice(2, -2);
          return (
            <span key={index} className="font-bold text-navy-700">
              {highlightedText}
            </span>
          );
        }
        return <span key={index}>{part}</span>;
      });

      // If it's a bullet point, render with bullet styling
      if (isBullet) {
        const content = line.replace(/^[-•*]\s+/, '');
        const processedContent = content.split(/(\*\*.*?\*\*)/g).map((part, index) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            const highlightedText = part.slice(2, -2);
            return (
              <span key={index} className="font-bold text-navy-700">
                {highlightedText}
              </span>
            );
          }
          return <span key={index}>{part}</span>;
        });

        return (
          <li key={lineIndex} className="ml-6 mb-1 text-navy-600 leading-relaxed">
            {processedContent}
          </li>
        );
      }

      return (
        <span key={lineIndex} className="block mb-2 text-navy-600 leading-relaxed">
          {processedParts}
        </span>
      );
    };

    return (
      <div className="space-y-3">
        {paragraphs.map((paragraph, pIndex) => {
          const lines = paragraph.split('\n');

          // Check if this paragraph contains bullet points
          const hasBullets = lines.some(line => line.trim().match(/^[-•*]\s+/));

          if (hasBullets) {
            return (
              <ul key={pIndex} className="list-none space-y-1">
                {lines.map((line, lIndex) => processLine(line, lIndex))}
              </ul>
            );
          }

          return (
            <div key={pIndex} className="mb-3">
              {lines.map((line, lIndex) => processLine(line, lIndex))}
            </div>
          );
        })}
      </div>
    );
  };

  export default HighlightText;