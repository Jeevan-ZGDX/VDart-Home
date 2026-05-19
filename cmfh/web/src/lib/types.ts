export type GrammarError = {
  message?: string;
  category?: string;
  rule?: string;
  offset?: number;
  length?: number;
  context?: string;
  replacements?: string[];
};

export type AnalyzeResponse = {
  text: string;
  grammar: {
    is_valid?: boolean;
    error_count?: number;
    errors?: GrammarError[];
  };
  filler: Record<string, unknown>;
  confidence: Record<string, unknown>;
  vocabulary: {
    vocabulary_score?: number;
    quality?: string;
    word_count?: number;
    unique_words?: number;
    lexical_diversity?: number;
    academic_words?: number;
    action_verbs?: number;
    weak_words?: number;
    top_words?: Record<string, number>;
  };
  structure: Record<string, unknown>;
  overall_score: number;
};

export type RewriteResponse = {
  original: string;
  rewritten: string;
  style: string;
  success: boolean;
  source: string;
  error?: string;
  message?: string;
};

export type HealthResponse = {
  status: string;
  whisper_model: string;
  ollama_available: boolean;
  database: string;
};

export type PoseResponse =
  | { detected: false; message?: string }
  | {
      detected: true;
      posture_score: number;
      hand_gesture: string;
      arm_position: string;
      shoulder_balance: number;
      confidence_level: string;
      suggestions: string[];
    };

