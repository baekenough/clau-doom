# TypeScript Reference Guide

Reference documentation for TypeScript development in clau-doom dashboard.

## Key Resources

- [Next.js App Router](https://nextjs.org/docs/app)
- [Recharts](https://recharts.org/)
- [noVNC](https://novnc.com/)
- [Zustand](https://docs.pmnd.rs/zustand)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## clau-doom Context

The dashboard is a Next.js 14+ application providing real-time DOOM spectation, research visualization, and experiment monitoring. It connects to the Go orchestrator via WebSocket and embeds noVNC for game screen streaming.

Project layout:
```
dashboard/
├── app/
│   ├── layout.tsx            # Root layout with providers
│   ├── page.tsx              # Home / overview
│   ├── arena/
│   │   └── page.tsx          # Multi-agent spectation grid
│   ├── player/
│   │   └── [id]/page.tsx     # Individual agent detail
│   ├── evolution/
│   │   └── page.tsx          # Generation trends + SPC charts
│   └── research/
│       └── page.tsx          # DOE visualization + ANOVA tables
├── components/
│   ├── vnc-viewer.tsx        # noVNC wrapper
│   ├── charts/               # Recharts components
│   └── tables/               # Data tables
├── lib/
│   ├── websocket.ts          # WebSocket client
│   └── store.ts              # Zustand stores
└── types/
    └── index.ts              # Shared type definitions
```

## Next.js 14+ App Router

### Layouts

```tsx
// app/layout.tsx
import { StoreProvider } from '@/components/store-provider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <StoreProvider>
          <nav className="flex gap-4 p-4 border-b">
            <Link href="/arena">Arena</Link>
            <Link href="/evolution">Evolution</Link>
            <Link href="/research">Research</Link>
          </nav>
          {children}
        </StoreProvider>
      </body>
    </html>
  );
}
```

### Server Components (default)

Server components fetch data at request time. Use for initial page loads and static content.

```tsx
// app/evolution/page.tsx (Server Component)
async function getGenerationData() {
  const res = await fetch('http://orchestrator:8080/api/generations', {
    next: { revalidate: 30 }, // ISR: revalidate every 30s
  });
  return res.json();
}

export default async function EvolutionPage() {
  const data = await getGenerationData();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Evolution Tracker</h1>
      <GenerationChart data={data.generations} />
      <SPCControlChart data={data.spc} />
    </div>
  );
}
```

### Client Components

Client components handle interactivity, WebSocket connections, and real-time updates.

```tsx
// components/charts/spc-chart.tsx
'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, ReferenceLine, Tooltip, Legend } from 'recharts';

interface SPCData {
  generation: number;
  xBar: number;
  ucl: number;
  lcl: number;
  cl: number;
}

export function SPCControlChart({ initialData }: { initialData: SPCData[] }) {
  const [data, setData] = useState(initialData);

  // Subscribe to real-time SPC updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/spc');
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data) as SPCData;
      setData(prev => [...prev, update]);
    };
    return () => ws.close();
  }, []);

  const cl = data[0]?.cl ?? 0;
  const ucl = data[0]?.ucl ?? 0;
  const lcl = data[0]?.lcl ?? 0;

  return (
    <LineChart width={800} height={400} data={data}>
      <XAxis dataKey="generation" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="xBar" stroke="#2563eb" dot={{ r: 3 }} />
      <ReferenceLine y={cl} stroke="green" strokeDasharray="5 5" label="CL" />
      <ReferenceLine y={ucl} stroke="red" strokeDasharray="5 5" label="UCL" />
      <ReferenceLine y={lcl} stroke="red" strokeDasharray="5 5" label="LCL" />
    </LineChart>
  );
}
```

### API Routes

```tsx
// app/api/agents/[id]/route.ts
import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const agentData = await fetchAgentFromOrchestrator(params.id);
  return NextResponse.json(agentData);
}
```

## WebSocket for Real-Time Updates

### WebSocket Client

```tsx
// lib/websocket.ts
type MessageHandler = (data: unknown) => void;

export class GameSocket {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<MessageHandler>>();
  private reconnectTimer: NodeJS.Timeout | null = null;

  connect(url: string) {
    this.ws = new WebSocket(url);

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const handlers = this.handlers.get(message.type);
      handlers?.forEach(handler => handler(message.payload));
    };

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(url), 3000);
    };
  }

  subscribe(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);

    return () => {
      this.handlers.get(type)?.delete(handler);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
  }
}
```

## Recharts

### Line Chart for Generation Trends

```tsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export function GenerationChart({ data }: { data: GenerationMetrics[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="generation" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="avgKillRate"
              stroke="#2563eb" name="Kill Rate" />
        <Line yAxisId="left" type="monotone" dataKey="avgSurvivalTime"
              stroke="#16a34a" name="Survival Time" />
        <Line yAxisId="right" type="monotone" dataKey="cpk"
              stroke="#dc2626" name="Cpk" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Bar Chart for DOE Main Effects

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export function MainEffectChart({ effects }: { effects: EffectData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={effects}>
        <XAxis dataKey="factor" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="effect" fill={(entry) =>
          entry.significant ? '#dc2626' : '#94a3b8'
        } />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

## noVNC Embedding

```tsx
// components/vnc-viewer.tsx
'use client';

import { useEffect, useRef } from 'react';
import RFB from '@novnc/novnc/core/rfb';

interface VNCViewerProps {
  url: string;       // WebSocket URL: ws://localhost:6901/websockify
  agentId: string;
  width?: number;
  height?: number;
}

export function VNCViewer({ url, agentId, width = 640, height = 480 }: VNCViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rfbRef = useRef<RFB | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const rfb = new RFB(containerRef.current, url, {
      scaleViewport: true,
      resizeSession: false,
    });
    rfb.viewOnly = true; // Spectation only
    rfbRef.current = rfb;

    return () => {
      rfb.disconnect();
    };
  }, [url]);

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-800 text-white px-3 py-1 text-sm">
        {agentId}
      </div>
      <div ref={containerRef} style={{ width, height }} />
    </div>
  );
}
```

### Arena Grid

```tsx
// app/arena/page.tsx
'use client';

import { VNCViewer } from '@/components/vnc-viewer';
import { useAgentStore } from '@/lib/store';

export default function ArenaPage() {
  const agents = useAgentStore(state => state.activeAgents);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Arena</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map(agent => (
          <VNCViewer
            key={agent.id}
            url={`ws://localhost:${agent.vncPort}/websockify`}
            agentId={agent.id}
            width={320}
            height={240}
          />
        ))}
      </div>
    </div>
  );
}
```

## Zustand State Management

```tsx
// lib/store.ts
import { create } from 'zustand';

