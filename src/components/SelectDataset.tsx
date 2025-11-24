import { useState, useEffect } from 'react';
import { MdKeyboardArrowDown } from 'react-icons/md';
import dataSetStore from '../zustand/stores/dataSetStore';
import { useGetDataSourcesMutation, useGetTablesMutation } from '../hooks/useDataSet';
import { SelectModelSkeleton } from './loaders/DataSourceTableLoader';
import { useParams } from 'react-router-dom';
import { DataSources } from '../interfaces/dataSourceInterface';

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
        const response = await fetch('http://localhost:5000/api/chat/models');
        const data = await response.json();
        if (data.status === 200 && data.data?.models) {
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

          <div className="relative">
            <select
              className={`appearance-none bg-blue-gray-50 border-blue-gray-100 text-gray-700 border rounded-[12px] py-2 pr-8 pl-4 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
              value={model}
              onChange={(e) => setModel(e.target.value)}
              title={availableModels.find(m => m.name === model)?.description || 'Select a model'}
            >
              <option value="">Select LLM Model</option>

              {/* OpenAI Models */}
              <optgroup label="OpenAI Models">
                {availableModels
                  .filter(m => m.platform === 'openai')
                  .map((modelInfo) => (
                    <option key={modelInfo.name} value={modelInfo.name}>
                      {modelInfo.display_name} - {modelInfo.description}
                    </option>
                  ))
                }
              </optgroup>

              {/* Groq Models */}
              <optgroup label="Groq Models">
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
          </div>
        </div>
      )}
    </div>
  );
};

export default SelectDataset;
