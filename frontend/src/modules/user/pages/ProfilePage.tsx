import { useAuth } from "@/hooks";
import { UserProfile } from "../components/UserProfile";

export function ProfilePage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        Unable to load profile.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
        <p className="text-muted-foreground">
          View and manage your profile information.
        </p>
      </div>
      <UserProfile user={user} />
    </div>
  );
}
