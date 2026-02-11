import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks";
import {
  useCreateInvitationMutation,
  useGetGroupMembersQuery,
  useGetGroupQuery,
  useRemoveGroupMemberMutation,
  useUpdateGroupMemberMutation,
} from "@/store/api/groupApi";
import { GROUP_ROLES } from "@/types";
import { Plus, UserMinus } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

export function GroupMembersPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: group } = useGetGroupQuery(groupId!);
  const { data: members, isLoading } = useGetGroupMembersQuery(groupId!);
  const [invite] = useCreateInvitationMutation();
  const [removeMember] = useRemoveGroupMemberMutation();
  const [updateMember] = useUpdateGroupMemberMutation();

  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");

  const handleInvite = async () => {
    try {
      await invite({
        groupId: groupId!,
        data: { email: inviteEmail, role: inviteRole },
      }).unwrap();
      setInviteOpen(false);
      setInviteEmail("");
    } catch {
      // Error handled
    }
  };

  const handleRemove = async (userId: string) => {
    if (!confirm("Are you sure you want to remove this member?")) return;
    await removeMember({ groupId: groupId!, userId });
  };

  const handleRoleChange = async (userId: string, role: string) => {
    await updateMember({ groupId: groupId!, userId, data: { role } });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const isOwner = group?.owner_id === user?.id;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Members</h1>
        <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Invite
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite Member</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label>Email</Label>
                <Input
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="colleague@example.com"
                />
              </div>
              <div>
                <Label>Role</Label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {GROUP_ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r.replace("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
              <Button
                onClick={handleInvite}
                disabled={!inviteEmail.trim()}
                className="w-full"
              >
                Send Invitation
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {members?.map((member) => {
          const memberIsOwner = member.user_id === group?.owner_id;
          return (
            <Card key={member.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                    {(member.user_full_name ?? "?").charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium">
                      {member.user_full_name}
                      {memberIsOwner && (
                        <span className="ml-2 text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                          Owner
                        </span>
                      )}
                      {member.user_id === user?.id && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                          You
                        </span>
                      )}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {member.user_email}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-xs text-muted-foreground space-x-2 hidden md:block">
                    <span>M:{member.members_scope}</span>
                    <span>O:{member.orders_scope}</span>
                    <span>B:{member.balances_scope}</span>
                    <span>A:{member.analytics_scope}</span>
                    <span>R:{member.restaurants_scope}</span>
                  </div>
                  {!memberIsOwner && (isOwner || user?.is_admin) && (
                    <>
                      <select
                        onChange={(e) =>
                          handleRoleChange(member.user_id, e.target.value)
                        }
                        className="h-8 rounded-md border border-input bg-background px-2 text-xs"
                        defaultValue=""
                      >
                        <option value="" disabled>
                          Change role
                        </option>
                        {GROUP_ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r.replace("_", " ")}
                          </option>
                        ))}
                      </select>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRemove(member.user_id)}
                      >
                        <UserMinus className="h-4 w-4 text-destructive" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
