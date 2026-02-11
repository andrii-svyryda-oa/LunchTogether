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
import {
  useCreateDishMutation,
  useDeleteDishMutation,
  useGetRestaurantQuery,
} from "@/store/api/restaurantApi";
import { Plus, Trash2, UtensilsCrossed } from "lucide-react";
import { useState } from "react";
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

  const [open, setOpen] = useState(false);
  const [dishName, setDishName] = useState("");
  const [dishDetail, setDishDetail] = useState("");
  const [dishPrice, setDishPrice] = useState("");

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
    <div className="animate-slide-up">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600 shadow-sm shrink-0">
            <UtensilsCrossed className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {restaurant.name}
            </h1>
            {restaurant.description && (
              <p className="text-muted-foreground">{restaurant.description}</p>
            )}
          </div>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="shadow-md shadow-primary/20">
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
                    ${Number(dish.price).toFixed(2)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteDish(dish.id)}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
