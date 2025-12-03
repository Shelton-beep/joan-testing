"use client";

import { useMemo, useState } from "react";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { exportCsv } from "@/lib/utils";

type SortKey =
  | "timestamp"
  | "user_id"
  | "location"
  | "bytes_transferred"
  | "event_label";

export function EventTable() {
  const { data: events, isLoading } = useEvents();
  const filters = useFilters();
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const pageSize = 20;

  const filtered = useMemo(() => {
    if (!events) return [];
    return (events as any[]).filter((e) => {
      const ts = new Date(e.timestamp);
      if (filters.startDate && ts < new Date(filters.startDate)) return false;
      if (filters.endDate) {
        const end = new Date(filters.endDate);
        end.setHours(23, 59, 59, 999);
        if (ts > end) return false;
      }
      if (filters.userId !== "All" && e.user_id !== filters.userId) return false;
      if (filters.location !== "All" && e.location !== filters.location)
        return false;
      if (filters.eventLabel !== "All" && e.event_label !== filters.eventLabel)
        return false;
      if (filters.status === "success" && e.login_success !== 1) return false;
      if (filters.status === "fail" && e.login_success !== 0) return false;
      if (filters.anomalyStatus === "normal" && e.is_anomaly) return false;
      if (filters.anomalyStatus === "anomaly" && !e.is_anomaly) return false;
      return true;
    });
  }, [events, filters]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      let av = a[sortKey];
      let bv = b[sortKey];
      if (sortKey === "timestamp") {
        av = new Date(a.timestamp).getTime();
        bv = new Date(b.timestamp).getTime();
      }
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const current = sorted.slice(page * pageSize, (page + 1) * pageSize);

  const changeSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const onExport = () => {
    exportCsv("anomaly_events.csv", sorted);
  };

  return (
    <Card className="border-slate-800 bg-slate-900/70">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="text-sm text-slate-200">
            Event details
          </CardTitle>
          <p className="mt-1 text-xs text-slate-500">
            Filtered authentication events with zero-trust labels.
          </p>
        </div>
        <button
          type="button"
          onClick={onExport}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100 hover:border-slate-500 hover:bg-slate-800"
        >
          Export CSV
        </button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="h-52 w-full animate-pulse rounded-lg bg-slate-800/60" />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-xs md:text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
                    <th
                      className="cursor-pointer px-3 py-2 font-medium"
                      onClick={() => changeSort("timestamp")}
                    >
                      Time
                    </th>
                    <th
                      className="cursor-pointer px-3 py-2 font-medium"
                      onClick={() => changeSort("user_id")}
                    >
                      User
                    </th>
                    <th className="px-3 py-2 font-medium">Device</th>
                    <th className="px-3 py-2 font-medium">IP</th>
                    <th
                      className="cursor-pointer px-3 py-2 font-medium"
                      onClick={() => changeSort("location")}
                    >
                      Location
                    </th>
                    <th className="px-3 py-2 font-medium">Login</th>
                    <th
                      className="cursor-pointer px-3 py-2 font-medium"
                      onClick={() => changeSort("event_label")}
                    >
                      Label
                    </th>
                    <th
                      className="cursor-pointer px-3 py-2 font-medium"
                      onClick={() => changeSort("bytes_transferred")}
                    >
                      Bytes
                    </th>
                    <th className="px-3 py-2 font-medium">is_anomaly</th>
                    <th className="px-3 py-2 font-medium">Model</th>
                  </tr>
                </thead>
              <tbody>
              {current.map((e: any, idx: number) => (
                    <tr
                  key={`${e.timestamp ?? "NaT"}-${e.user_id ?? "unknown"}-${e.device_id ?? "device"}-${e.resource_accessed ?? "resource"}-${idx}`}
                      className={`border-b border-slate-900/60 ${
                        e.is_anomaly ? "bg-rose-500/5" : "bg-transparent"
                      }`}
                    >
                      <td className="px-3 py-2 text-slate-200">
                    {(() => {
                      const d = new Date(e.timestamp);
                      return Number.isNaN(d.getTime())
                        ? "-"
                        : d.toLocaleString();
                    })()}
                      </td>
                      <td className="px-3 py-2 text-slate-200">{e.user_id}</td>
                      <td className="px-3 py-2 text-slate-400">
                        {e.device_id ?? "-"}
                      </td>
                      <td className="px-3 py-2 text-slate-400">
                        {e.ip_address ?? "-"}
                      </td>
                      <td className="px-3 py-2 text-slate-300">
                        {e.location}
                      </td>
                      <td className="px-3 py-2">
                        <Badge
                          variant={e.login_success === 1 ? "default" : "outline"}
                        >
                          {e.login_success === 1 ? "Success" : "Failed"}
                        </Badge>
                      </td>
                      <td className="px-3 py-2">
                        <span className="inline-flex max-w-[180px] items-center truncate rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-100">
                          {e.event_label}
                        </span>
                      </td>
                      <td className="px-3 py-2 tabular-nums text-slate-200">
                        {e.bytes_transferred?.toLocaleString?.() ??
                          String(e.bytes_transferred)}
                      </td>
                      <td className="px-3 py-2">
                        <Badge
                          variant={e.is_anomaly ? "default" : "outline"}
                          className={
                            e.is_anomaly ? "bg-rose-500/20 text-rose-100" : ""
                          }
                        >
                          {e.is_anomaly ? "Anomaly" : "Normal"}
                        </Badge>
                      </td>
                      <td className="px-3 py-2">
                        <Badge
                          variant={
                            e.model_prediction === "anomaly"
                              ? "default"
                              : "outline"
                          }
                          className={
                            e.model_prediction === "anomaly"
                              ? "bg-amber-500/20 text-amber-100"
                              : ""
                          }
                        >
                          {e.model_prediction ?? "-"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
              <span>
                Showing{" "}
                <span className="font-semibold text-slate-200">
                  {current.length}
                </span>{" "}
                of{" "}
                <span className="font-semibold text-slate-200">
                  {sorted.length}
                </span>{" "}
                events
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={page === 0}
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  className="rounded-md border border-slate-700 px-2 py-0.5 text-xs disabled:opacity-40"
                >
                  Prev
                </button>
                <span>
                  Page {page + 1} / {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page + 1 >= totalPages}
                  onClick={() =>
                    setPage((p) => Math.min(totalPages - 1, p + 1))
                  }
                  className="rounded-md border border-slate-700 px-2 py-0.5 text-xs disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}


