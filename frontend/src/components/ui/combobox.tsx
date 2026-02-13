import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/utils";
import { Check, ChevronsUpDown, Plus } from "lucide-react";
import { useEffect, useRef, useState } from "react";

export interface ComboboxOption {
  value: string;
  label: string;
}

interface ComboboxProps {
  options: ComboboxOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  emptyText?: string;
  allowCreate?: boolean;
  onCreateNew?: (name: string) => void;
  createLabel?: string;
  className?: string;
  disabled?: boolean;
}

export function Combobox({
  options,
  value,
  onChange,
  placeholder = "Select...",
  searchPlaceholder = "Search...",
  emptyText = "No results found.",
  allowCreate = false,
  onCreateNew,
  createLabel = "Create",
  className,
  disabled = false,
}: ComboboxProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const selectedLabel = options.find((o) => o.value === value)?.label;

  const filtered = options.filter((o) =>
    o.label.toLowerCase().includes(search.toLowerCase()),
  );

  const showCreate =
    allowCreate &&
    search.trim() !== "" &&
    !options.some((o) => o.label.toLowerCase() === search.trim().toLowerCase());

  useEffect(() => {
    if (open) {
      // Focus the input after popover opens
      setTimeout(() => inputRef.current?.focus(), 0);
    } else {
      setSearch("");
    }
  }, [open]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn(
            "w-full justify-between font-normal",
            !value && "text-muted-foreground",
            className,
          )}
        >
          <span className="truncate">{selectedLabel ?? placeholder}</span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0">
        {/* Search input */}
        <div className="flex items-center border-b px-3">
          <input
            ref={inputRef}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={searchPlaceholder}
            className="flex h-9 w-full bg-transparent py-2 text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>

        {/* Options list */}
        <div className="max-h-60 overflow-y-auto p-1">
          {/* "None" / clear option */}
          <button
            type="button"
            className={cn(
              "relative flex w-full cursor-pointer select-none items-center rounded-md px-2 py-1.5 text-sm outline-none transition-colors duration-150 hover:bg-accent hover:text-accent-foreground",
              !value && "bg-accent text-accent-foreground",
            )}
            onClick={() => {
              onChange("");
              setOpen(false);
            }}
          >
            <Check
              className={cn(
                "mr-2 h-4 w-4",
                !value ? "opacity-100" : "opacity-0",
              )}
            />
            <span className="text-muted-foreground italic">{placeholder}</span>
          </button>

          {filtered.map((option) => (
            <button
              key={option.value}
              type="button"
              className={cn(
              "relative flex w-full cursor-pointer select-none items-center rounded-md px-2 py-1.5 text-sm outline-none transition-colors duration-150 hover:bg-accent hover:text-accent-foreground",
              value === option.value && "bg-accent text-accent-foreground",
              )}
              onClick={() => {
                onChange(option.value);
                setOpen(false);
              }}
            >
              <Check
                className={cn(
                  "mr-2 h-4 w-4",
                  value === option.value ? "opacity-100" : "opacity-0",
                )}
              />
              {option.label}
            </button>
          ))}

          {filtered.length === 0 && !showCreate && (
            <div className="py-6 text-center text-sm text-muted-foreground">
              {emptyText}
            </div>
          )}

          {/* Create new option */}
          {showCreate && (
            <button
              type="button"
              className="relative flex w-full cursor-pointer select-none items-center rounded-md px-2 py-1.5 text-sm outline-none transition-colors duration-150 hover:bg-accent hover:text-accent-foreground text-primary font-medium"
              onClick={() => {
                if (onCreateNew) {
                  onCreateNew(search.trim());
                }
                setOpen(false);
                setSearch("");
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              {createLabel} &ldquo;{search.trim()}&rdquo;
            </button>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
