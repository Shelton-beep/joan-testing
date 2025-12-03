"use client";

import { useMemo } from "react";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";

export function RealtimeIndicator() {
  const { data: events } = useEvents();
  const realtime = useFilters((s) => s.realtime);

  const status = useMemo(() => {
    if (!realtime || !events || events.length === 0) {
      return { label: "Realtime off", tone: "idle", ageText: "" };
    }

    const timestamps = (events as any[])
      .map((e) => new Date(e.timestamp))
      .filter((d) => !Number.isNaN(d.getTime()))
      .sort((a, b) => b.getTime() - a.getTime());

    if (timestamps.length === 0) {
      return { label: "No events", tone: "error", ageText: "" };
    }

    const latest = timestamps[0];
    const ageSeconds = (Date.now() - latest.getTime()) / 1000;

    if (ageSeconds < 15) {
      return {
        label: "Live",
        tone: "ok",
        ageText: `${Math.round(ageSeconds)}s ago`,
      };
    }
    if (ageSeconds < 60) {
      return {
        label: "Recent",
        tone: "warn",
        ageText: `${Math.round(ageSeconds)}s ago`,
      };
    }
    return {
      label: "Stale",
      tone: "error",
      ageText: `${Math.round(ageSeconds / 60)}m ago`,
    };
  }, [events, realtime]);

  if (!realtime) {
    return (
      <div className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/70 px-3 py-1 text-[11px] text-slate-300">
        <span className="h-2 w-2 rounded-full bg-slate-500" />
        Manual refresh
      </div>
    );
  }

  const toneClasses =
    status.tone === "ok"
      ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-200"
      : status.tone === "warn"
      ? "border-amber-500/60 bg-amber-500/10 text-amber-200"
      : "border-rose-500/60 bg-rose-500/10 text-rose-200";

  const dotClass =
    status.tone === "ok"
      ? "bg-emerald-400"
      : status.tone === "warn"
      ? "bg-amber-400"
      : "bg-rose-400";

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] ${toneClasses}`}
    >
      <span className={`h-2 w-2 rounded-full ${dotClass}`} />
      <span>{status.label}</span>
      {status.ageText && (
        <span className="text-slate-300/80">({status.ageText})</span>
      )}
    </div>
  );
}


