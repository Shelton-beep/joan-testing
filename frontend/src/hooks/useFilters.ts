"use client";

import { create } from "zustand";

export type StatusFilter = "all" | "success" | "fail";
export type AnomalyFilter = "all" | "normal" | "anomaly";

type FiltersState = {
  startDate: string;
  endDate: string;
  userId: string;
  location: string;
  eventLabel: string;
  status: StatusFilter;
  anomalyStatus: AnomalyFilter;
  realtime: boolean;
  setStartDate: (v: string) => void;
  setEndDate: (v: string) => void;
  setUserId: (v: string) => void;
  setLocation: (v: string) => void;
  setEventLabel: (v: string) => void;
  setStatus: (v: StatusFilter) => void;
  setAnomalyStatus: (v: AnomalyFilter) => void;
  toggleRealtime: () => void;
};

export const useFilters = create<FiltersState>((set) => ({
  startDate: "",
  endDate: "",
  userId: "All",
  location: "All",
  eventLabel: "All",
  status: "all",
  anomalyStatus: "all",
  realtime: false,
  setStartDate: (v) => set({ startDate: v }),
  setEndDate: (v) => set({ endDate: v }),
  setUserId: (v) => set({ userId: v }),
  setLocation: (v) => set({ location: v }),
  setEventLabel: (v) => set({ eventLabel: v }),
  setStatus: (v) => set({ status: v }),
  setAnomalyStatus: (v) => set({ anomalyStatus: v }),
  toggleRealtime: () => set((s) => ({ realtime: !s.realtime })),
}));


