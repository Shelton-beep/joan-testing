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

export function AnomaliesByTypeChart() {
  const { data: events, isLoading } = useEvents();
  const filters = useFilters();

  const data = useMemo(() => {
    if (!events) return [];

    const counts = new Map<string, number>();

    for (const e of events as any[]) {
      if (!e.is_anomaly) continue;

      const ts = new Date(e.timestamp);
      if (filters.startDate && ts < new Date(filters.startDate)) continue;
      if (filters.endDate) {
        const end = new Date(filters.endDate);
        end.setHours(23, 59, 59, 999);
        if (ts > end) continue;
      }

      if (filters.userId !== "All" && e.user_id !== filters.userId) continue;
      if (filters.location !== "All" && e.location !== filters.location)
        continue;
      if (filters.eventLabel !== "All" && e.event_label !== filters.eventLabel)
        continue;

      const key = e.event_label;
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }

    return Array.from(counts.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  }, [events, filters]);

  return (
    <Card className="h-[280px] border-slate-800 bg-slate-900/70 md:h-[320px]">
      <CardHeader>
        <CardTitle className="text-sm text-slate-200">
          Anomalies by type
        </CardTitle>
      </CardHeader>
      <CardContent className="h-[200px] md:h-[230px]">
        {isLoading ? (
          <div className="h-full w-full animate-pulse rounded-lg bg-slate-800/60" />
        ) : (
          <ResponsiveContainer>
            <BarChart
              data={data}
              layout="vertical"
              margin={{ left: 40, right: 20, top: 10, bottom: 10 }}
            >
              <XAxis
                type="number"
                tick={{ fill: "#64748b", fontSize: 11 }}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: "#cbd5f5", fontSize: 11 }}
                width={120}
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
              <Bar dataKey="value" fill="#fb7185" radius={[4, 4, 4, 4]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}


