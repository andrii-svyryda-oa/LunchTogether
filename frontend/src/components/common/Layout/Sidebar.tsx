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

const GROUP_GRADIENTS = [
  "from-orange-500 to-amber-500",
  "from-blue-500 to-indigo-500",
  "from-emerald-500 to-teal-500",
  "from-purple-500 to-violet-500",
  "from-pink-500 to-rose-500",
  "from-cyan-500 to-sky-500",
];

function getGroupGradient(name: string): string {
  const index = name.charCodeAt(0) % GROUP_GRADIENTS.length;
  return GROUP_GRADIENTS[index];
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user } = useAuth();
  const { data: groups } = useGetGroupsQuery();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 border-r border-sidebar-border bg-sidebar-background transition-transform duration-300 ease-in-out flex",
          "md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        {/* Discord-like icon bar */}
        <div className="w-18 border-r border-sidebar-border flex flex-col items-center py-3 gap-2 overflow-y-auto">
          {/* Home button */}
          <NavLink
            to={ROUTES.HOME}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "h-11 w-11 rounded-2xl flex items-center justify-center transition-all duration-200 hover:rounded-xl group",
                isActive
                  ? "bg-primary text-primary-foreground rounded-xl shadow-lg shadow-primary/30"
                  : "bg-sidebar-accent text-sidebar-foreground hover:bg-primary/20 hover:text-primary",
              )
            }
          >
            <Home className="h-5 w-5" />
          </NavLink>

          <div className="w-8 h-px bg-sidebar-border my-1" />

          {/* Group icons */}
          {groups?.map((group) => (
            <NavLink
              key={group.id}
              to={`/groups/${group.id}`}
              onClick={onClose}
              title={group.name}
              className={({ isActive }) =>
                cn(
                  "h-11 w-11 rounded-2xl flex items-center justify-center text-sm font-bold transition-all duration-200 hover:rounded-xl",
                  isActive
                    ? `bg-linear-to-br ${getGroupGradient(
                        group.name,
                      )} text-white rounded-xl shadow-lg`
                    : "bg-sidebar-accent text-sidebar-foreground hover:bg-sidebar-border",
                )
              }
            >
              {group.name.charAt(0).toUpperCase()}
            </NavLink>
          ))}
        </div>

        {/* Navigation links */}
        <nav className="flex-1 flex flex-col p-3 overflow-y-auto">
          <div className="space-y-0.5">
            <p className="text-[11px] font-semibold text-sidebar-foreground/40 uppercase tracking-wider px-3 mb-2">
              Navigation
            </p>
            <NavLink
              to={ROUTES.HOME}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-primary"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
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
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-primary"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
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
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-primary"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
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
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-primary"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                )
              }
            >
              <Settings className="h-4 w-4" />
              Settings
            </NavLink>
          </div>

          {user?.is_admin && (
            <div className="mt-auto pt-4">
              <p className="text-[11px] font-semibold text-sidebar-foreground/40 uppercase tracking-wider px-3 mb-2">
                Admin
              </p>
              <NavLink
                to={ROUTES.USERS}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  )
                }
              >
                <ShieldCheck className="h-4 w-4" />
                Manage Users
              </NavLink>
            </div>
          )}
        </nav>
      </aside>
    </>
  );
}
