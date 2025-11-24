/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from 'zustand';
import { DataSources } from '../../interfaces/dataSourceInterface';

export interface DataSetStore {
  dataSets: DataSources[] | null;
  tables: string[] ;
  selectedModel:string ;
  setTables: (tables: string[]) => void;
  setModel: (model: string) => void;
  setDataSet: (dataSets: DataSources[]) => void;
  addDataSet: (dataSet: DataSources) => void;
  updateDataSet: (dataSet: DataSources) => void;
  deleteDataSet: (id: number) => void;
  getDataSet: (id: number) => DataSources | any;
}

const dataSetStore = create<DataSetStore>((set) => ({
  dataSets: null,
  tables:[],
  selectedModel:"gpt-4o-mini",  // Updated to use OpenAI's fast and cost-effective model

  setTables: (tables: string[]) => set({ tables }),
  setModel: (model:string) => set({ selectedModel:model }),

  setDataSet: (dataSets: DataSources[]) => set({ dataSets }),

  addDataSet: (dataSet: DataSources) =>
    set((state) => ({
      dataSets: state.dataSets ? [...state.dataSets, dataSet] : [dataSet],
    })),

  updateDataSet: (updatedDataSet: DataSources) =>
    set((state) => ({
      dataSets:
        state.dataSets?.map((dataSet) =>
          dataSet.id === updatedDataSet.id ? updatedDataSet : dataSet,
        ) || null,
    })),

  deleteDataSet: (id: number) =>
    set((state) => ({
      dataSets: state.dataSets?.filter((dataSet) => dataSet.id !== id) || null,
    })),

  getDataSet: (id: number) => {
    const state = dataSetStore.getState();
    return state.dataSets?.find((dataSet) => dataSet.id === id);
  },
}));

export default dataSetStore;
