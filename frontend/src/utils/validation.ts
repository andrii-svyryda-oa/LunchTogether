import { z } from "zod/v4";
import { VALIDATION, VALIDATION_MESSAGES } from "@/constants";

export const emailSchema = z
  .email(VALIDATION_MESSAGES.EMAIL.INVALID)
  .max(VALIDATION.EMAIL.MAX_LENGTH, VALIDATION_MESSAGES.EMAIL.MAX_LENGTH);

export const passwordSchema = z
  .string()
  .min(VALIDATION.PASSWORD.MIN_LENGTH, VALIDATION_MESSAGES.PASSWORD.MIN_LENGTH)
  .max(VALIDATION.PASSWORD.MAX_LENGTH, VALIDATION_MESSAGES.PASSWORD.MAX_LENGTH);

export const fullNameSchema = z
  .string()
  .min(
    VALIDATION.FULL_NAME.MIN_LENGTH,
    VALIDATION_MESSAGES.FULL_NAME.MIN_LENGTH
  )
  .max(
    VALIDATION.FULL_NAME.MAX_LENGTH,
    VALIDATION_MESSAGES.FULL_NAME.MAX_LENGTH
  );

export const loginSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
});

export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  full_name: fullNameSchema,
});

export const forgotPasswordSchema = z.object({
  email: emailSchema,
});

export const resetPasswordSchema = z
  .object({
    new_password: passwordSchema,
    confirm_password: passwordSchema,
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
