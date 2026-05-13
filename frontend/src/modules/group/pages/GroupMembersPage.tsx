import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Combobox } from "@/components/ui/combobox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth, useGroupPermissions } from "@/hooks";
import {
  useCancelInvitationMutation,
  useCreateInvitationMutation,
  useGetGroupInvitationsQuery,
  useGetGroupMembersQuery,
  useGetGroupQuery,
  useRemoveGroupMemberMutation,
  useUpdateGroupMemberMutation,
} from "@/store/api/groupApi";
import { GROUP_ROLES } from "@/types";
import { formatDate } from "@/utils";
import {
  AlertCircle,
  Loader2,
  Mail,
  Plus,
  UserMinus,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

const ROLE_OPTIONS = GROUP_ROLES.map((r) => ({
  value: r,
  label: r.replace("_", " "),
}));

export function GroupMembersPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuth();
  const { data: group } = useGetGroupQuery(groupId!);
  const { data: members, isLoading } = useGetGroupMembersQuery(groupId!);
  const { data: pendingInvitations } = useGetGroupInvitationsQuery(groupId!);
  const [invite, { isLoading: isInviting }] = useCreateInvitationMutation();
  const [cancelInvitation, { isLoading: isCancellingInvite }] =
    useCancelInvitationMutation();
  const [cancellingInvitationId, setCancellingInvitationId] = useState<
    string | null
  >(null);
  const [removeMember] = useRemoveGroupMemberMutation();
  const [updateMember] = useUpdateGroupMemberMutation();

  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");
  const [inviteError, setInviteError] = useState<string | null>(null);

  const { canInviteMembers, canManageMembers } = useGroupPermissions(groupId);

  const getErrorMessage = (error: unknown): string => {
    const err = error as { data?: { detail?: string } };
    return err?.data?.detail ?? "Failed to send invitation. Please try again.";
  };

  const handleInviteDialogChange = (open: boolean) => {
    setInviteOpen(open);
    if (!open) {
      setInviteError(null);
    }
  };

  const handleInvite = async () => {
    setInviteError(null);
    try {
      await invite({
        groupId: groupId!,
        data: { email: inviteEmail, role: inviteRole },
      }).unwrap();
      setInviteOpen(false);
      setInviteEmail("");
    } catch (error: unknown) {
      setInviteError(getErrorMessage(error));
    }
  };

  const handleRemove = async (userId: string) => {
    if (!confirm("Are you sure you want to remove this member?")) return;
    await removeMember({ groupId: groupId!, userId });
  };

  const handleRoleChange = async (userId: string, role: string) => {
    await updateMember({ groupId: groupId!, userId, data: { role } });
  };

  const handleCancelInvitation = async (invitationId: string) => {
    if (!confirm("Cancel this pending invitation?")) return;
    setCancellingInvitationId(invitationId);
    try {
      await cancelInvitation({ groupId: groupId!, invitationId }).unwrap();
    } catch {
      // Silently ignore; invitation list will refresh on next load.
    } finally {
      setCancellingInvitationId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const isOwner = group?.owner_id === user?.id;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Members</h1>
          <p className="text-muted-foreground mt-1">
            {members?.length ?? 0} members in this group
          </p>
        </div>
        {canInviteMembers && (
        <Dialog open={inviteOpen} onOpenChange={handleInviteDialogChange}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
              <Plus className="mr-2 h-4 w-4" />
              Invite
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Invite Member</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  value={inviteEmail}
                  onChange={(e) => {
                    setInviteEmail(e.target.value);
                    if (inviteError) {
                      setInviteError(null);
                    }
                  }}
                  placeholder="colleague@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Combobox
                  options={ROLE_OPTIONS}
                  value={inviteRole}
                  onChange={setInviteRole}
                  placeholder="Select role..."
                  searchPlaceholder="Search roles..."
                />
              </div>
              {inviteError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{inviteError}</AlertDescription>
                </Alert>
              )}
              <Button
                onClick={handleInvite}
                disabled={!inviteEmail.trim() || isInviting}
                className="w-full"
              >
                {isInviting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Invitation
              </Button>
            </div>
          </DialogContent>
        </Dialog>
        )}
      </div>

      {members && members.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <Users className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium">No members yet</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {members?.map((member) => {
            const memberIsOwner = member.user_id === group?.owner_id;
            return (
              <Card key={member.id} className="p-4 hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm shrink-0">
                      {(member.user_full_name ?? "?").charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-medium">{member.user_full_name}</p>
                        {memberIsOwner && (
                          <span className="text-[11px] font-medium bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                            Owner
                          </span>
                        )}
                        {member.user_id === user?.id && (
                          <span className="text-[11px] font-medium bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                            You
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {member.user_email}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-[11px] text-muted-foreground space-x-1.5 hidden lg:flex">
                      {member.permissions.map((p) => (
                        <span
                          key={p.permission_type}
                          className="bg-muted px-1.5 py-0.5 rounded"
                        >
                          {p.permission_type.charAt(0).toUpperCase()}:{p.level}
                        </span>
                      ))}
                    </div>
                    {!memberIsOwner && (isOwner || user?.role === "admin" || canManageMembers) && (
                      <>
                        <div className="w-36">
                          <Combobox
                            options={ROLE_OPTIONS}
                            value=""
                            onChange={(val) => {
                              if (val) handleRoleChange(member.user_id, val);
                            }}
                            placeholder="Change role"
                            searchPlaceholder="Search roles..."
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemove(member.user_id)}
                          className="text-muted-foreground hover:text-destructive"
                        >
                          <UserMinus className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {pendingInvitations && pendingInvitations.length > 0 && (
        <div className="mt-10">
          <div className="flex items-center gap-2 mb-3">
            <h2 className="text-lg font-semibold tracking-tight">
              Pending Invitations
            </h2>
            <span className="text-[11px] font-medium bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">
              {pendingInvitations.length}
            </span>
          </div>
          <div className="space-y-3">
            {pendingInvitations.map((invitation) => {
              const canCancel =
                isOwner ||
                user?.role === "admin" ||
                canManageMembers ||
                invitation.inviter_id === user?.id;
              const isThisInviteCancelling =
                isCancellingInvite &&
                cancellingInvitationId === invitation.id;
              return (
                <Card key={invitation.id} className="p-4 hover:shadow-md">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100 text-amber-700 shrink-0">
                        <Mail className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-medium truncate">
                            {invitation.invitee_email}
                          </p>
                          <span className="text-[11px] font-medium bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">
                            Pending
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          Invited by{" "}
                          {invitation.inviter_id === user?.id
                            ? "you"
                            : invitation.inviter_full_name ?? "a member"}
                          {" · "}
                          {formatDate(invitation.created_at)}
                        </p>
                      </div>
                    </div>
                    {canCancel && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleCancelInvitation(invitation.id)}
                        disabled={isThisInviteCancelling}
                        className="text-muted-foreground hover:text-destructive shrink-0"
                        title="Cancel invitation"
                      >
                        {isThisInviteCancelling ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <X className="h-4 w-4" />
                        )}
                      </Button>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
