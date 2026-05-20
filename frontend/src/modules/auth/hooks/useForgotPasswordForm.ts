import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  forgotPasswordSchema,
  type ForgotPasswordFormData,
} from "@/utils/validation";
import { useRequestPasswordResetMutation } from "@/store/api/authApi";

export function useForgotPasswordForm() {
  const [serverError, setServerError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [requestReset, { isLoading }] = useRequestPasswordResetMutation();

  const form = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setServerError(null);
    setSuccessMessage(null);
    try {
      const result = await requestReset(data).unwrap();
      setSuccessMessage(
        result.message ??
          "If an account with that email exists, a reset link has been sent.",
      );
      form.reset();
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(
        err?.data?.detail ?? "Failed to request reset. Please try again.",
      );
    }
  };

  return {
    form,
    onSubmit: form.handleSubmit(onSubmit),
    serverError,
    successMessage,
    isSubmitting: isLoading,
  };
}
