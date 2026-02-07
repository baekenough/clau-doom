---
name: typescript-best-practices
description: TypeScript and Next.js App Router patterns for the clau-doom real-time dashboard with WebSocket integration
user-invocable: false
---

# TypeScript Best Practices for clau-doom Dashboard

## Next.js App Router

### Layout Structure

```typescript
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "clau-doom Dashboard",
  description: "Evolutionary AI agent experimentation platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <DashboardShell>{children}</DashboardShell>
      </body>
    </html>
  );
}
```

### Page Organization

```
app/
  layout.tsx              # Root layout with navigation shell
  page.tsx                # Home / experiment overview
  arena/
    page.tsx              # Live game spectation (noVNC)
    loading.tsx           # Arena loading skeleton
  player/
    page.tsx              # Agent statistics
    [agentId]/
      page.tsx            # Individual agent detail
  evolution/
    page.tsx              # Generation tracking and fitness evolution
    loading.tsx
  research/
    page.tsx              # DOE design and ANOVA results
    loading.tsx
    error.tsx             # Research-specific error boundary
  api/
    experiments/
      route.ts            # GET/POST experiments
    generations/
      [id]/
        route.ts          # GET generation data
    ws/
      route.ts            # WebSocket upgrade endpoint
```

### Loading States

```typescript
// app/evolution/loading.tsx
export default function EvolutionLoading() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-48 animate-pulse rounded bg-muted" />
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-64 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    </div>
  );
}
```

### Error Boundaries

```typescript
// app/research/error.tsx
"use client";

export default function ResearchError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <h2 className="text-lg font-semibold">Analysis Error</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <button onClick={reset} className="btn btn-primary">
        Retry Analysis
      </button>
    </div>
  );
}
```

## Server Components vs Client Components

### Server Component (default)

```typescript
// app/evolution/page.tsx - Server Component (no "use client")
import { getGenerationSummary } from "@/lib/data";

export default async function EvolutionPage() {
  const summary = await getGenerationSummary();

  return (
    <div>
      <h1>Evolution Progress</h1>
      <GenerationTable data={summary} />
      <FitnessChart data={summary} /> {/* Client component for interactivity */}
    </div>
  );
}
```

### Client Component

```typescript
// components/fitness-chart.tsx
"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface FitnessChartProps {
  initialData: GenerationSummary[];
}

export function FitnessChart({ initialData }: FitnessChartProps) {
  const [data, setData] = useState(initialData);

  // Real-time updates via WebSocket
  useEffect(() => {
    const ws = new WebSocket(`${getWsUrl()}/api/ws`);
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      if (update.type === "generation_complete") {
        setData((prev) => [...prev, update.payload]);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <XAxis dataKey="generation" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="meanFitness" stroke="#8884d8" name="Mean" />
        <Line type="monotone" dataKey="bestFitness" stroke="#82ca9d" name="Best" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## API Routes

### REST Endpoint

```typescript
// app/api/experiments/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  const experiments = await db.query("SELECT * FROM experiments ORDER BY created_at DESC");
  return NextResponse.json(experiments);
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const validated = ExperimentSchema.safeParse(body);
  if (!validated.success) {
    return NextResponse.json(
      { error: validated.error.flatten() },
      { status: 400 },
    );
  }

  const experiment = await db.insert("experiments", validated.data);
  return NextResponse.json(experiment, { status: 201 });
}
```

### Data Fetching from gRPC Backend

```typescript
// lib/data.ts
import { OrchestratorClient } from "@/lib/grpc-client";

export async function getGenerationSummary(): Promise<GenerationSummary[]> {
  const client = new OrchestratorClient(process.env.GRPC_ENDPOINT!);
  const response = await client.getGenerationStatus({
    experimentId: "current",
  });
  return response.generations.map(mapToSummary);
}
```

## WebSocket Integration

### WebSocket Hook

```typescript
// hooks/use-websocket.ts
"use client";

