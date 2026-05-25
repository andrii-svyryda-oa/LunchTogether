import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { GroupMember } from "@/types";

export interface ParticipantEntry {
  userId: string;
  name: string;
}

interface MemberPickerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  participants: ParticipantEntry[];
  otherMembers: GroupMember[];
  onSelect: (userId: string) => void;
}

export function MemberPickerDialog({
  open,
  onOpenChange,
  participants,
  otherMembers,
  onSelect,
}: MemberPickerDialogProps) {
  const handlePick = (userId: string) => {
    onOpenChange(false);
    onSelect(userId);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Select Member</DialogTitle>
        </DialogHeader>
        <div className="space-y-2 pt-4 max-h-80 overflow-y-auto">
          {participants.map((p) => (
            <Button
              key={p.userId}
              variant="outline"
              className="w-full justify-start"
              onClick={() => handlePick(p.userId)}
            >
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-[10px] font-bold mr-2 shrink-0">
                {p.name.charAt(0).toUpperCase()}
              </div>
              {p.name}
            </Button>
          ))}

          {otherMembers.length > 0 && (
            <>
              {participants.length > 0 && <div className="border-t my-2" />}
              <p className="text-xs text-muted-foreground px-1 pb-1">
                Other group members
              </p>
              {otherMembers.map((member) => (
                <Button
                  key={member.user_id}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => handlePick(member.user_id)}
                >
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-muted-foreground text-[10px] font-bold mr-2 shrink-0">
                    {(member.user_full_name ?? "?").charAt(0).toUpperCase()}
                  </div>
                  {member.user_full_name ?? member.user_email}
                </Button>
              ))}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
