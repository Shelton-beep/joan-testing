"use client";

import * as React from "react";

type AccordionProps = {
  type?: "single" | "multiple";
  collapsible?: boolean;
  defaultValue?: string;
  className?: string;
  children: React.ReactNode;
};

export function Accordion({
  className = "",
  children,
}: AccordionProps) {
  return <div className={`space-y-2 ${className}`}>{children}</div>;
}

type AccordionItemProps = {
  value?: string;
  className?: string;
  children: React.ReactNode;
};

export function AccordionItem({
  className = "",
  children,
}: AccordionItemProps) {
  // Simple wrapper – state is handled by <details>
  return <div className={className}>{children}</div>;
}

type TriggerProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  children: React.ReactNode;
};

export function AccordionTrigger({ className = "", children, ...props }: TriggerProps) {
  return (
    <button
      type="button"
      className={`flex w-full items-center justify-between gap-2 border-b border-slate-800 bg-slate-900/80 px-3 py-2 text-left text-sm font-medium text-slate-200 hover:bg-slate-800/80 ${className}`}
      {...props}
    >
      <span>{children}</span>
      <span className="text-xs text-slate-400">▼</span>
    </button>
  );
}

type ContentProps = {
  className?: string;
  children: React.ReactNode;
};

export function AccordionContent({ className = "", children }: ContentProps) {
  return <div className={`pt-3 ${className}`}>{children}</div>;
}


