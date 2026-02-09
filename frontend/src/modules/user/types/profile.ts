import type { UserUpdateRequest } from "@/types";

export type ProfileFormData = Required<UserUpdateRequest>;

export interface ProfileEditState {
  isEditing: boolean;
  serverError: string | null;
}
