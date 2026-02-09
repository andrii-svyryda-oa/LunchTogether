import type { LoginFormData, RegisterFormData } from "@/utils/validation";

export type { LoginFormData, RegisterFormData };

export interface AuthFormState {
  serverError: string | null;
  isSubmitting: boolean;
}
