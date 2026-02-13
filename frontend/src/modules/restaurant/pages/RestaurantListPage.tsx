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
import {
  useCreateRestaurantMutation,
  useDeleteRestaurantMutation,
  useGetRestaurantsQuery,
} from "@/store/api/restaurantApi";
import { ArrowRight, Plus, Trash2, UtensilsCrossed } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

export function RestaurantListPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const { data: restaurants, isLoading } = useGetRestaurantsQuery(groupId!);
  const [createRestaurant] = useCreateRestaurantMutation();
  const [deleteRestaurant] = useDeleteRestaurantMutation();

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const handleCreate = async () => {
    try {
      await createRestaurant({
        groupId: groupId!,
        data: { name, description: description || undefined },
      }).unwrap();
      setOpen(false);
      setName("");
      setDescription("");
    } catch {
      // handled
    }
  };

  const handleDelete = async (restaurantId: string) => {
    if (!confirm("Delete this restaurant and all its dishes?")) return;
    await deleteRestaurant({ groupId: groupId!, restaurantId });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Restaurants</h1>
          <p className="text-muted-foreground mt-1">
            Manage your group&apos;s favorite places to eat.
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
              <Plus className="mr-2 h-4 w-4" />
              Add Restaurant
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Restaurant</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Pizza Place"
                />
              </div>
              <div className="space-y-2">
                <Label>Description (optional)</Label>
                <Input
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <Button
                onClick={handleCreate}
                disabled={!name.trim()}
                className="w-full"
              >
                Add
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {restaurants && restaurants.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <UtensilsCrossed className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">
            No restaurants yet
          </p>
          <p className="text-sm text-muted-foreground">
            Add one to build your group&apos;s menu!
          </p>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {restaurants?.map((r) => (
            <Card key={r.id} className="p-5 hover:shadow-md group">
              <div className="flex items-center justify-between gap-2">
                <Link
                  to={`/groups/${groupId}/restaurants/${r.id}`}
                  className="flex items-center gap-3 flex-1 min-w-0"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-rose-50 text-rose-600 shrink-0 group-hover:scale-105 transition-transform">
                    <UtensilsCrossed className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold truncate group-hover:text-primary transition-colors">
                      {r.name}
                    </h3>
                    {r.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {r.description}
                      </p>
                    )}
                  </div>
                </Link>
                <div className="flex items-center justify-end gap-1 shrink-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(r.id)}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Link to={`/groups/${groupId}/restaurants/${r.id}`}>
                    <ArrowRight className="h-4 w-4 text-muted-foreground opacity-100" />
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
