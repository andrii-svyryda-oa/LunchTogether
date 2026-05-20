import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  resetPasswordSchema,
  type ResetPasswordFormData,
} from "@/utils/validation";
import { useConfirmPasswordResetMutation } from "@/store/api/authApi";
import { ROUTES } from "@/constants";

export function useResetPasswordForm() {
  const [serverError, setServerError] = useState<string | null>(null);
  const [confirmReset, { isLoading }] = useConfirmPasswordResetMutation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    setServerError(null);
    if (!token) {
      setServerError("Reset token is missing or invalid.");
      return;
    }
    try {
      await confirmReset({
        token,
        new_password: data.new_password,
      }).unwrap();
      navigate(ROUTES.LOGIN, {
        state: {
          message:
            "Password reset successful. Please log in with your new password.",
        },
      });
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(
        err?.data?.detail ?? "Failed to reset password. The link may have expired.",
      );
    }
  };

  return {
    form,
    onSubmit: form.handleSubmit(onSubmit),
    serverError,
    isSubmitting: isLoading,
    hasToken: Boolean(token),
  };
}
