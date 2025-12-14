'use client';

import { useEffect, useState } from 'react';
import ComponentNode from './ComponentNode';
import DataFlow from './DataFlow';

interface ArchitectureViewProps {
  data: any;
}

export default function ArchitectureView({ data }: ArchitectureViewProps) {
  const [components, setComponents] = useState([
    { id: 'producers', name: 'Data Producers', status: 'active', type: 'producer' },
    { id: 'kafka', name: 'Confluent Kafka', status: 'active', type: 'kafka' },
    { id: 'consumer', name: 'Threat Consumer', status: 'active', type: 'processor' },
    { id: 'vertex', name: 'Vertex AI', status: 'active', type: 'ai' },
    { id: 'mitre', name: 'MITRE Mapper', status: 'active', type: 'processor' },
    { id: 'dashboard', name: 'Dashboard', status: 'active', type: 'dashboard' },
  ]);

  useEffect(() => {
    // Update component status based on live data
    if (data?.topics) {
      setComponents((prev) =>
        prev.map((comp) => {
          if (comp.id === 'kafka') {
            const hasMessages = Object.values(data.topics).some(
              (topic: any) => topic.message_count > 0
            );
            return { ...comp, status: hasMessages ? 'active' : 'idle' };
          }
          return comp;
        })
      );
    }
  }, [data]);

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
      <h2 className="text-2xl font-bold mb-6">System Architecture - Live View</h2>
      <div className="relative">
        {/* Architecture Flow */}
        <div className="grid grid-cols-6 gap-4 items-center">
          {components.map((component, index) => (
            <div key={component.id} className="flex flex-col items-center">
              <ComponentNode component={component} />
              {index < components.length - 1 && (
                <div className="w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500 mt-4 mb-4 animate-pulse" />
              )}
            </div>
          ))}
        </div>

        {/* Data Flow Animation */}
        <DataFlow data={data} />
      </div>

      {/* Component Status Legend */}
      <div className="mt-6 flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
          <span>Active</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full" />
          <span>Idle</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          <span>Error</span>
        </div>
      </div>
    </div>
  );
}

