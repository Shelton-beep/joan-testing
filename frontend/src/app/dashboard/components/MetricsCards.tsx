"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEvents } from "@/hooks/useEvents";
import { useFilters } from "@/hooks/useFilters";
import { ArrowDownRight, ArrowUpRight, Activity, Timer } from "lucide-react";

export function MetricsCards() {
  const { data: events, isLoading, isError } = useEvents();
  const filters = useFilters();

  const { total, anomalies, rate, avgMttd } = useMemo(() => {
    if (!events) {
      return { total: 0, anomalies: 0, rate: 0, avgMttd: 0 };
    }

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

    const total = filtered.length;
    const anomalies = filtered.filter((e) => e.is_anomaly).length;
    const rate = total ? (anomalies / total) * 100 : 0;

    const anomalyTimes = filtered
      .filter((e) => e.is_anomaly)
      .map((e) => new Date(e.timestamp))
      .sort((a, b) => a.getTime() - b.getTime());

    let avgMttd = 0;
    if (anomalyTimes.length > 1) {
      const diffs: number[] = [];
      for (let i = 1; i < anomalyTimes.length; i++) {
        diffs.push(
          (anomalyTimes[i].getTime() - anomalyTimes[i - 1].getTime()) /
            (1000 * 60),
        );
      }
      avgMttd =
        diffs.reduce((acc, v) => acc + v, 0) / Math.max(diffs.length, 1);
    }

    return { total, anomalies, rate, avgMttd };
  }, [events, filters]);

  const cards = [
    {
      label: "Total events",
      value: total.toLocaleString(),
      icon: Activity,
      accent: "from-sky-500/30 to-sky-500/5",
    },
    {
      label: "Anomalies detected",
      value: anomalies.toLocaleString(),
      icon: ArrowUpRight,
      accent: "from-rose-500/30 to-rose-500/5",
    },
    {
      label: "Anomaly rate",
      value: `${rate.toFixed(2)}%`,
      icon: ArrowDownRight,
      accent: "from-amber-500/30 to-amber-500/5",
    },
    {
      label: "Avg. MTTD",
      value: `${avgMttd.toFixed(1)} min`,
      icon: Timer,
      accent: "from-emerald-500/30 to-emerald-500/5",
    },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map(({ label, value, icon: Icon, accent }) => (
        <Card
          key={label}
          className="relative overflow-hidden border-slate-800 bg-slate-900/70"
        >
          <div
            className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${accent} opacity-60`}
          />
          <CardHeader className="relative z-10 flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium text-slate-300">
              {label}
            </CardTitle>
            <Icon className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent className="relative z-10">
            {isLoading || isError ? (
              <div className="h-6 w-24 animate-pulse rounded-md bg-slate-800" />
            ) : (
              <div className="text-2xl font-semibold text-slate-50">
                {value}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </section>
  );
}


