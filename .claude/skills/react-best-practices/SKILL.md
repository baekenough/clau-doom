---
name: react-best-practices
description: React component patterns for clau-doom dashboard UI including recharts visualization, noVNC integration, and real-time updates
user-invocable: false
---

# React Best Practices for clau-doom Dashboard UI

## Component Design

### Composition Over Inheritance

```tsx
// Base card component composed by domain-specific cards
function Card({ title, children, actions }: CardProps) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        {actions && <div className="flex gap-2">{actions}</div>}
      </div>
      <div className="mt-3">{children}</div>
    </div>
  );
}

// Domain-specific composition
function AgentScoreCard({ agent }: { agent: AgentScore }) {
  return (
    <Card
      title={`Agent ${agent.id}`}
      actions={<StatusBadge status={agent.status} />}
    >
      <div className="grid grid-cols-2 gap-2">
        <MetricDisplay label="Kills" value={agent.kills} />
        <MetricDisplay label="Deaths" value={agent.deaths} />
        <MetricDisplay label="Health" value={`${agent.health}%`} />
        <MetricDisplay label="Fitness" value={agent.fitness.toFixed(3)} />
      </div>
    </Card>
  );
}
```

### Custom Hooks for Domain Logic

```tsx
// hooks/use-generation-data.ts
function useGenerationData(experimentId: string) {
  const [generations, setGenerations] = useState<GenerationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const response = await fetch(`/api/experiments/${experimentId}/generations`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!cancelled) {
          setGenerations(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error("Unknown error"));
          setLoading(false);
        }
      }
    }

    fetchData();
    return () => { cancelled = true; };
  }, [experimentId]);

  return { generations, loading, error };
}
```

### Render Props for Flexible Data Display

```tsx
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  renderRow?: (item: T, index: number) => React.ReactNode;
  onRowClick?: (item: T) => void;
}

function DataTable<T extends { id: string }>({
  data,
  columns,
  renderRow,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key}>{col.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((item, i) =>
          renderRow ? (
            renderRow(item, i)
          ) : (
            <tr key={item.id} onClick={() => onRowClick?.(item)}>
              {columns.map((col) => (
                <td key={col.key}>{col.render(item)}</td>
              ))}
            </tr>
          ),
        )}
      </tbody>
    </table>
  );
}
```

## recharts / d3 Visualization

### Fitness Evolution Chart

```tsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Area, ComposedChart, Brush,
} from "recharts";

function FitnessEvolutionChart({ data }: { data: GenerationSummary[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
        <XAxis dataKey="generation" label={{ value: "Generation", position: "bottom" }} />
        <YAxis label={{ value: "Fitness", angle: -90, position: "insideLeft" }} />
        <Tooltip content={<FitnessTooltip />} />
        <Legend />
        <Area
          type="monotone"
          dataKey="stdRange"
          fill="#8884d8"
          fillOpacity={0.1}
          stroke="none"
          name="Std Dev Range"
        />
        <Line type="monotone" dataKey="meanFitness" stroke="#8884d8" strokeWidth={2} name="Mean" dot={false} />
        <Line type="monotone" dataKey="bestFitness" stroke="#82ca9d" strokeWidth={1} strokeDasharray="5 5" name="Best" dot={false} />
        <Line type="monotone" dataKey="medianFitness" stroke="#ffc658" strokeWidth={1} name="Median" dot={false} />
        <Brush dataKey="generation" height={30} stroke="#8884d8" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
```

### Custom Tooltip

```tsx
function FitnessTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-md border bg-popover p-3 shadow-md">
      <p className="font-semibold">Generation {label}</p>
      {payload.map((entry: any) => (
        <p key={entry.name} style={{ color: entry.color }}>
          {entry.name}: {entry.value.toFixed(4)}
        </p>
      ))}
    </div>
  );
}
```

### ANOVA Results Visualization

```tsx
import { BarChart, Bar, ErrorBar, Cell } from "recharts";

function ANOVAResultsChart({
  factors,
  pValues,
}: {
  factors: string[];
  pValues: number[];
}) {
  const data = factors.map((factor, i) => ({
    factor,
    negLogP: -Math.log10(pValues[i]),
    significant: pValues[i] < 0.05,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="factor" />
        <YAxis label={{ value: "-log10(p)", angle: -90, position: "insideLeft" }} />
        <Tooltip
          formatter={(value: number) => [
            `p = ${Math.pow(10, -value).toExponential(2)}`,
            "-log10(p)",
          ]}
        />
        {/* Significance threshold line at p=0.05 */}
        <ReferenceLine y={-Math.log10(0.05)} stroke="red" strokeDasharray="3 3" label="p=0.05" />
        <Bar dataKey="negLogP">
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.significant ? "#22c55e" : "#94a3b8"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
```

### Real-Time Agent Scatter Plot

```tsx
import { ScatterChart, Scatter, ZAxis } from "recharts";

function AgentPerformanceScatter({ agents }: { agents: AgentScore[] }) {
  const data = agents.map((a) => ({
    kills: a.kills,
    deaths: a.deaths,
    fitness: a.fitness,
    id: a.agentId,
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart>
        <CartesianGrid />
        <XAxis dataKey="kills" name="Kills" />
        <YAxis dataKey="deaths" name="Deaths" />
        <ZAxis dataKey="fitness" range={[20, 200]} name="Fitness" />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        <Scatter data={data} fill="#8884d8" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
```

## noVNC Integration

