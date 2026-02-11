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
import { Plus, Trash2 } from "lucide-react";
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
      <div className="flex items-center justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Restaurants</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Restaurant
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Restaurant</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label>Name</Label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Pizza Place"
                />
              </div>
              <div>
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
        <p className="text-center text-muted-foreground py-12">
          No restaurants yet. Add one to get started!
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {restaurants?.map((r) => (
            <Card key={r.id} className="p-4">
              <div className="flex items-center justify-between">
                <Link
                  to={`/groups/${groupId}/restaurants/${r.id}`}
                  className="flex-1"
                >
                  <h3 className="font-semibold hover:underline">{r.name}</h3>
                  {r.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {r.description}
                    </p>
                  )}
                </Link>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(r.id)}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
