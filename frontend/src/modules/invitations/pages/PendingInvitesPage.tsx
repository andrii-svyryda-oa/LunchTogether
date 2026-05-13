import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  useAcceptInvitationMutation,
  useDeclineInvitationMutation,
  useGetMyPendingInvitationsQuery,
} from "@/store/api/groupApi";
import { formatDate } from "@/utils";
import type { MyInvitation } from "@/types";
import { AlertCircle, CheckCircle, Loader2, Mail, XCircle } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export function PendingInvitesPage() {
  const { data: invitations, isLoading } = useGetMyPendingInvitationsQuery();
  const [accept] = useAcceptInvitationMutation();
  const [decline] = useDeclineInvitationMutation();
  const navigate = useNavigate();

  const [pendingAction, setPendingAction] = useState<{
    id: string;
    action: "accept" | "decline";
  } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const handleAccept = async (invitation: MyInvitation) => {
    setActionError(null);
    setPendingAction({ id: invitation.id, action: "accept" });
    try {
      const result = await accept(invitation.token).unwrap();
      navigate(`/groups/${result.group_id}`);
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setActionError(
        err?.data?.detail ?? "Failed to accept invitation. Please try again."
      );
      setPendingAction(null);
    }
  };

  const handleDecline = async (invitation: MyInvitation) => {
    setActionError(null);
    setPendingAction({ id: invitation.id, action: "decline" });
    try {
      await decline(invitation.token).unwrap();
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setActionError(
        err?.data?.detail ?? "Failed to decline invitation. Please try again."
      );
    } finally {
      setPendingAction(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const isEmpty = !invitations || invitations.length === 0;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Pending Invitations</h1>
        <p className="text-muted-foreground mt-1">
          {isEmpty
            ? "You have no pending invitations."
            : `You have ${invitations.length} pending invitation${invitations.length !== 1 ? "s" : ""}.`}
        </p>
      </div>

      {actionError && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{actionError}</AlertDescription>
        </Alert>
      )}

      {isEmpty ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <Mail className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium">
            No pending invitations
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            When someone invites you to a group, it will appear here.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {invitations.map((invitation) => {
            const isAccepting =
              pendingAction?.id === invitation.id &&
              pendingAction.action === "accept";
            const isDeclining =
              pendingAction?.id === invitation.id &&
              pendingAction.action === "decline";
            const isBusy = isAccepting || isDeclining;

            return (
              <Card key={invitation.id} className="p-5 hover:shadow-md">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4 min-w-0">
                    {/* Group avatar letter */}
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground font-bold text-lg shrink-0">
                      {invitation.group_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-base truncate">
                        {invitation.group_name}
                      </p>
                      <p className="text-sm text-muted-foreground truncate">
                        Invited by{" "}
                        {invitation.inviter_full_name ?? "a member"} ·{" "}
                        {formatDate(invitation.created_at)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDecline(invitation)}
                      disabled={isBusy}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      {isDeclining ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span className="ml-1.5 hidden sm:inline">Decline</span>
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAccept(invitation)}
                      disabled={isBusy}
                    >
                      {isAccepting ? (
                        <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
                      ) : (
                        <CheckCircle className="mr-1.5 h-4 w-4" />
                      )}
                      Accept
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
