'use client';

import { useEffect, useState } from 'react';

interface DataFlowProps {
  data: any;
}

export default function DataFlow({ data }: DataFlowProps) {
  const [messageCount, setMessageCount] = useState(0);

  useEffect(() => {
    if (data?.topics) {
      const total = Object.values(data.topics).reduce(
        (sum: number, topic: any) => sum + (topic.message_count || 0),
        0
      );
      setMessageCount(total);
    }
  }, [data]);

  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
      {/* Animated data particles */}
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 bg-blue-400 rounded-full animate-ping"
          style={{
            left: `${20 + i * 15}%`,
            animationDelay: `${i * 0.5}s`,
            animationDuration: '2s',
          }}
        />
      ))}

      {/* Message count overlay */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="bg-black bg-opacity-50 px-4 py-2 rounded-lg">
          <div className="text-2xl font-bold text-blue-400">{messageCount}</div>
          <div className="text-xs text-gray-400">Messages Processed</div>
        </div>
      </div>
    </div>
  );
}

