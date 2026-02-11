import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import { useUpdateUserMutation } from "@/store/api/userApi";
import { useState } from "react";
import { toast } from "sonner";

export function SettingsPage() {
  const { user } = useAuth();
  const [updateUser, { isLoading }] = useUpdateUserMutation();

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [navigateToActive, setNavigateToActive] = useState(
    user?.navigate_to_active_order ?? false,
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
      <h1 className="text-3xl font-bold tracking-tight mb-6">Settings</h1>

      <div className="max-w-2xl space-y-6">
        {/* Profile */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div>
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
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Preferences</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto-navigate to active order</p>
              <p className="text-sm text-muted-foreground">
                When entering a group page, automatically go to the active order
                if one exists.
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={navigateToActive}
              onClick={() => setNavigateToActive(!navigateToActive)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                navigateToActive ? "bg-primary" : "bg-gray-200"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  navigateToActive ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </Card>

        {/* Account info */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Account</h2>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-muted-foreground">Role:</span>{" "}
              <span className="font-medium">
                {user?.is_admin ? "Admin" : "User"}
              </span>
            </p>
            <p>
              <span className="text-muted-foreground">Status:</span>{" "}
              <span className="font-medium">
                {user?.is_active ? "Active" : "Inactive"}
              </span>
            </p>
            <p>
              <span className="text-muted-foreground">Member since:</span>{" "}
              <span className="font-medium">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString()
                  : "N/A"}
              </span>
            </p>
          </div>
        </Card>

        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}
