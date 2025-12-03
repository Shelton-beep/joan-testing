"use client";

import { useEffect, useMemo } from "react";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";
import { Badge } from "@/components/ui/badge";

export function FiltersPanel() {
  const { data: events } = useEvents();
  const filters = useFilters();

  const distinctUsers = useMemo(() => {
    if (!events) return [];
    return Array.from(new Set(events.map((e: any) => e.user_id))).sort();
  }, [events]);

  const distinctLocations = useMemo(() => {
    if (!events) return [];
    return Array.from(new Set(events.map((e: any) => e.location))).sort();
  }, [events]);

  const distinctLabels = useMemo(() => {
    if (!events) return [];
    return Array.from(new Set(events.map((e: any) => e.event_label))).sort();
  }, [events]);

  // Initialise date range from events on first load
  useEffect(() => {
    if (!events || events.length === 0) return;
    if (filters.startDate && filters.endDate) return;

    const times = events
      .map((e: any) => new Date(e.timestamp))
      .filter((d: Date) => !Number.isNaN(d.getTime()))
      .sort((a: Date, b: Date) => a.getTime() - b.getTime());

    if (times.length === 0) return;
    const first = times[0];
    const last = times[times.length - 1];
    const toInput = (d: Date) => d.toISOString().slice(0, 10);
    filters.setStartDate(toInput(first));
    filters.setEndDate(toInput(last));
  }, [events, filters]);

  return (
    <section className="grid gap-4 rounded-xl border border-slate-800/60 bg-slate-950/60 p-4 md:grid-cols-3 lg:grid-cols-4">
      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">User</p>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.userId}
          onChange={(e) => filters.setUserId(e.target.value)}
        >
          <option value="All">All</option>
          {distinctUsers.map((u) => (
            <option key={u} value={u}>
              {u}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">Location</p>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.location}
          onChange={(e) => filters.setLocation(e.target.value)}
        >
          <option value="All">All</option>
          {distinctLocations.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">Anomaly label</p>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.eventLabel}
          onChange={(e) => filters.setEventLabel(e.target.value)}
        >
          <option value="All">All</option>
          {distinctLabels.map((lab) => (
            <option key={lab} value={lab}>
              {lab}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">Login result</p>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.status}
          onChange={(e) =>
            filters.setStatus(e.target.value as "all" | "success" | "fail")
          }
        >
          <option value="all">All</option>
          <option value="success">Success only</option>
          <option value="fail">Failed only</option>
        </select>
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">Anomaly status</p>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.anomalyStatus}
          onChange={(e) =>
            filters.setAnomalyStatus(
              e.target.value as "all" | "normal" | "anomaly",
            )
          }
        >
          <option value="all">All</option>
          <option value="normal">Normal only</option>
          <option value="anomaly">Anomalies only</option>
        </select>
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">From date</p>
        <input
          type="date"
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.startDate}
          onChange={(e) => filters.setStartDate(e.target.value)}
        />
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">To date</p>
        <input
          type="date"
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-2 py-1.5 text-xs text-slate-100"
          value={filters.endDate}
          onChange={(e) => filters.setEndDate(e.target.value)}
        />
      </div>

      <div className="space-y-1">
        <p className="text-xs font-medium text-slate-300">Real-time mode</p>
        <button
          type="button"
          onClick={filters.toggleRealtime}
          className={`inline-flex w-full items-center justify-between rounded-md border px-3 py-1.5 text-xs ${
            filters.realtime
              ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-200"
              : "border-slate-700 bg-slate-950 text-slate-200"
          }`}
        >
          <span>{filters.realtime ? "Streaming" : "Manual"}</span>
          <Badge variant={filters.realtime ? "default" : "outline"}>
            {filters.realtime ? "On" : "Off"}
          </Badge>
        </button>
      </div>
    </section>
  );
}


