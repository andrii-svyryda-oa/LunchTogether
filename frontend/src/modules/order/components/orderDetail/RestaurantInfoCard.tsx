import { Linkify } from "@/components/common/Linkify/Linkify";
import { Card } from "@/components/ui/card";
import type { RestaurantDetail } from "@/types";
import { Info } from "lucide-react";

interface RestaurantInfoCardProps {
  restaurant: RestaurantDetail;
}

export function RestaurantInfoCard({ restaurant }: RestaurantInfoCardProps) {
  if (!restaurant.description && !restaurant.menu_url) return null;

  return (
    <Card className="p-5 mb-8 border-l-4 border-l-primary bg-primary/5">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
          <Info className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1 space-y-3">
          {restaurant.description && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                Description
              </p>
              <p className="text-sm whitespace-pre-line">
                {restaurant.description}
              </p>
            </div>
          )}
          {restaurant.menu_url && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                Ordering details
              </p>
              <Linkify
                text={restaurant.menu_url}
                className="block text-sm whitespace-pre-line break-words"
              />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
