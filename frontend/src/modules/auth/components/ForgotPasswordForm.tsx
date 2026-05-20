import { Link } from "react-router-dom";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { useForgotPasswordForm } from "../hooks/useForgotPasswordForm";
import { ROUTES } from "@/constants";

export function ForgotPasswordForm() {
  const { form, onSubmit, serverError, successMessage, isSubmitting } =
    useForgotPasswordForm();

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        {serverError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{serverError}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert>
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="Enter your email"
                  autoComplete="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Send Reset Link
        </Button>

        <p className="text-center text-sm text-muted-foreground">
          Remembered your password?{" "}
          <Link
            to={ROUTES.LOGIN}
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Back to login
          </Link>
        </p>
      </form>
    </Form>
  );
}
