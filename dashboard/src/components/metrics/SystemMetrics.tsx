'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Cpu, HardDrive, Activity } from 'lucide-react';

export default function SystemMetrics() {
  const [metrics, setMetrics] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    const fetchMetrics = () => {
      fetch('/api/metrics/system')
        .then((res) => res.json())
        .then((data) => {
          setMetrics(data);
          // Add to chart data
          setChartData((prev) => [
            ...prev.slice(-19),
            {
              time: new Date().toLocaleTimeString(),
              cpu: data.cpu?.percent || 0,
              memory: data.memory?.percent || 0,
            },
          ]);
        })
        .catch((err) => console.error('Error fetching metrics:', err));
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return <div className="text-center text-gray-400 py-8">Loading metrics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <div className="text-sm text-gray-400">CPU Usage</div>
          </div>
          <div className="text-2xl font-bold">{metrics.cpu?.percent?.toFixed(1) || 0}%</div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.cpu?.count || 0} cores
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <HardDrive className="w-5 h-5 text-green-400" />
            <div className="text-sm text-gray-400">Memory Usage</div>
          </div>
          <div className="text-2xl font-bold">
            {metrics.memory?.percent?.toFixed(1) || 0}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.memory?.used?.toFixed(2) || 0} GB /{' '}
            {metrics.memory?.total?.toFixed(2) || 0} GB
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-purple-400" />
            <div className="text-sm text-gray-400">Uptime</div>
          </div>
          <div className="text-2xl font-bold">
            {metrics.uptime ? Math.floor(metrics.uptime / 3600) : 0}h
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.uptime
              ? `${Math.floor((metrics.uptime % 3600) / 60)}m ${Math.floor(metrics.uptime % 60)}s`
              : '0m 0s'}
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Performance Over Time</h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9ca3af" fontSize={10} />
            <YAxis stroke="#9ca3af" fontSize={10} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
            />
            <Area
              type="monotone"
              dataKey="cpu"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              name="CPU %"
            />
            <Area
              type="monotone"
              dataKey="memory"
              stroke="#10b981"
              fill="#10b981"
              fillOpacity={0.3}
              name="Memory %"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

