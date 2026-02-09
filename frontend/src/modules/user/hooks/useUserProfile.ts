import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { useUpdateUserMutation } from "@/store/api/userApi";
import { fullNameSchema, emailSchema } from "@/utils/validation";
import type { User } from "@/types";

const profileSchema = z.object({
  full_name: fullNameSchema,
  email: emailSchema,
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function useUserProfile(user: User) {
  const [isEditing, setIsEditing] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [updateUser, { isLoading: isUpdating }] = useUpdateUserMutation();

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user.full_name,
      email: user.email,
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setServerError(null);
    try {
      await updateUser({ id: user.id, data }).unwrap();
      setIsEditing(false);
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(
        err?.data?.detail ?? "Failed to update profile. Please try again."
      );
    }
  };

  const handleCancel = () => {
    form.reset({
      full_name: user.full_name,
      email: user.email,
    });
    setServerError(null);
    setIsEditing(false);
  };

  return {
    form,
    isEditing,
    setIsEditing,
    onSubmit: form.handleSubmit(onSubmit),
    handleCancel,
    serverError,
    isUpdating,
  };
}
