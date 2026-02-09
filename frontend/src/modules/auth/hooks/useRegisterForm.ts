import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { registerSchema, type RegisterFormData } from "@/utils/validation";
import { useAuth } from "@/hooks";
import { ROUTES } from "@/constants";

export function useRegisterForm() {
  const [serverError, setServerError] = useState<string | null>(null);
  const { register: registerUser, isRegistering } = useAuth();
  const navigate = useNavigate();

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
      full_name: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    try {
      await registerUser(data).unwrap();
      navigate(ROUTES.LOGIN, {
        state: { message: "Registration successful! Please log in." },
      });
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(
        err?.data?.detail ?? "Registration failed. Please try again."
      );
    }
  };

  return {
    form,
    onSubmit: form.handleSubmit(onSubmit),
    serverError,
    isSubmitting: isRegistering,
  };
}
