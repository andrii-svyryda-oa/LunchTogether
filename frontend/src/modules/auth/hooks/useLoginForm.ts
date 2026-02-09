import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, useLocation } from "react-router-dom";
import { loginSchema, type LoginFormData } from "@/utils/validation";
import { useAuth } from "@/hooks";
import { ROUTES } from "@/constants";

export function useLoginForm() {
  const [serverError, setServerError] = useState<string | null>(null);
  const { login, isLoggingIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname: string } })?.from
    ?.pathname ?? ROUTES.HOME;

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      await login(data).unwrap();
      navigate(from, { replace: true });
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(err?.data?.detail ?? "Login failed. Please try again.");
    }
  };

  return {
    form,
    onSubmit: form.handleSubmit(onSubmit),
    serverError,
    isSubmitting: isLoggingIn,
  };
}
