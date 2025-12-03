"use client";

import Link from "next/link";
import { ArrowRight, Shield, Activity, LineChart } from "lucide-react";
import { Card } from "@/components/ui/card";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-linear-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-10 lg:px-8 lg:py-16">
        <main className="flex flex-1 flex-col items-center justify-center gap-10 text-center md:gap-12">
          <div className="space-y-5 md:space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-200">
              <Shield className="h-3.5 w-3.5" />
              Zero-Trust Anomaly Detection
            </div>
            <h1 className="text-3xl font-semibold tracking-tight md:text-5xl">
              Real‑time security analytics for your authentication logs.
            </h1>
            <p className="mx-auto max-w-xl text-sm text-slate-400 md:text-base">
              This frontend connects to your Python Zero‑Trust engine to surface
              impossible travel, off‑hours logins, data exfiltration and more —
              with explainable, SOC‑friendly visuals.
            </p>
          </div>

          <div className="flex flex-col items-center gap-4 md:flex-row md:gap-6">
            <Link
              href="/user"
              className="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-2.5 text-sm font-medium text-slate-100 ring-1 ring-slate-700 transition hover:bg-slate-800"
            >
              User login
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-full bg-emerald-500 px-6 py-2.5 text-sm font-medium text-slate-950 transition hover:bg-emerald-400"
            >
              Admin dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>

          <section className="grid w-full max-w-3xl gap-4 md:grid-cols-3">
            <Card className="border-slate-800 bg-slate-900/70 p-4 text-left">
              <div className="mb-3 flex items-center gap-2 text-emerald-300">
                <Activity className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">
                  Live Events
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Stream login events from your Python backend and flag anomalies
                in real time using your Isolation Forest model.
              </p>
            </Card>

            <Card className="border-slate-800 bg-slate-900/70 p-4 text-left">
              <div className="mb-3 flex items-center gap-2 text-sky-300">
                <LineChart className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">
                  Rich Analytics
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Visualise trends by time, location and anomaly type, mirroring
                the capabilities of your existing Streamlit dashboard.
              </p>
            </Card>

            <Card className="border-slate-800 bg-slate-900/70 p-4 text-left">
              <div className="mb-3 flex items-center gap-2 text-amber-300">
                <Shield className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-wide">
                  Explainable ML
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Integrate SHAP outputs from the backend to understand why the
                model flagged a session as anomalous.
              </p>
            </Card>
          </section>
        </main>
      </div>
    </div>
  );
}
