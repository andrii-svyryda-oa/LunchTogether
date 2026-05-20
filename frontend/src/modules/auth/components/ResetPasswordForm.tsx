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
import { AlertCircle, Loader2 } from "lucide-react";
import { useResetPasswordForm } from "../hooks/useResetPasswordForm";
import { ROUTES } from "@/constants";

export function ResetPasswordForm() {
  const { form, onSubmit, serverError, isSubmitting, hasToken } =
    useResetPasswordForm();

  if (!hasToken) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            This reset link is missing or invalid. Please request a new one.
          </AlertDescription>
        </Alert>
        <Button asChild className="w-full">
          <Link to={ROUTES.FORGOT_PASSWORD}>Request a new link</Link>
        </Button>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        {serverError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{serverError}</AlertDescription>
          </Alert>
        )}

        <FormField
          control={form.control}
          name="new_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>New password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Enter a new password"
                  autoComplete="new-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="confirm_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Repeat the new password"
                  autoComplete="new-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Reset Password
        </Button>

        <p className="text-center text-sm text-muted-foreground">
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
