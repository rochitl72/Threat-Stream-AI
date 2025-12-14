'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface KafkaTopicsMonitorProps {
  data: any;
}

export default function KafkaTopicsMonitor({ data }: KafkaTopicsMonitorProps) {
  const [topics, setTopics] = useState<any[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    if (data?.topics) {
      const topicsList = Object.entries(data.topics).map(([name, info]: [string, any]) => ({
        name,
        messageCount: info.message_count || 0,
        messagesPerSecond: info.metrics?.messages_per_second || 0,
        lastMessage: info.last_message?.timestamp,
      }));
      setTopics(topicsList);

      // Prepare chart data
      setChartData(
        topicsList.map((topic) => ({
          name: topic.name.replace('-', ' '),
          messages: topic.messageCount,
          rate: topic.messagesPerSecond,
        }))
      );
    }
  }, [data]);

  return (
    <div className="space-y-4">
      {/* Topics List */}
      <div className="grid grid-cols-2 gap-4">
        {topics.map((topic) => (
          <div
            key={topic.name}
            className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500"
          >
            <div className="font-semibold text-sm mb-1">{topic.name}</div>
            <div className="text-2xl font-bold text-blue-400">{topic.messageCount}</div>
            <div className="text-xs text-gray-400">
              {topic.messagesPerSecond.toFixed(2)} msg/s
            </div>
          </div>
        ))}
      </div>

      {/* Message Rate Chart */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Message Rate</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            />
            <Bar dataKey="messages" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