interface Agent {
  id: string;
  generation: number;
  health: number;
  kills: number;
  vncPort: number;
  phase: string;
}

interface AgentStore {
  activeAgents: Agent[];
  selectedAgent: string | null;
  setAgents: (agents: Agent[]) => void;
  updateAgent: (id: string, update: Partial<Agent>) => void;
  selectAgent: (id: string | null) => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  activeAgents: [],
  selectedAgent: null,
  setAgents: (agents) => set({ activeAgents: agents }),
  updateAgent: (id, update) =>
    set((state) => ({
      activeAgents: state.activeAgents.map((a) =>
        a.id === id ? { ...a, ...update } : a
      ),
    })),
  selectAgent: (id) => set({ selectedAgent: id }),
}));

// Research store for experiment data
interface ResearchStore {
  currentExperiment: string | null;
  anovaResults: ANOVATable | null;
  doeMatrix: DOERun[];
  setExperiment: (id: string) => void;
  setAnovaResults: (results: ANOVATable) => void;
}

export const useResearchStore = create<ResearchStore>((set) => ({
  currentExperiment: null,
  anovaResults: null,
  doeMatrix: [],
  setExperiment: (id) => set({ currentExperiment: id }),
  setAnovaResults: (results) => set({ anovaResults: results }),
}));
```

## Package Dependencies

| Package | Purpose |
|---------|---------|
| `next` | React framework (App Router) |
| `react` / `react-dom` | UI library |
| `recharts` | Charting library |
| `@novnc/novnc` | VNC client |
| `zustand` | State management |
| `tailwindcss` | Utility CSS |
| `typescript` | Type safety |
