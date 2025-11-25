export const API_BASE_URL = 'http://localhost:8000/api';

export const AUTH_ENDPOINTS = {
  SIGNUP: `${API_BASE_URL}/user/v1/signup`,
  LOGIN: `${API_BASE_URL}/user/v1/login`,
  GET_USER: `${API_BASE_URL}/user/v1/`,
};

export const CHAT_ENDPOINTS = {
  ASK_QUESTION: `${API_BASE_URL}/chat/v1/ask-question`,
  INITIATE_CONVERSATION: `${API_BASE_URL}/chat/v1/initiate-conversations`,
  GET_CONVERSATIONS: `${API_BASE_URL}/chat/v1/get-conversations`,
  GET_CONVERSATION_HISTORY:(conversation_id:number)=> `${API_BASE_URL}/chat/v1/get-conversations-history/${conversation_id}`,
  GET_MODELS: `${API_BASE_URL}/chat/v1/models`,
};

export const DATA_SOURCE_ENDPOINTS = {
  UPLOAD_SPREADSHEET: `${API_BASE_URL}/data/v1/upload-spreadsheet`,
  UPLOAD_DOCUMENT: `${API_BASE_URL}/data/v1/upload-document`,
  ADD_DATA_SOURCE: `${API_BASE_URL}/data/v1/add-data-source`,
  GET_DATA_SOURCES: `${API_BASE_URL}/data/v1/get-data-sources`,
  GET_DATA_SOURCE_TABLES: `${API_BASE_URL}/data/v1/get-source-tables`,
};