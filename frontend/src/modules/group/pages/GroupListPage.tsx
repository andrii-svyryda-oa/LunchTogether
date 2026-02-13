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
import { ArrowRight, Plus, Users } from "lucide-react";
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
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <Alert variant="destructive">Failed to load groups.</Alert>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Groups</h1>
          <p className="text-muted-foreground mt-1">
            Manage your lunch groups and create new ones.
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
              <Plus className="mr-2 h-4 w-4" />
              Create Group
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Group</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="group-name">Name</Label>
                <Input
                  id="group-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Lunch crew"
                />
              </div>
              <div className="space-y-2">
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
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <Users className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">
            No groups yet
          </p>
          <p className="text-sm text-muted-foreground">
            Create one to get started ordering lunch together!
          </p>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {groups?.map((group) => (
            <Link key={group.id} to={`/groups/${group.id}`}>
              <Card className="p-5 hover:shadow-md hover:border-primary/30 cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-lg shrink-0 group-hover:scale-105 transition-transform shadow-sm">
                    {group.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold truncate">{group.name}</h3>
                    {group.description && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {group.description}
                      </p>
                    )}
                    {group.owner_id === user?.id && (
                      <span className="mt-1.5 inline-block text-[11px] font-medium bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                        Owner
                      </span>
                    )}
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
