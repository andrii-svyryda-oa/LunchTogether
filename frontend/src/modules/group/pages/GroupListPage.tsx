import { Alert } from "@/components/ui/alert";
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
  useCreateGroupMutation,
  useGetGroupsQuery,
} from "@/store/api/groupApi";
import { Plus } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

export function GroupListPage() {
  const { data: groups, isLoading, error } = useGetGroupsQuery();
  const [createGroup] = useCreateGroupMutation();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const handleCreate = async () => {
    try {
      await createGroup({
        name,
        description: description || undefined,
      }).unwrap();
      setOpen(false);
      setName("");
      setDescription("");
    } catch {
      // Error handled by RTK Query
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <Alert variant="destructive">Failed to load groups.</Alert>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">My Groups</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Group
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Group</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label htmlFor="group-name">Name</Label>
                <Input
                  id="group-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Lunch crew"
                />
              </div>
              <div>
                <Label htmlFor="group-desc">Description (optional)</Label>
                <Input
                  id="group-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Our daily lunch group"
                />
              </div>
              <Button
                onClick={handleCreate}
                disabled={!name.trim()}
                className="w-full"
              >
                Create
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {groups && groups.length === 0 ? (
        <p className="text-center text-muted-foreground py-12">
          You don't belong to any groups yet. Create one to get started!
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {groups?.map((group) => (
            <Link key={group.id} to={`/groups/${group.id}`}>
              <Card className="p-6 hover:border-primary transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
                    {group.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold">{group.name}</h3>
                    {group.description && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {group.description}
                      </p>
                    )}
                  </div>
                </div>
                {group.owner_id === user?.id && (
                  <span className="mt-3 inline-block text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                    Owner
                  </span>
                )}
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
