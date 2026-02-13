import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ROUTES } from "@/constants";
import { useAuth } from "@/hooks";
import {
  useCreateGroupMutation,
  useGetGroupsQuery,
} from "@/store/api/groupApi";
import { cn } from "@/utils";
import {
  Home,
  LayoutDashboard,
  Plus,
  Settings,
  ShieldCheck,
  ShoppingCart,
  User,
  Users,
  UtensilsCrossed,
  Wallet,
} from "lucide-react";
import { useState } from "react";
import { NavLink, useLocation, useParams } from "react-router-dom";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

// Pages that belong to the "home" context
const HOME_PATHS = ["/", "/profile", "/settings", "/users"];

function isHomeContext(pathname: string): boolean {
  return HOME_PATHS.some(
    (p) => pathname === p || (p !== "/" && pathname.startsWith(p + "/"))
  );
}

function isGroupContext(pathname: string): boolean {
  return pathname.startsWith("/groups/");
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user } = useAuth();
  const { data: groups } = useGetGroupsQuery();
  const location = useLocation();
  const { groupId } = useParams<{ groupId: string }>();
  const [createGroup] = useCreateGroupMutation();
  const [createOpen, setCreateOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupDesc, setNewGroupDesc] = useState("");

  // Determine which groupId is active from the URL
  const activeGroupId =
    groupId ??
    (isGroupContext(location.pathname)
      ? location.pathname.split("/")[2]
      : undefined);

  const inHomeContext =
    isHomeContext(location.pathname) && !isGroupContext(location.pathname);
  const inGroupContext = isGroupContext(location.pathname);

  const handleCreateGroup = async () => {
    try {
      await createGroup({
        name: newGroupName,
        description: newGroupDesc || undefined,
      }).unwrap();
      setCreateOpen(false);
      setNewGroupName("");
      setNewGroupDesc("");
    } catch {
      // Error handled by RTK Query
    }
  };

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
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Discord-like icon bar */}
        <div className="w-18 border-r border-sidebar-border flex flex-col items-center py-3 gap-2 overflow-y-auto">
          {/* Home button */}
          <NavLink
            to={ROUTES.HOME}
            onClick={onClose}
            className={() =>
              cn(
                "h-11 w-11 rounded-2xl flex items-center justify-center transition-all duration-200 hover:rounded-xl group",
                inHomeContext
                  ? "bg-primary text-primary-foreground rounded-xl shadow-lg shadow-primary/30"
                  : "bg-sidebar-accent text-sidebar-foreground hover:bg-primary/20 hover:text-primary"
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
              state={{ autoNavigate: true }}
              onClick={onClose}
              title={group.name}
              className={() =>
                cn(
                  "h-11 w-11 rounded-2xl flex items-center justify-center text-sm font-bold transition-all duration-200 hover:rounded-xl",
                  activeGroupId === group.id
                    ? "bg-primary text-primary-foreground rounded-xl shadow-lg shadow-primary/30"
                    : "bg-sidebar-accent text-sidebar-foreground hover:bg-sidebar-border"
                )
              }
            >
              {group.name.charAt(0).toUpperCase()}
            </NavLink>
          ))}

          {/* Add group button */}
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <button
                className="h-11 w-11 rounded-2xl flex items-center justify-center text-sm transition-all duration-200 hover:rounded-xl bg-sidebar-accent text-sidebar-foreground hover:bg-primary/15 hover:text-primary cursor-pointer hover:scale-105"
                title="Create Group"
              >
                <Plus className="h-5 w-5" />
              </button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Group</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="sidebar-group-name">Name</Label>
                  <Input
                    id="sidebar-group-name"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                    placeholder="Lunch crew"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sidebar-group-desc">
                    Description (optional)
                  </Label>
                  <Input
                    id="sidebar-group-desc"
                    value={newGroupDesc}
                    onChange={(e) => setNewGroupDesc(e.target.value)}
                    placeholder="Our daily lunch group"
                  />
                </div>
                <Button
                  onClick={handleCreateGroup}
                  disabled={!newGroupName.trim()}
                  className="w-full"
                >
                  Create
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Context-dependent sub-navigation */}
        <nav className="flex-1 flex flex-col p-3 overflow-y-auto">
          {inHomeContext && (
            <>
              <div className="space-y-0.5">
                <p className="text-[11px] font-semibold text-sidebar-foreground/40 uppercase tracking-wider px-3 mb-2">
                  Navigation
                </p>
                <NavLink
                  to={ROUTES.HOME}
                  end
                  onClick={onClose}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-primary"
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                    )
                  }
                >
                  <Home className="h-4 w-4" />
                  Home
                </NavLink>

                <NavLink
                  to={ROUTES.PROFILE}
                  onClick={onClose}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-primary"
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
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
                        : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                    )
                  }
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </NavLink>
              </div>

              {user?.role === "admin" && (
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
                          : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                      )
                    }
                  >
                    <ShieldCheck className="h-4 w-4" />
                    Manage Users
                  </NavLink>
                </div>
              )}
            </>
          )}

          {inGroupContext && activeGroupId && (
            <div className="space-y-0.5">
              <p className="text-[11px] font-semibold text-sidebar-foreground/40 uppercase tracking-wider px-3 mb-2">
                Group
              </p>
              <NavLink
                to={`/groups/${activeGroupId}`}
                end
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </NavLink>

              <NavLink
                to={`/groups/${activeGroupId}/members`}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <Users className="h-4 w-4" />
                Members
              </NavLink>

              <NavLink
                to={`/groups/${activeGroupId}/restaurants`}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <UtensilsCrossed className="h-4 w-4" />
                Restaurants
              </NavLink>

              <NavLink
                to={`/groups/${activeGroupId}/orders`}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <ShoppingCart className="h-4 w-4" />
                Orders
              </NavLink>

              <NavLink
                to={`/groups/${activeGroupId}/balances`}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <Wallet className="h-4 w-4" />
                Balances
              </NavLink>
            </div>
          )}
        </nav>
      </aside>
    </>
  );
}