import { useEffect, useRef, useState, useCallback } from "react";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: unknown) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket({
  url,
  onMessage,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus("connected");
      reconnectCount.current = 0;
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    };

    ws.onclose = () => {
      setStatus("disconnected");
      if (reconnectCount.current < maxReconnectAttempts) {
        reconnectCount.current++;
        setTimeout(connect, reconnectInterval);
      }
    };

    ws.onerror = () => {
      setStatus("error");
    };

    wsRef.current = ws;
  }, [url, onMessage, reconnectInterval, maxReconnectAttempts]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { status, send };
}
```

### Real-Time Event Types

```typescript
// lib/types/events.ts
type ExperimentEvent =
  | { type: "generation_start"; payload: { generationId: number; populationSize: number } }
  | { type: "generation_complete"; payload: GenerationSummary }
  | { type: "agent_evaluated"; payload: AgentScore }
  | { type: "experiment_complete"; payload: { experimentId: string; totalGenerations: number } }
  | { type: "game_frame"; payload: { agentId: string; frame: string } };
```

## Type Safety

### Strict Mode Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Discriminated Unions

```typescript
type AgentStatus =
  | { state: "idle"; lastActive: Date }
  | { state: "evaluating"; gameId: string; startedAt: Date }
  | { state: "completed"; score: number; duration: number }
  | { state: "error"; error: string; retryCount: number };

function getStatusLabel(status: AgentStatus): string {
  switch (status.state) {
    case "idle":
      return `Idle since ${status.lastActive.toISOString()}`;
    case "evaluating":
      return `Playing game ${status.gameId}`;
    case "completed":
      return `Score: ${status.score.toFixed(2)}`;
    case "error":
      return `Error (retry ${status.retryCount}): ${status.error}`;
  }
}
```

### Branded Types

```typescript
type AgentId = string & { readonly __brand: "AgentId" };
type ExperimentId = string & { readonly __brand: "ExperimentId" };
type GenerationId = number & { readonly __brand: "GenerationId" };

function createAgentId(id: string): AgentId {
  if (!id.match(/^agent-[a-z0-9]{8}$/)) {
    throw new Error(`Invalid agent ID format: ${id}`);
  }
  return id as AgentId;
}
```

## State Management

### Zustand Store

```typescript
// stores/experiment-store.ts
import { create } from "zustand";

interface ExperimentState {
  currentExperiment: Experiment | null;
  generations: GenerationSummary[];
  liveAgentScores: Map<string, AgentScore>;
  wsStatus: ConnectionStatus;

  // Actions
  setExperiment: (exp: Experiment) => void;
  addGeneration: (gen: GenerationSummary) => void;
  updateAgentScore: (score: AgentScore) => void;
  setWsStatus: (status: ConnectionStatus) => void;
}

export const useExperimentStore = create<ExperimentState>((set) => ({
  currentExperiment: null,
  generations: [],
  liveAgentScores: new Map(),
  wsStatus: "disconnected",

  setExperiment: (exp) => set({ currentExperiment: exp }),
  addGeneration: (gen) =>
    set((state) => ({ generations: [...state.generations, gen] })),
  updateAgentScore: (score) =>
    set((state) => {
      const newScores = new Map(state.liveAgentScores);
      newScores.set(score.agentId, score);
      return { liveAgentScores: newScores };
    }),
  setWsStatus: (status) => set({ wsStatus: status }),
}));
```

## Testing

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    globals: true,
    css: true,
  },
  resolve: {
    alias: {
      "@": new URL("./src", import.meta.url).pathname,
    },
  },
});
```

### Component Test

```typescript
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AgentCard } from "@/components/agent-card";

describe("AgentCard", () => {
  it("renders agent information correctly", () => {
    render(
      <AgentCard
        agent={{
          id: "agent-abc12345" as AgentId,
          generation: 5 as GenerationId,
          fitness: 0.85,
          status: { state: "completed", score: 0.85, duration: 45 },
        }}
      />,
    );

    expect(screen.getByText("agent-abc12345")).toBeDefined();
    expect(screen.getByText("0.85")).toBeDefined();
  });
});
```
