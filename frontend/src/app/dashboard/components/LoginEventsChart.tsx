"use client";

import { useMemo } from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";

export function LoginEventsChart() {
  const { data: events, isLoading } = useEvents();
  const filters = useFilters();

  const data = useMemo(() => {
    if (!events) return [];

    const filtered = (events as any[]).filter((e) => {
      const ts = new Date(e.timestamp);
      if (Number.isNaN(ts.getTime())) return false;
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

    const bucket = new Map<
      string,
      { date: string; total: number; anomalies: number }
    >();

    for (const e of filtered) {
      const ts = new Date(e.timestamp);
      const dateKey = ts.toISOString().slice(0, 10); // YYYY-MM-DD
      const existing = bucket.get(dateKey) ?? {
        date: dateKey,
        total: 0,
        anomalies: 0,
      };
      existing.total += 1;
      if (e.is_anomaly) existing.anomalies += 1;
      bucket.set(dateKey, existing);
    }

    return Array.from(bucket.values()).sort((a, b) =>
      a.date.localeCompare(b.date),
    );
  }, [events, filters]);

  return (
    <Card className="h-[280px] border-slate-800 bg-slate-900/70 md:h-[320px]">
      <CardHeader>
        <CardTitle className="text-sm text-slate-200">
          Login events over time
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[200px] md:h-[230px]">
        {isLoading ? (
          <div className="h-full w-full animate-pulse rounded-lg bg-slate-800/60" />
        ) : (
          <ResponsiveContainer>
            <AreaChart
              data={data}
              margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="totalFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.7} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="anomalyFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#fb7185" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#fb7185" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#64748b", fontSize: 11 }}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#64748b", fontSize: 11 }}
                allowDecimals={false}
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
              <Legend />
              <Area
                type="monotone"
                dataKey="total"
                stroke="#0ea5e9"
                strokeWidth={2}
                fill="url(#totalFill)"
                name="Total events"
              />
              <Area
                type="monotone"
                dataKey="anomalies"
                stroke="#fb7185"
                strokeWidth={2}
                fill="url(#anomalyFill)"
                name="Anomalies"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}


