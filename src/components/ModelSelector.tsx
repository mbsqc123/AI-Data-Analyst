import { useState, useEffect } from 'react';
import { MdKeyboardArrowDown } from 'react-icons/md';
import dataSetStore from '../zustand/stores/dataSetStore';
import { CHAT_ENDPOINTS } from '../zustand/apis/endPoints';

interface ModelInfo {
  name: string;
  display_name: string;
  description: string;
  platform: string;
  capability: string;
  best_for: string[];
}

interface ModelSelectorProps {
  compact?: boolean; // Optional prop for compact display in chat header
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ compact = false }) => {
  const model = dataSetStore((state) => state.selectedModel);
  const setModel = dataSetStore((state) => state.setModel);

  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [loadingModels, setLoadingModels] = useState(true);

  // Set default model to gpt-4o-mini if not already set
  useEffect(() => {
    if (!model && availableModels.length > 0) {
      const defaultModel = availableModels.find(m => m.name === 'gpt-4o-mini');
      if (defaultModel) {
        console.log('Setting default model to:', defaultModel.name);
        setModel(defaultModel.name);
      }
    }
  }, [availableModels, model, setModel]);

  // Fetch available models from the backend
  useEffect(() => {
    const fetchModels = async () => {
      try {
        console.log('Fetching models from:', CHAT_ENDPOINTS.GET_MODELS);
        const response = await fetch(CHAT_ENDPOINTS.GET_MODELS);
        const data = await response.json();
        if (data.status_code === 200 && data.data?.models) {
          console.log('Available models loaded:', data.data.models);
          setAvailableModels(data.data.models);
        }
      } catch (error) {
        console.error('Error fetching models:', error);
        // Fallback to default models if fetch fails
        setAvailableModels([
          { name: 'gpt-4o-mini', display_name: 'GPT-4o Mini', description: 'Fast and cost-effective', platform: 'openai', capability: 'fast', best_for: [] },
          { name: 'gpt-4o', display_name: 'GPT-4o', description: 'Best all-around', platform: 'openai', capability: 'balanced', best_for: [] },
        ]);
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, []);

  if (loadingModels) {
    return (
      <div className="relative">
        <div className={`bg-blue-gray-50 border-blue-gray-100 text-gray-400 border rounded-lg ${compact ? 'py-1.5 px-3 text-sm' : 'py-2 px-4'}`}>
          Loading models...
        </div>
      </div>
    );
  }

  return (
    <div className="relative group">
      <select
        className={`appearance-none bg-blue-gray-50 border-blue-gray-100 text-gray-700 border rounded-lg leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
          compact ? 'py-1.5 pr-8 pl-3 text-sm min-w-[200px]' : 'py-2 pr-8 pl-4 min-w-[280px]'
        }`}
        value={model}
        onChange={(e) => {
          console.log('Model selector changed to:', e.target.value);
          setModel(e.target.value);
        }}
        title={availableModels.find(m => m.name === model)?.description || 'Select a model'}
      >
        <option value="">Select LLM Model</option>

        {/* OpenAI Models */}
        <optgroup label="🤖 OpenAI Models">
          {availableModels
            .filter(m => m.platform === 'openai')
            .map((modelInfo) => (
              <option key={modelInfo.name} value={modelInfo.name}>
                {modelInfo.name === 'gpt-4o' && '⭐ '}
                {modelInfo.name === 'o1' && '🧠 '}
                {modelInfo.display_name} - {modelInfo.description}
              </option>
            ))
          }
        </optgroup>

        {/* Groq Models */}
        {availableModels.filter(m => m.platform === 'groq').length > 0 && (
          <optgroup label="⚡ Groq Models (Fast & Free)">
            {availableModels
              .filter(m => m.platform === 'groq')
              .map((modelInfo) => (
                <option key={modelInfo.name} value={modelInfo.name}>
                  {modelInfo.display_name} - {modelInfo.description}
                </option>
              ))
            }
          </optgroup>
        )}
      </select>
      <div
        className={`pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700`}
      >
        <MdKeyboardArrowDown className="h-5 w-5" />
      </div>
      {/* Tooltip showing model info */}
      {!compact && model && availableModels.find(m => m.name === model) && (
        <div className="absolute left-0 top-full mt-2 hidden group-hover:block z-10">
          <div className="bg-navy-800 text-white text-xs rounded-lg p-3 shadow-lg max-w-xs">
            <p className="font-semibold mb-1">
              {availableModels.find(m => m.name === model)?.display_name}
            </p>
            <p className="mb-2 opacity-90">
              {availableModels.find(m => m.name === model)?.description}
            </p>
            {availableModels.find(m => m.name === model)?.best_for &&
             availableModels.find(m => m.name === model)!.best_for.length > 0 && (
              <div>
                <p className="font-semibold mb-1">Best for:</p>
                <ul className="list-disc list-inside opacity-90">
                  {availableModels.find(m => m.name === model)!.best_for.map((use, idx) => (
                    <li key={idx}>{use}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
