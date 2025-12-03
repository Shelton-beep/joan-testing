"use client";

import { useState } from "react";
import Link from "next/link";
import { Shield, LogIn, ArrowLeft, LogOut } from "lucide-react";
import { Card } from "@/components/ui/card";

type PredictResponse = {
  user_id?: string;
  device_id?: string;
  location?: string;
  prediction: "normal" | "anomaly";
};

export default function UserLoginPage() {
  const [userId, setUserId] = useState("user_101");
  const [deviceId, setDeviceId] = useState("device_22");
  const [ipAddress, setIpAddress] = useState("192.168.10.5");
  const [location, setLocation] = useState("New York, USA");
  const [resource, setResource] = useState("sales");
  const [loginSuccess, setLoginSuccess] = useState<1 | 0>(1);
  const [bytesTransferred, setBytesTransferred] = useState(500_000);
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    setResult(null);

    try {
      const host =
        typeof window !== "undefined" ? window.location.hostname : "localhost";
      const backendBase =
        process.env.NEXT_PUBLIC_BACKEND_URL || `http://${host}:8000`;

      const payload = {
        user_id: userId,
        device_id: deviceId,
        ip_address: ipAddress,
        location,
        login_success: loginSuccess,
        access_time: new Date().toTimeString().slice(0, 8),
        resource_accessed: resource,
        bytes_transferred: bytesTransferred,
      };

      const res = await fetch(`${backendBase}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Backend responded with ${res.status}`);
      }

      const data = (await res.json()) as PredictResponse;
      setResult(data);

      if (data.prediction === "anomaly") {
        setMessage(
          "This login has been flagged as an anomaly by the Zero-Trust engine. An alert email may have been sent to the SOC inbox."
        );
      } else {
        setMessage(
          "This login appears consistent with expected behaviour according to the current model."
        );
      }
    } catch (err) {
      console.error(err);
      setMessage(
        "Login request failed. Check that the backend API is running and reachable."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50">
      <div className="mx-auto flex min-h-screen max-w-md flex-col px-4 py-10">
        <header className="mb-8 flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
          >
            <ArrowLeft className="h-3 w-3" />
            Back
          </Link>
          <button
            type="button"
            className="inline-flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-[11px] font-medium text-slate-100 hover:border-slate-500 hover:bg-slate-800"
            onClick={() => {
              window.location.href = "/";
            }}
          >
            <LogOut className="h-3 w-3" />
            Logout
          </button>
        </header>

        <main className="flex flex-1 flex-col items-center justify-center">
          <Card className="w-full border-slate-800 bg-slate-900/80 p-6 shadow-xl shadow-emerald-500/10">
            <h1 className="mb-2 text-lg font-semibold tracking-tight">
              Sign in to continue
            </h1>
            <p className="mb-6 text-xs text-slate-400">
              This is the user-facing entry point. In production, this form
              calls your Python backend&apos;s <code>/predict</code> endpoint so
              each login attempt can be scored for anomalies.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <label
                  htmlFor="user_id"
                  className="block text-xs font-medium text-slate-200"
                >
                  User ID
                </label>
                <input
                  id="user_id"
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                />
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="device_id"
                  className="block text-xs font-medium text-slate-200"
                >
                  Device ID
                </label>
                <input
                  id="device_id"
                  type="text"
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                />
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="ip_address"
                  className="block text-xs font-medium text-slate-200"
                >
                  IP address
                </label>
                <input
                  id="ip_address"
                  type="text"
                  value={ipAddress}
                  onChange={(e) => setIpAddress(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                />
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="location"
                  className="block text-xs font-medium text-slate-200"
                >
                  Location
                </label>
                <input
                  id="location"
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                />
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="resource"
                  className="block text-xs font-medium text-slate-200"
                >
                  Resource accessed
                </label>
                <select
                  id="resource"
                  value={resource}
                  onChange={(e) => setResource(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                >
                  <option value="sales">sales</option>
                  <option value="finance">finance</option>
                  <option value="hr">hr</option>
                  <option value="prod">prod</option>
                </select>
              </div>

              <div className="space-y-1">
                <span className="block text-xs font-medium text-slate-200">
                  Login result
                </span>
                <div className="flex gap-3 text-xs">
                  <label className="inline-flex items-center gap-1 text-slate-200">
                    <input
                      type="radio"
                      name="login_success"
                      value="1"
                      checked={loginSuccess === 1}
                      onChange={() => setLoginSuccess(1)}
                    />
                    Success
                  </label>
                  <label className="inline-flex items-center gap-1 text-slate-200">
                    <input
                      type="radio"
                      name="login_success"
                      value="0"
                      checked={loginSuccess === 0}
                      onChange={() => setLoginSuccess(0)}
                    />
                    Failed
                  </label>
                </div>
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="bytes"
                  className="block text-xs font-medium text-slate-200"
                >
                  Bytes transferred
                </label>
                <input
                  id="bytes"
                  type="number"
                  value={bytesTransferred}
                  onChange={(e) => setBytesTransferred(Number(e.target.value))}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                  min={0}
                />
                <p className="text-[10px] text-slate-500">
                  Large values may be treated as potential data exfiltration by
                  the backend model.
                </p>
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="password"
                  className="block text-xs font-medium text-slate-200"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-500/40 focus:border-emerald-500 focus:ring-1"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-emerald-500 px-3 py-2 text-sm font-medium text-slate-950 transition hover:bg-emerald-400 disabled:opacity-60"
              >
                <LogIn className="h-4 w-4" />
                {submitting ? "Signing in..." : "Sign in"}
              </button>
            </form>

            {message && (
              <p className="mt-4 text-xs text-emerald-300">{message}</p>
            )}

            {result && (
              <div className="mt-4 rounded-md border border-slate-700 bg-slate-950/80 p-3 text-xs text-slate-200">
                <p className="mb-1 font-medium">
                  Model decision:{" "}
                  <span
                    className={
                      result.prediction === "anomaly"
                        ? "text-rose-300"
                        : "text-emerald-300"
                    }
                  >
                    {result.prediction.toUpperCase()}
                  </span>
                </p>
                <p className="text-slate-400">
                  This reflects the isolation-forest based Zero-Trust policy
                  running in your Python backend. For deeper explanation (SHAP),
                  use the admin dashboard or notebooks.
                </p>
              </div>
            )}
          </Card>
        </main>
      </div>
    </div>
  );
}
