"use client";

import { Suspense } from "react";
import Link from "next/link";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MetricsCards } from "./components/MetricsCards";
import { FiltersPanel } from "./components/FiltersPanel";
import { LoginEventsChart } from "./components/LoginEventsChart";
import { AnomaliesByTypeChart } from "./components/AnomaliesByTypeChart";
import { LocationStatsChart } from "./components/LocationStatsChart";
import { EventTable } from "./components/EventTable";
import { ShapExplainability } from "./components/ShapExplainability";
import { RealtimeIndicator } from "./components/RealtimeIndicator";

const queryClient = new QueryClient();

export default function DashboardPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <Suspense
        fallback={
          <div className="p-6 text-sm text-slate-300">Loading dashboard...</div>
        }
      >
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50">
          <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 lg:px-8 lg:py-10">
            <header className="mb-6 flex flex-col gap-3 md:mb-8 md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
                  Zero-Trust Anomaly Detection
                </h1>
                <p className="mt-1 max-w-xl text-xs text-slate-400 md:text-sm">
                  SOC dashboard for monitoring authentication behaviour,
                  anomalies, and model signals.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <RealtimeIndicator />
                <Link
                  href="/"
                  className="inline-flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-[11px] font-medium text-slate-100 hover:border-slate-500 hover:bg-slate-800"
                >
                  Logout
                </Link>
              </div>
            </header>

            <main className="flex flex-1 flex-col gap-6 pb-10">
              <FiltersPanel />
              <MetricsCards />

              <section className="grid gap-6 lg:grid-cols-[1.5fr,1fr]">
                <LoginEventsChart />
                <AnomaliesByTypeChart />
              </section>

              <section className="grid gap-6 lg:grid-cols-[1.2fr,1fr]">
                <LocationStatsChart />
                <ShapExplainability />
              </section>

              <EventTable />
            </main>
          </div>
        </div>
      </Suspense>
    </QueryClientProvider>
  );
}
