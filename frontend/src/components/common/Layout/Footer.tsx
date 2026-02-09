import { APP } from "@/constants";

export function Footer() {
  return (
    <footer className="border-t py-4 text-center text-sm text-muted-foreground">
      <p>
        &copy; {new Date().getFullYear()} {APP.NAME}. All rights reserved.
      </p>
    </footer>
  );
}
