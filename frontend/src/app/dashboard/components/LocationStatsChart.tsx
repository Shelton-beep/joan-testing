"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";

export function LocationStatsChart() {
  const { data: events, isLoading } = useEvents();
  const filters = useFilters();

  const data = useMemo(() => {
    if (!events) return [];

    type Agg = { location: string; total: number; anomalies: number };
    const map = new Map<string, Agg>();

    const filtered = (events as any[]).filter((e) => {
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

    for (const e of filtered) {
      const loc = e.location ?? "Unknown";
      const current = map.get(loc) ?? { location: loc, total: 0, anomalies: 0 };
      current.total += 1;
      if (e.is_anomaly) current.anomalies += 1;
      map.set(loc, current);
    }

    const rows = Array.from(map.values()).map((r) => ({
      ...r,
      anomalyRate: r.total ? (r.anomalies / r.total) * 100 : 0,
    }));

    return rows.sort((a, b) => b.anomalies - a.anomalies).slice(0, 8);
  }, [events, filters]);

  return (
    <Card className="border-slate-800 bg-slate-900/70">
      <CardHeader>
        <CardTitle className="text-sm text-slate-200">
          Location analytics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="h-40 w-full animate-pulse rounded-lg bg-slate-800/60" />
        ) : (
          <div className="h-40">
            <ResponsiveContainer>
              <BarChart
                data={data}
                margin={{ top: 10, right: 20, left: -10, bottom: 10 }}
              >
                <XAxis
                  dataKey="location"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#64748b", fontSize: 10 }}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#64748b", fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#020617",
                    border: "1px solid #1e293b",
                    borderRadius: 8,
                    padding: "8px 10px",
                    fontSize: 12,
                  }}
                />
                <Bar
                  dataKey="total"
                  stackId="a"
                  fill="#0ea5e9"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="anomalies"
                  stackId="a"
                  fill="#fb7185"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="max-h-40 overflow-y-auto rounded-md border border-slate-800/70 bg-slate-950/60">
          <table className="min-w-full text-left text-[11px] text-slate-300">
            <thead className="border-b border-slate-800/70 bg-slate-950/80">
              <tr>
                <th className="px-2 py-1 font-medium">Location</th>
                <th className="px-2 py-1 font-medium">Total</th>
                <th className="px-2 py-1 font-medium">Anomalies</th>
                <th className="px-2 py-1 font-medium">Rate</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.location} className="border-b border-slate-900/60">
                  <td className="px-2 py-1">{row.location}</td>
                  <td className="px-2 py-1 tabular-nums">{row.total}</td>
                  <td className="px-2 py-1 tabular-nums">{row.anomalies}</td>
                  <td className="px-2 py-1 tabular-nums">
                    {row.anomalyRate.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}


