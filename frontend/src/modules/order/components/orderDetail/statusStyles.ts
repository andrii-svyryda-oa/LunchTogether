export const STATUS_STYLES: Record<
  string,
  { bg: string; text: string; dot: string }
> = {
  initiated: { bg: "bg-blue-50", text: "text-blue-700", dot: "bg-blue-500" },
  confirmed: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    dot: "bg-amber-500",
  },
  ordered: {
    bg: "bg-purple-50",
    text: "text-purple-700",
    dot: "bg-purple-500",
  },
  finished: {
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    dot: "bg-emerald-500",
  },
  cancelled: { bg: "bg-red-50", text: "text-red-700", dot: "bg-red-500" },
};
