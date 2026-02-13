import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import { useUpdateUserMutation } from "@/store/api/userApi";
import { cn } from "@/utils";
import { Loader2, Settings, ShieldCheck, UserCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function SettingsPage() {
  const { user } = useAuth();
  const [updateUser, { isLoading }] = useUpdateUserMutation();

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [navigateToActive, setNavigateToActive] = useState(
    user?.navigate_to_active_order ?? false
  );

  const handleSave = async () => {
    if (!user) return;
    try {
      await updateUser({
        id: user.id,
        data: {
          full_name: fullName !== user.full_name ? fullName : undefined,
          email: email !== user.email ? email : undefined,
          navigate_to_active_order:
            navigateToActive !== user.navigate_to_active_order
              ? navigateToActive
              : undefined,
        },
      }).unwrap();
      toast.success("Settings saved successfully");
    } catch {
      toast.error("Failed to save settings");
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Profile */}
        <Card className="overflow-hidden">
          <div className="flex items-center gap-3 px-6 py-4 border-b bg-muted/30">
            <UserCircle className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Profile</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
        </Card>

        {/* Preferences */}
        <Card className="overflow-hidden">
          <div className="flex items-center gap-3 px-6 py-4 border-b bg-muted/30">
            <Settings className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Preferences</h2>
          </div>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto-navigate to active order</p>
                <p className="text-sm text-muted-foreground">
                  When entering a group page, automatically go to the active
                  order if one exists.
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={navigateToActive}
                onClick={() => setNavigateToActive(!navigateToActive)}
                className={cn(
                  "relative inline-flex h-6 w-11 items-center rounded-full transition-colors shrink-0 ml-4",
                  navigateToActive ? "bg-primary" : "bg-muted"
                )}
              >
                <span
                  className={cn(
                    "inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform",
                    navigateToActive ? "translate-x-6" : "translate-x-1"
                  )}
                />
              </button>
            </div>
          </div>
        </Card>

        {/* Account info */}
        <Card className="overflow-hidden">
          <div className="flex items-center gap-3 px-6 py-4 border-b bg-muted/30">
            <ShieldCheck className="h-5 w-5 text-muted-foreground" />
            <h2 className="font-semibold">Account</h2>
          </div>
          <div className="p-6">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                  Role
                </p>
                <span
                  className={cn(
                    "inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium",
                    user?.role === "admin"
                      ? "bg-purple-50 text-purple-700"
                      : "bg-blue-50 text-blue-700"
                  )}
                >
                  {user?.role === "admin" ? "Admin" : "User"}
                </span>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                  Status
                </p>
                <span
                  className={cn(
                    "inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full font-medium",
                    user?.is_active
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-red-50 text-red-700"
                  )}
                >
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full",
                      user?.is_active ? "bg-emerald-500" : "bg-red-500"
                    )}
                  />
                  {user?.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                  Member since
                </p>
                <p className="text-sm font-medium">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : "N/A"}
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Button
          onClick={handleSave}
          disabled={isLoading}
          className="shadow-md shadow-primary/20"
        >
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isLoading ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}
