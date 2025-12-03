"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useShap } from "@/hooks/useShap";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export function ShapExplainability() {
  const { data, isLoading, isError } = useShap();

  const isImage = data && "image" in data;
  const isVector = data && "features" in data && "importance" in data;

  return (
    <Card className="border-slate-800 bg-slate-900/70">
      <CardHeader>
        <CardTitle className="text-sm text-slate-200">
          Model explainability (SHAP)
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-40 w-full animate-pulse rounded-lg bg-slate-800/60" />
        ) : isError || !data ? (
          <p className="text-xs text-slate-400">
            SHAP endpoint not available on this backend. Use the Python
            notebooks or Streamlit dashboard for deeper model insights.
          </p>
        ) : isImage ? (
          <img
            src={`data:image/png;base64,${(data as any).image}`}
            alt="SHAP summary plot"
            className="max-h-72 w-full rounded-md border border-slate-800 object-contain"
          />
        ) : isVector ? (
          <div className="h-56">
            <ResponsiveContainer>
              <BarChart
                data={(data as any).features.map(
                  (f: string, i: number) => ({
                    feature: f,
                    importance: (data as any).importance[i],
                  }),
                )}
                layout="vertical"
                margin={{ left: 60, right: 20, top: 10, bottom: 10 }}
              >
                <XAxis
                  type="number"
                  tick={{ fill: "#64748b", fontSize: 11 }}
                />
                <YAxis
                  dataKey="feature"
                  type="category"
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
                <Bar
                  dataKey="importance"
                  fill="#22c55e"
                  radius={[4, 4, 4, 4]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="text-xs text-slate-400">
            SHAP data format not recognised. Please check the backend /api/shap
            implementation.
          </p>
        )}
      </CardContent>
    </Card>
  );
}


