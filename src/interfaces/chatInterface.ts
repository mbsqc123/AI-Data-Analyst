
export interface ChatRequestBody {
  question: string;
  type: "url" | "spreadsheet" | "direct_chat" | string;
  conversaction_id?: number;
  dataset_id?: number;
  selected_tables?: string[];
  llm_model:string
}

export type StreamCallback = (chunk: string) => void;

export interface StreamConfig {
  onChunk: StreamCallback;
  signal?: AbortSignal;
}

export interface InitiateConversationRequestBody {
  data_source_id: number;
}

export interface InitiateConversationResponse {
  conversaction_id: number;
  conversaction_title: string;
  data_source_id: number;
}

interface FormattedData {
  label: string;
  value: number;
}
export interface TableInfo {
  table_name: string;
  columns: string[];
  noun_columns: string[];
}
export interface ProcessingMessage {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parsed_question?: { is_relevant: boolean; relevant_tables: TableInfo[] };
  sql_query?: string;
  sql_valid?: boolean;
  query_result?: string;
  answer?: string;
  recommended_visualization?: string;
  reason?: string;
  formatted_data_for_visualization?: FormattedData[];
  error: string;
  original: string;
}

export interface AiAnswer{
  answer?: string,
  formatted_data_for_visualization?: object[],
  recommended_visualization?: string,
  sql_query?: string,
  sql_valid?: boolean,
  parsed_question?: { is_relevant: boolean; relevant_tables: TableInfo[] },
  model_used?: string
}

export interface FileUploadMessage {
  fileName: string;
  fileSize: number;
  rowsProcessed?: number;
  timestamp: Date;
  dataSourceId?: number;
  tableName?: string;
}

export interface ConversationMessages{
  user_question?: string,
  ai_answer?: AiAnswer,
  file_upload?: FileUploadMessage,
}

export interface Conversations {
  id: number;
  title: string;
  created_at:string
}

export interface ConversationsResponse {
  conversations: Conversations[];
}

// For the content object
export interface MessageContent {
  question?: string;
  answer?: ProcessingMessage[];
}

// For the main message object
interface Message {
  id: number;
  role: 'user' | 'assistant'; // Using literal type for role if those are the only options
  content: MessageContent;
  created_at: string;
  updated_at: string;
}

export interface ConversationHistoryResponse {
  messages: Message[];
}