import { Link, useNavigate } from "react-router-dom";
import { LogOut, Menu, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks";
import { ROUTES } from "@/constants";
import { APP } from "@/constants";

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout().unwrap();
      navigate(ROUTES.LOGIN);
    } catch {
      // Error handled by RTK Query
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-lg supports-backdrop-filter:bg-background/60">
      <div className="flex h-16 items-center px-4 gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0 md:hidden"
          onClick={onToggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </Button>

        <Link to={ROUTES.HOME} className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-linear-to-br from-orange-500 to-amber-500 shadow-md shadow-orange-500/20">
            <UtensilsCrossed className="h-4.5 w-4.5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">{APP.NAME}</span>
        </Link>

        <div className="flex-1" />

        <div className="flex items-center gap-1">
          {isAuthenticated && user ? (
            <>
              <Button variant="ghost" size="sm" asChild className="gap-2">
                <Link to={ROUTES.PROFILE}>
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-linear-to-br from-orange-500 to-amber-500 text-[11px] font-bold text-white">
                    {user.full_name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="hidden sm:inline">{user.full_name}</span>
                </Link>
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="text-muted-foreground hover:text-foreground"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.LOGIN}>Sign in</Link>
              </Button>
              <Button size="sm" asChild className="rounded-lg shadow-md shadow-primary/20">
                <Link to={ROUTES.REGISTER}>Get Started</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
