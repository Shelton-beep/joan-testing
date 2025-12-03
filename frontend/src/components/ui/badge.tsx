import * as React from "react";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "outline";
};

export function Badge({
  className = "",
  variant = "default",
  ...props
}: BadgeProps) {
  const base =
    "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium";
  const styles =
    variant === "outline"
      ? "border-zinc-300 text-zinc-700 dark:border-zinc-700 dark:text-zinc-200"
      : "border-transparent bg-emerald-500/10 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300";

  return <span className={`${base} ${styles} ${className}`} {...props} />;
}


