"use client";

import { useQuery } from "@tanstack/react-query";
import { getShap } from "@/lib/api";

export function useShap() {
  return useQuery({
    queryKey: ["shap"],
    queryFn: getShap,
    staleTime: 60_000,
  });
}


