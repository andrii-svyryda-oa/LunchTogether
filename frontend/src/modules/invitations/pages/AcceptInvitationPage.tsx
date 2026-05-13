import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { APP, ROUTES } from "@/constants";
import { useAuth } from "@/hooks";
import { useGetInvitationByTokenQuery } from "@/store/api/groupApi";
import {
  fullNameSchema,
  passwordSchema,
} from "@/utils/validation";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertCircle, Loader2, UtensilsCrossed } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { z } from "zod/v4";

// ------- invite-register schema -------
const inviteRegisterSchema = z.object({
  full_name: fullNameSchema,
  password: passwordSchema,
});
type InviteRegisterFormData = z.infer<typeof inviteRegisterSchema>;

// ------- main page -------
export function AcceptInvitationPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const { data: preview, isLoading, isError } = useGetInvitationByTokenQuery(token, {
    skip: !token,
  });

  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  if (!token) {
    return <InvalidInviteCard message="No invitation token provided." />;
  }

  if (isLoading || authLoading) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (isError || !preview) {
    return (
      <InvalidInviteCard message="This invitation is not valid or has already been used." />
    );
  }

  // Logged in — email mismatch
  if (isAuthenticated && user && user.email !== preview.invitee_email) {
    return <EmailMismatchCard preview={preview} />;
  }

  // Logged in — emails match → go straight to pending invites page
  if (isAuthenticated && user && user.email === preview.invitee_email) {
    return <Navigate to={ROUTES.INVITATIONS} replace />;
  }

  // Not logged in, account exists → go to login with prefill
  if (preview.invitee_has_account && !isAuthenticated) {
    return (
      <Navigate
        to={ROUTES.LOGIN}
        state={{
          prefillEmail: preview.invitee_email,
          from: { pathname: ROUTES.INVITATIONS },
        }}
        replace
      />
    );
  }

  // New user — show register form
  return <RegisterAndJoinCard preview={preview} />;
}

// ------- sub-components -------

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-lg shadow-primary/25 mb-4">
            <UtensilsCrossed className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">{APP.NAME}</h1>
        </div>
        {children}
      </div>
    </div>
  );
}

function InvalidInviteCard({ message }: { message: string }) {
  return (
    <PageShell>
      <Card className="border-0 shadow-xl shadow-black/5">
        <CardHeader className="text-center">
          <CardTitle>Invitation Not Found</CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        <CardContent>
          <a
            href={ROUTES.HOME}
            className="block w-full text-center text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Go to home
          </a>
        </CardContent>
      </Card>
    </PageShell>
  );
}

interface PreviewProps {
  preview: import("@/types").InvitationPreview;
}

function EmailMismatchCard({ preview }: PreviewProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleSwitchAccount = async () => {
    setIsLoggingOut(true);
    try {
      await logout().unwrap();
    } catch {
      // Continue to login even if logout fails
    }
    navigate(ROUTES.LOGIN, {
      state: {
        prefillEmail: preview.invitee_email,
        from: { pathname: ROUTES.INVITATIONS },
      },
    });
  };

  return (
    <PageShell>
      <Card className="border-0 shadow-xl shadow-black/5">
        <CardHeader className="text-center">
          <CardTitle>Wrong Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              This invitation is for{" "}
              <span className="font-semibold">{preview.invitee_email}</span> but
              you are signed in as{" "}
              <span className="font-semibold">{user?.email}</span>.
            </AlertDescription>
          </Alert>
          <Button
            className="w-full"
            onClick={handleSwitchAccount}
            disabled={isLoggingOut}
          >
            {isLoggingOut && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Sign out and sign in as {preview.invitee_email}
          </Button>
        </CardContent>
      </Card>
    </PageShell>
  );
}

function RegisterAndJoinCard({ preview }: PreviewProps) {
  const { register: registerUser, login, isRegistering } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<InviteRegisterFormData>({
    resolver: zodResolver(inviteRegisterSchema),
    defaultValues: { full_name: "", password: "" },
  });

  // Keep isSubmitting in sync with isRegistering from the hook
  useEffect(() => {
    if (!isRegistering) setIsSubmitting(false);
  }, [isRegistering]);

  const onSubmit = async (data: InviteRegisterFormData) => {
    setServerError(null);
    setIsSubmitting(true);
    try {
      await registerUser({
        email: preview.invitee_email,
        full_name: data.full_name,
        password: data.password,
      }).unwrap();

      // Auto-login with the newly created credentials
      await login({
        email: preview.invitee_email,
        password: data.password,
      }).unwrap();

      navigate(ROUTES.INVITATIONS);
    } catch (error: unknown) {
      const err = error as { data?: { detail?: string } };
      setServerError(
        err?.data?.detail ?? "Could not create account. Please try again."
      );
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell>
      <Card className="border-0 shadow-xl shadow-black/5">
        <CardHeader>
          <CardTitle>Join {preview.group_name}</CardTitle>
          <CardDescription>
            <span className="font-medium">{preview.inviter_full_name}</span>{" "}
            invited you to join{" "}
            <span className="font-medium">{preview.group_name}</span>. Create an
            account to accept this invitation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              {serverError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{serverError}</AlertDescription>
                </Alert>
              )}

              {/* Email is locked to the invitee address */}
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  value={preview.invitee_email}
                  readOnly
                  disabled
                  className="bg-muted"
                />
              </div>

              <FormField
                control={form.control}
                name="full_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Full Name</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter your full name"
                        autoComplete="name"
                        autoFocus
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        placeholder="Create a password"
                        autoComplete="new-password"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Create Account &amp; Continue
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </PageShell>
  );
}
