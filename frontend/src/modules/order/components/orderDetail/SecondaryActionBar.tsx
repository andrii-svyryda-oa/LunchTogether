import { Button } from "@/components/ui/button";
import type { GroupMember } from "@/types";
import { Plus } from "lucide-react";
import { useState } from "react";
import {
  MemberPickerDialog,
  type ParticipantEntry,
} from "./MemberPickerDialog";

interface SecondaryActionBarProps {
  canEditInitiated: boolean;
  canEditConfirmed: boolean;
  participants: ParticipantEntry[];
  otherMembers: GroupMember[];
  onAddForSelf: () => void;
  onAddForMember: (userId: string) => void;
}

export function SecondaryActionBar({
  canEditInitiated,
  canEditConfirmed,
  participants,
  otherMembers,
  onAddForSelf,
  onAddForMember,
}: SecondaryActionBarProps) {
  const [pickerOpen, setPickerOpen] = useState(false);

  if (!canEditInitiated && !canEditConfirmed) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-8">
      {canEditInitiated && (
        <Button className="shadow-md shadow-primary/20" onClick={onAddForSelf}>
          <Plus className="mr-2 h-4 w-4" />
          Add Dish
        </Button>
      )}

      {canEditConfirmed && (
        <Button
          className="shadow-md shadow-primary/20"
          onClick={() => setPickerOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Dish for Member
        </Button>
      )}

      <MemberPickerDialog
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        participants={participants}
        otherMembers={otherMembers}
        onSelect={onAddForMember}
      />
    </div>
  );
}
