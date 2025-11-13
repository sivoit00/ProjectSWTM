export default function Visualization() {
  type GraphNode = {
    x: number;
    y: number;
    w: number;
    h: number;
    color: string;
    label: string;
  };

  const graphNodes: Record<string, GraphNode> = {
    insurance: { x: 300, y: 120, w: 140, h: 50, color: "#D46A29", label: "Insurance" },
    chatbot:   { x: 300, y: 300, w: 140, h: 50, color: "#D22DD8", label: "AI Chatbot" },
    guard:     { x: 300, y: 520, w: 140, h: 50, color: "#0A4BFF", label: "GuardRails" },
    server:    { x: 120, y: 200, w: 140, h: 50, color: "#26B6C6", label: "Server" },
    sql:       { x: 140, y: 420, w: 140, h: 50, color: "#E6C62F", label: "SQL Database" },
    lawyer:    { x: 480, y: 200, w: 140, h: 50, color: "#3EC764", label: "Lawyer" },
    garage:    { x: 460, y: 420, w: 140, h: 50, color: "#A237E0", label: "Garage" },
  };

  type NodeKey = keyof typeof graphNodes;

  const graphEdges: [NodeKey, NodeKey][] = [
    ["insurance", "chatbot"],
    ["chatbot", "guard"],
    ["chatbot", "server"],
    ["chatbot", "lawyer"],
    ["chatbot", "garage"],
    ["chatbot", "sql"],
    ["insurance", "server"],
    ["insurance", "lawyer"],
    ["insurance", "sql"],
    ["server", "sql"],
    ["sql", "garage"],
    ["sql", "guard"],
    ["guard", "garage"],
    ["garage", "lawyer"],
  ];

  function edgePoint(a: GraphNode, b: GraphNode) {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const w = a.w / 2;
    const h = a.h / 2;
    const scale = Math.max(Math.abs(dx) / w, Math.abs(dy) / h);
    return { x: a.x + dx / scale, y: a.y + dy / scale };
  }

  return (
    <div className="hidden md:flex w-1/2 items-center justify-center border-l border-white/10 backdrop-blur-xl bg-white/5">
      <div className="relative w-[600px] h-[600px] bg-white/5 rounded-xl border border-white/10">
        <svg width="100%" height="100%">
          {graphEdges.map(([a, b], i) => {
            const A = graphNodes[a];
            const B = graphNodes[b];
            const p1 = edgePoint(A, B);
            const p2 = edgePoint(B, A);
            return (
              <line
                key={i}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#85D4E6"
                strokeWidth="3"
                strokeDasharray="6 6"
              />
            );
          })}

          {Object.values(graphNodes).map((n, i) => (
            <g key={i}>
              <rect
                x={n.x - n.w / 2}
                y={n.y - n.h / 2}
                width={n.w}
                height={n.h}
                rx="12"
                fill={n.color}
              />
              <text x={n.x} y={n.y + 4} textAnchor="middle" fontSize="14" fill="white">
                {n.label}
              </text>
            </g>
          ))}
        </svg>

        <div className="absolute bottom-3 w-full text-center text-sm text-gray-300">
          AI-system-module overview (Sprint 1)
        </div>
      </div>
    </div>
  );
}