### Embedding noVNC Client

```tsx
"use client";

import { useEffect, useRef, useState } from "react";

interface VNCViewerProps {
  host: string;
  port: number;
  path?: string;
  agentId: string;
}

function VNCViewer({ host, port, path = "websockify", agentId }: VNCViewerProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const rfbRef = useRef<any>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let rfb: any;

    async function connect() {
      // Dynamic import for noVNC (client-side only)
      const { default: RFB } = await import("@novnc/novnc/core/rfb");

      if (!canvasRef.current) return;

      const url = `ws://${host}:${port}/${path}`;
      rfb = new RFB(canvasRef.current, url, {
        credentials: { password: "" },
      });

      rfb.viewOnly = true;
      rfb.scaleViewport = true;
      rfb.resizeSession = false;

      rfb.addEventListener("connect", () => setConnected(true));
      rfb.addEventListener("disconnect", () => setConnected(false));

      rfbRef.current = rfb;
    }

    connect();

    return () => {
      rfbRef.current?.disconnect();
    };
  }, [host, port, path]);

  return (
    <div className="relative">
      <div className="absolute left-2 top-2 z-10 flex items-center gap-2">
        <div className={`h-2 w-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
        <span className="text-xs text-white/80">Agent: {agentId}</span>
      </div>
      <div ref={canvasRef} className="aspect-video w-full rounded-lg bg-black" />
    </div>
  );
}
```

### Multi-Agent Arena View

```tsx
function ArenaGrid({ agents }: { agents: ActiveAgent[] }) {
  const layout = agents.length <= 4 ? "grid-cols-2" : "grid-cols-3";

  return (
    <div className={`grid ${layout} gap-2`}>
      {agents.map((agent) => (
        <VNCViewer
          key={agent.id}
          host={agent.vncHost}
          port={agent.vncPort}
          agentId={agent.id}
        />
      ))}
    </div>
  );
}
```

## Performance Optimization

### React.memo for Expensive Renders

```tsx
const AgentRow = React.memo(function AgentRow({
  agent,
  onSelect,
}: {
  agent: AgentScore;
  onSelect: (id: string) => void;
}) {
  return (
    <tr onClick={() => onSelect(agent.agentId)} className="cursor-pointer hover:bg-muted">
      <td>{agent.agentId}</td>
      <td>{agent.kills}</td>
      <td>{agent.deaths}</td>
      <td>{agent.fitness.toFixed(4)}</td>
    </tr>
  );
});
```

### useMemo for Derived Data

```tsx
function GenerationStats({ scores }: { scores: AgentScore[] }) {
  const stats = useMemo(() => {
    const fitnesses = scores.map((s) => s.fitness);
    return {
      mean: fitnesses.reduce((a, b) => a + b, 0) / fitnesses.length,
      max: Math.max(...fitnesses),
      min: Math.min(...fitnesses),
      std: standardDeviation(fitnesses),
    };
  }, [scores]);

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard label="Mean" value={stats.mean.toFixed(4)} />
      <StatCard label="Max" value={stats.max.toFixed(4)} />
      <StatCard label="Min" value={stats.min.toFixed(4)} />
      <StatCard label="Std Dev" value={stats.std.toFixed(4)} />
    </div>
  );
}
```

### useCallback for Stable References

```tsx
function ExperimentDashboard() {
  const { addGeneration, updateAgentScore } = useExperimentStore();

  const handleMessage = useCallback(
    (data: ExperimentEvent) => {
      switch (data.type) {
        case "generation_complete":
          addGeneration(data.payload);
          break;
        case "agent_evaluated":
          updateAgentScore(data.payload);
          break;
      }
    },
    [addGeneration, updateAgentScore],
  );

  useWebSocket({
    url: `${getWsUrl()}/api/ws`,
    onMessage: handleMessage,
  });

  return <>{/* dashboard content */}</>;
}
```

### Virtualization for Large Lists

```tsx
import { useVirtualizer } from "@tanstack/react-virtual";

function AgentList({ agents }: { agents: AgentScore[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: agents.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: "relative" }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <AgentRow agent={agents[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Dashboard Tabs

### Tab Structure

| Tab | Purpose | Key Components |
|-----|---------|----------------|
| Arena | Live game spectation | noVNC viewers, real-time scores |
| Player | Agent statistics | Agent list, detail cards, performance history |
| Evolution | Generation tracking | Fitness evolution chart, generation table, population diversity |
| Research | DOE/ANOVA results | Factor analysis, significance plots, residual diagnostics |

### Tab Navigation

```tsx
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";

const tabs = [
  { href: "/arena", label: "Arena", icon: GamepadIcon },
  { href: "/player", label: "Player", icon: UserIcon },
  { href: "/evolution", label: "Evolution", icon: TrendingUpIcon },
  { href: "/research", label: "Research", icon: FlaskIcon },
];

function DashboardNav() {
  const pathname = usePathname();

  return (
    <nav className="flex border-b">
      {tabs.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          className={`flex items-center gap-2 px-4 py-2 ${
            pathname.startsWith(tab.href)
              ? "border-b-2 border-primary text-primary"
              : "text-muted-foreground"
          }`}
        >
          <tab.icon className="h-4 w-4" />
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
```

## Accessibility

- All interactive elements have `aria-label` or visible text
- Charts include `aria-describedby` with summary text
- Color is not the sole indicator (use patterns, labels)
- Keyboard navigation support for all tabs and controls
- Focus management when switching between views
