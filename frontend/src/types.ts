export interface SourceItem {
  title: string;
  url: string;
  snippet?: string;
  metadata?: {
    chat_id?: string;
    data_source?: string;
    coverage?: string;
    full_text?: string;
    [key: string]: unknown;
  };
}

export interface ChartData {
  url: string;
  title?: string;
  alt?: string;
  convertedUrl?: string;
  isConverting?: boolean;
  conversionError?: string;
  isDownloading?: boolean;
  loadError?: boolean;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  sources?: SourceItem[];
  charts?: ChartData[];
  structuredResponse?: StructuredResponse;
}

export interface ChatState {
  messages: Message[];
  isTyping: boolean;
  inputValue: string;
}

// Structured Response Types
export interface StructuredResponse {
  overview?: OverviewSection;
  keyFindings?: KeyFindingsSection;
  howToUse?: HowToSection;
  coverage?: CoverageSection;
  limitations?: LimitationsSection;
  datasetInfo?: DatasetInfoSection;
  references?: ReferencesSection;
  customSections?: CustomSection[];
}

export interface OverviewSection {
  title: string;
  content: string;
  keyStats?: Statistic[];
}

export interface KeyFindingsSection {
  title: string;
  findings: Finding[];
}

export interface HowToSection {
  title: string;
  steps: HowToStep[];
}

export interface CoverageSection {
  title: string;
  coverage: string[];
  applicability?: string[];
}

export interface LimitationsSection {
  title: string;
  limitations: string[];
}

export interface DatasetInfoSection {
  title: string;
  info: DatasetInfo[];
}

export interface ReferencesSection {
  title: string;
  sources: Reference[];
}

export interface CustomSection {
  title: string;
  content: string;
  type: 'list' | 'table' | 'text' | 'comparison';
  items?: string[];
  data?: Record<string, unknown>;
}

export interface Statistic {
  label: string;
  value: string | number;
  unit?: string;
  comparison?: string;
  highlighted?: boolean;
}

export interface Finding {
  title?: string;
  content: string;
  icon?: string;
  type: 'statistic' | 'insight' | 'trend' | 'comparison';
}

export interface HowToStep {
  step: number;
  title: string;
  description: string;
  action?: string;
}

export interface DatasetInfo {
  label: string;
  value: string;
  type: 'text' | 'date' | 'link' | 'number';
}

export interface Reference {
  title: string;
  url?: string;
  description?: string;
  type: 'dataset' | 'document' | 'link';
}

// Response parsing types
export interface ParsedSection {
  type: string;
  title: string;
  content: string;
  level: number;
  subsections?: ParsedSection[];
}

export interface ParseResult {
  sections: ParsedSection[];
  metadata?: {
    hasMarkdown: boolean;
    hasLists: boolean;
    hasHeadings: boolean;
    totalSections: number;
  };
}