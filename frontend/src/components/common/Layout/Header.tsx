import { Link, useNavigate } from "react-router-dom";
import { LogOut, User, Menu } from "lucide-react";
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
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center px-4">
        <Button
          variant="ghost"
          size="icon"
          className="mr-2 md:hidden"
          onClick={onToggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </Button>

        <Link to={ROUTES.HOME} className="mr-6 flex items-center space-x-2">
          <span className="font-bold text-lg">{APP.NAME}</span>
        </Link>

        <div className="flex flex-1 items-center justify-end space-x-2">
          {isAuthenticated && user ? (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.PROFILE}>
                  <User className="mr-2 h-4 w-4" />
                  {user.full_name}
                </Link>
              </Button>
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to={ROUTES.LOGIN}>Login</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to={ROUTES.REGISTER}>Register</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
