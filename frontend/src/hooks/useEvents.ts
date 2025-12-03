"use client";

import { useQuery } from "@tanstack/react-query";
import { useFilters } from "./useFilters";
import { getEvents } from "@/lib/api";

export function useEvents() {
  const realtime = useFilters((s) => s.realtime);

  const query = useQuery({
    queryKey: ["events"],
    queryFn: async () => {
      const data = await getEvents();
      return data.events;
    },
    refetchInterval: realtime ? 5000 : false,
  });

  return query;
}


