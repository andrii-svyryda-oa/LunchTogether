interface EnvConfig {
  apiBaseUrl: string;
  appName: string;
}

export const env: EnvConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  appName: import.meta.env.VITE_APP_NAME ?? "LunchTogether",
};
