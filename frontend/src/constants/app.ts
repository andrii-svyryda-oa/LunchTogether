import { env } from "@/config/env";

export const APP = {
  NAME: env.appName,
  DEFAULT_PAGE_SIZE: 10,
  DEBOUNCE_MS: 300,
} as const;
