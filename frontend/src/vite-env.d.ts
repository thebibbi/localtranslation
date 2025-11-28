/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_MAX_FILE_SIZE: string;
  readonly VITE_SUPPORTED_FORMATS: string;
  readonly VITE_DEFAULT_MODEL_SIZE: string;
  readonly VITE_ENABLE_DEV_TOOLS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
