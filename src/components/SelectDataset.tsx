import { useState, useEffect } from 'react';
import { MdKeyboardArrowDown } from 'react-icons/md';
import dataSetStore from '../zustand/stores/dataSetStore';
import { useGetDataSourcesMutation, useGetTablesMutation } from '../hooks/useDataSet';
import { SelectModelSkeleton } from './loaders/DataSourceTableLoader';
import { useParams } from 'react-router-dom';
import { DataSources } from '../interfaces/dataSourceInterface';
import { CHAT_ENDPOINTS } from '../zustand/apis/endPoints';

interface ModelInfo {
  name: string;
  display_name: string;
  description: string;
  platform: string;
  capability: string;
  best_for: string[];
}

const SelectDataset: React.FC = () => {
  const { data_source_id } = useParams();

  const tables = dataSetStore((state) => state.tables);
  const model = dataSetStore((state) => state.selectedModel);
  const dataSets = dataSetStore((state) => state.dataSets);
  const getDataSet = dataSetStore((state) => state.getDataSet);
  const setModel = dataSetStore((state) => state.setModel);

  const { mutate: getDataSource, status: dataSourceStatus } = useGetDataSourcesMutation();
  const { mutate: getTables, status: loadTableStatus } = useGetTablesMutation();

  const [selectedDataSource, setSelectedDataSource] = useState('');
  const [dataSet, setDataSet] = useState<DataSources>();
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [loadingModels, setLoadingModels] = useState(true);

  // Log when availableModels changes
  useEffect(() => {
    console.log('Available models updated:', availableModels);
    console.log('Number of models:', availableModels.length);
  }, [availableModels]);

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


  useEffect(() => {
    if (!dataSets) {
      getDataSource();
    }
    if (dataSets && data_source_id) {
      const data = getDataSet(Number(data_source_id));
      setDataSet(data);
    }
  }, [dataSets, data_source_id]);

  useEffect(() => {
    if (dataSet?.type === 'url' && dataSet?.connection_url) {
      getTables({db_url:dataSet?.connection_url})
    }
  }, [dataSet]);

  // Fetch available models from the backend
  useEffect(() => {
    const fetchModels = async () => {
      try {
        console.log('Fetching models from:', CHAT_ENDPOINTS.GET_MODELS);
        const response = await fetch(CHAT_ENDPOINTS.GET_MODELS);
        console.log('Models API response status:', response.status);
        const data = await response.json();
        console.log('Models API response data:', data);
        if (data.status_code === 200 && data.data?.models) {
          console.log('Available models loaded:', data.data.models);
          setAvailableModels(data.data.models);
        }
      } catch (error) {
        console.error('Error fetching models:', error);
        // Fallback to default models if fetch fails
        setAvailableModels([
          { name: 'gpt-4o-mini', display_name: 'GPT-4o Mini', description: 'Fast and cost-effective', platform: 'openai', capability: 'fast', best_for: [] },
          { name: 'gemma2-9b-it', display_name: 'Gemma 2 9B', description: 'Balanced model', platform: 'groq', capability: 'balanced', best_for: [] },
        ]);
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, []);

  return (
    <div className="mx-auto mb-24">
      <h1 className={`text-center text-2xl font-bold text-navy-800`}>Have Something In Mind?</h1>

      <p className={`text-center text-sm text-navy-600 my-4`}>
        Select Or Add A Data Set, Ask Me Anything About The Data Set,
        <br />
        Get Meaningful Insight From Me.
      </p>
      {(dataSourceStatus === 'pending' || loadTableStatus === 'pending' || loadingModels) ? (
        <SelectModelSkeleton />
      ) : (
        <div className="flex justify-center items-center mt-4">
          {dataSet?.type === 'url' && (
            <>
              <div className="relative">
                <select
                  className={`appearance-none bg-blue-gray-50 border-blue-gray-100 text-gray-700 border rounded-[12px] py-2 pr-8 pl-4 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  value={selectedDataSource}
                  onChange={(e) => setSelectedDataSource(e.target.value)}
                >
                  <option value="">Selected Tables</option>
                  {
                    tables?.map((table) => (
                      <option key={table} value={table}>{table}</option>
                    ))
                  }
                </select>
                <div
                  className={`mr-l pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700`}
                >
                  <MdKeyboardArrowDown className="h-5 w-5" />
                </div>
              </div>
              <span className={`mx-4 text-gray-400`}>|</span>
            </>
          )}

          <div className="relative group">
            <select
              className={`appearance-none bg-blue-gray-50 border-blue-gray-100 text-gray-700 border rounded-[12px] py-2 pr-8 pl-4 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-w-[280px]`}
              value={model}
              onChange={(e) => {
                console.log('Dropdown changed to:', e.target.value);
                console.log('setModel function:', typeof setModel);
                console.log('Current model value:', model);
                setModel(e.target.value);
                console.log('Model updated via setModel');
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
            </select>
            <div
              className={`mr-l pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700`}
            >
              <MdKeyboardArrowDown className="h-5 w-5" />
            </div>
            {/* Tooltip showing model info */}
            {model && availableModels.find(m => m.name === model) && (
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
        </div>
      )}
    </div>
  );
};

export default SelectDataset;
