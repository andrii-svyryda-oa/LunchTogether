import { ROUTES } from "@/constants";
import { useAuth } from "@/hooks";
import { useGetGroupsQuery } from "@/store/api/groupApi";
import { cn } from "@/utils";
import { Home, Settings, ShieldCheck, User, Users } from "lucide-react";
import { NavLink } from "react-router-dom";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user } = useAuth();
  const { data: groups } = useGetGroupsQuery();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-64 border-r bg-background transition-transform duration-200 flex",
          "md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        {/* Discord-like icon bar */}
        <div className="w-16 border-r bg-muted/30 flex flex-col items-center py-3 gap-2 overflow-y-auto">
          {/* Home button */}
          <NavLink
            to={ROUTES.HOME}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "h-10 w-10 rounded-xl flex items-center justify-center transition-all hover:rounded-lg",
                isActive
                  ? "bg-primary text-primary-foreground rounded-lg"
                  : "bg-muted hover:bg-primary/20",
              )
            }
          >
            <Home className="h-5 w-5" />
          </NavLink>

          <div className="w-8 border-t my-1" />

          {/* Group icons */}
          {groups?.map((group) => (
            <NavLink
              key={group.id}
              to={`/groups/${group.id}`}
              onClick={onClose}
              title={group.name}
              className={({ isActive }) =>
                cn(
                  "h-10 w-10 rounded-xl flex items-center justify-center text-sm font-bold transition-all hover:rounded-lg",
                  isActive
                    ? "bg-primary text-primary-foreground rounded-lg"
                    : "bg-muted hover:bg-primary/20",
                )
              }
            >
              {group.name.charAt(0).toUpperCase()}
            </NavLink>
          ))}
        </div>

        {/* Navigation links */}
        <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
          <NavLink
            to={ROUTES.HOME}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Home className="h-4 w-4" />
            Home
          </NavLink>

          <NavLink
            to={ROUTES.GROUPS}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Users className="h-4 w-4" />
            Groups
          </NavLink>

          <NavLink
            to={ROUTES.PROFILE}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <User className="h-4 w-4" />
            Profile
          </NavLink>

          <NavLink
            to={ROUTES.SETTINGS}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Settings className="h-4 w-4" />
            Settings
          </NavLink>

          {user?.is_admin && (
            <>
              <div className="pt-3 pb-1">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-3">
                  Admin
                </p>
              </div>
              <NavLink
                to={ROUTES.USERS}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                  )
                }
              >
                <ShieldCheck className="h-4 w-4" />
                Manage Users
              </NavLink>
            </>
          )}
        </nav>
      </aside>
    </>
  );
}
