import { APP } from "@/constants";

export function Footer() {
  return (
    <footer className="md:ml-64 border-t py-6 text-center text-xs text-muted-foreground">
      <p>
        &copy; {new Date().getFullYear()} {APP.NAME} &middot; Made with care for
        hungry teams
      </p>
    </footer>
  );
}
