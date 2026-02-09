import { useAppSelector } from "./useAppSelector";
import {
  selectUser,
  selectIsAuthenticated,
  selectIsLoading,
} from "@/store/slices/authSlice";
import {
  useLoginMutation,
  useLogoutMutation,
  useRegisterMutation,
} from "@/store/api/authApi";

export const useAuth = () => {
  const user = useAppSelector(selectUser);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isLoading = useAppSelector(selectIsLoading);
  const [login, { isLoading: isLoggingIn }] = useLoginMutation();
  const [register, { isLoading: isRegistering }] = useRegisterMutation();
  const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    isLoggingIn,
    isRegistering,
    isLoggingOut,
  };
};
