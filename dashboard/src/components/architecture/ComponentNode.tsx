'use client';

interface ComponentNodeProps {
  component: {
    id: string;
    name: string;
    status: 'active' | 'idle' | 'error';
    type: string;
  };
}

export default function ComponentNode({ component }: ComponentNodeProps) {
  const statusColors = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  const typeIcons = {
    producer: '📤',
    kafka: '⚡',
    processor: '⚙️',
    ai: '🤖',
    dashboard: '📊',
  };

  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-20 h-20 rounded-lg ${statusColors[component.status]} flex items-center justify-center text-3xl shadow-lg transition-all duration-300 hover:scale-110`}
      >
        {typeIcons[component.type as keyof typeof typeIcons] || '📦'}
      </div>
      <div className="mt-2 text-center">
        <div className="font-semibold text-sm">{component.name}</div>
        <div className="text-xs text-gray-400 capitalize">{component.status}</div>
      </div>
    </div>
  );
}

