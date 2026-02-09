import type { ReactNode } from "react";

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

export interface WithChildren {
  children: ReactNode;
}

export interface WithClassName {
  className?: string;
}

export type AsyncStatus = "idle" | "loading" | "succeeded" | "failed";

export interface SelectOption {
  label: string;
  value: string;
}
