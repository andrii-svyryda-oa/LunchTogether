import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { RegisterForm } from "../components/RegisterForm";
import { APP } from "@/constants";
import { UtensilsCrossed } from "lucide-react";

export function RegisterPage() {
  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md animate-slide-up">
        {/* Branded header */}
        <div className="text-center mb-8">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-linear-to-br from-orange-500 to-amber-500 shadow-lg shadow-orange-500/25 mb-4">
            <UtensilsCrossed className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">{APP.NAME}</h1>
          <p className="text-muted-foreground mt-1">Create a new account</p>
        </div>

        {/* Form card */}
        <Card className="border-0 shadow-xl shadow-black/5">
          <CardContent className="pt-6">
            <RegisterForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
