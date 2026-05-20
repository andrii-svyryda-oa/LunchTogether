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
import { Textarea } from "@/components/ui/textarea";
import { useGroupPermissions } from "@/hooks";
import {
  useCreateDishMutation,
  useDeleteDishMutation,
  useGetRestaurantQuery,
  useUpdateRestaurantMutation,
} from "@/store/api/restaurantApi";
import { Pencil, Plus, Trash2, UtensilsCrossed } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export function RestaurantDetailPage() {
  const { groupId, restaurantId } = useParams<{
    groupId: string;
    restaurantId: string;
  }>();
  const { data: restaurant, isLoading } = useGetRestaurantQuery({
    groupId: groupId!,
    restaurantId: restaurantId!,
  });
  const [createDish] = useCreateDishMutation();
  const [deleteDish] = useDeleteDishMutation();
  const [updateRestaurant] = useUpdateRestaurantMutation();
  const { canEditRestaurants } = useGroupPermissions(groupId);

  const [open, setOpen] = useState(false);
  const [dishName, setDishName] = useState("");
  const [dishDetail, setDishDetail] = useState("");
  const [dishPrice, setDishPrice] = useState("");

  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editMenuUrl, setEditMenuUrl] = useState("");
  const [editError, setEditError] = useState<string | null>(null);

  useEffect(() => {
    if (editOpen && restaurant) {
      setEditName(restaurant.name);
      setEditDescription(restaurant.description ?? "");
      setEditMenuUrl(restaurant.menu_url ?? "");
      setEditError(null);
    }
  }, [editOpen, restaurant]);

  const handleSaveDetails = async () => {
    setEditError(null);
    try {
      await updateRestaurant({
        groupId: groupId!,
        restaurantId: restaurantId!,
        data: {
          name: editName,
          description: editDescription ? editDescription : null,
          menu_url: editMenuUrl ? editMenuUrl : null,
        },
      }).unwrap();
      setEditOpen(false);
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setEditError(err?.data?.detail ?? "Failed to update restaurant.");
    }
  };

  const handleAddDish = async () => {
    try {
      await createDish({
        groupId: groupId!,
        restaurantId: restaurantId!,
        data: {
          name: dishName,
          detail: dishDetail || undefined,
          price: parseFloat(dishPrice),
        },
      }).unwrap();
      setOpen(false);
      setDishName("");
      setDishDetail("");
      setDishPrice("");
    } catch {
      // handled
    }
  };

  const handleDeleteDish = async (dishId: string) => {
    if (!confirm("Delete this dish?")) return;
    await deleteDish({
      groupId: groupId!,
      restaurantId: restaurantId!,
      dishId,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!restaurant) {
    return <Alert variant="destructive">Restaurant not found.</Alert>;
  }

  return (
    <div>
      <div className="flex items-start justify-between mb-8 gap-4">
        <div className="flex items-start gap-4 min-w-0 flex-1">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 shadow-sm shrink-0">
            <UtensilsCrossed className="h-7 w-7" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-3xl font-bold tracking-tight">
                {restaurant.name}
              </h1>
              {canEditRestaurants && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setEditOpen(true)}
                  className="h-8 w-8 text-muted-foreground hover:text-primary"
                  aria-label="Edit restaurant details"
                >
                  <Pencil className="h-4 w-4" />
                </Button>
              )}
            </div>
            {restaurant.description && (
              <p className="text-muted-foreground mt-1 whitespace-pre-line">
                {restaurant.description}
              </p>
            )}
            {restaurant.menu_url && (
              <div className="mt-3 rounded-lg bg-muted/60 px-3 py-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                  Ordering details
                </p>
                <p className="text-sm whitespace-pre-line break-words">
                  {restaurant.menu_url}
                </p>
              </div>
            )}
          </div>
        </div>
        {canEditRestaurants && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="shadow-md shadow-primary/20 shrink-0">
                <Plus className="mr-2 h-4 w-4" />
                Add Dish
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Dish</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input
                    value={dishName}
                    onChange={(e) => setDishName(e.target.value)}
                    placeholder="Margherita Pizza"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Detail (optional)</Label>
                  <Input
                    value={dishDetail}
                    onChange={(e) => setDishDetail(e.target.value)}
                    placeholder="Large, extra cheese"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Price</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={dishPrice}
                    onChange={(e) => setDishPrice(e.target.value)}
                    placeholder="12.99"
                  />
                </div>
                <Button
                  onClick={handleAddDish}
                  disabled={!dishName.trim() || !dishPrice}
                  className="w-full"
                >
                  Add Dish
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <div className="flex items-center gap-2 mb-5">
        <h2 className="text-xl font-semibold">Menu</h2>
        <span className="text-sm text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
          {restaurant.dishes?.length ?? 0} dishes
        </span>
      </div>

      {restaurant.dishes && restaurant.dishes.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 border-dashed">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted mb-4">
            <UtensilsCrossed className="h-7 w-7 text-muted-foreground" />
          </div>
          <p className="text-muted-foreground font-medium mb-1">
            No dishes yet
          </p>
          <p className="text-sm text-muted-foreground">
            Add one to build the menu!
          </p>
        </Card>
      ) : (
        <div className="space-y-2">
          {restaurant.dishes?.map((dish) => (
            <Card key={dish.id} className="p-4 hover:shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{dish.name}</p>
                  {dish.detail && (
                    <p className="text-sm text-muted-foreground">
                      {dish.detail}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-primary">
                    {Number(dish.price).toFixed(2)} ₴
                  </span>
                  {canEditRestaurants && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteDish(dish.id)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Restaurant Details</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            {editError && (
              <Alert variant="destructive" className="text-sm">
                {editError}
              </Alert>
            )}
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Pizza Place"
              />
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="What makes this place special..."
                maxLength={1000}
                rows={4}
              />
            </div>
            <div className="space-y-2">
              <Label>Ordering Details</Label>
              <Textarea
                value={editMenuUrl}
                onChange={(e) => setEditMenuUrl(e.target.value)}
                placeholder="Phone, website, hours, delivery notes..."
                maxLength={2000}
                rows={3}
              />
            </div>
            <Button
              onClick={handleSaveDetails}
              disabled={!editName.trim()}
              className="w-full"
            >
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
