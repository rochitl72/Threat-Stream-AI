'use client';

import { useEffect, useState } from 'react';
import { Activity, Brain, Zap, Clock } from 'lucide-react';

export default function VertexAIProcessing() {
  const [processing, setProcessing] = useState(false);
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    averageLatency: 0,
    model: 'gemini-pro',
    location: 'us-central1',
  });

  useEffect(() => {
    // Simulate processing updates
    const interval = setInterval(() => {
      setProcessing((prev) => !prev);
      setStats((prev) => ({
        ...prev,
        totalAnalyses: prev.totalAnalyses + Math.floor(Math.random() * 3),
        averageLatency: 150 + Math.random() * 50,
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Processing Status */}
      <div className="flex items-center gap-4">
        <div className={`p-4 rounded-lg ${processing ? 'bg-green-500' : 'bg-gray-700'}`}>
          <Brain className="w-8 h-8 text-white" />
        </div>
        <div>
          <div className="text-lg font-semibold">
            {processing ? 'Processing Threats' : 'Idle'}
          </div>
          <div className="text-sm text-gray-400">Vertex AI - Gemini Pro</div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-blue-400" />
            <div className="text-sm text-gray-400">Total Analyses</div>
          </div>
          <div className="text-2xl font-bold">{stats.totalAnalyses}</div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-green-400" />
            <div className="text-sm text-gray-400">Avg Latency</div>
          </div>
          <div className="text-2xl font-bold">{stats.averageLatency.toFixed(0)}ms</div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            <div className="text-sm text-gray-400">Model</div>
          </div>
          <div className="text-lg font-semibold">{stats.model}</div>
        </div>

        <div className="bg-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <div className="text-sm text-gray-400">Location</div>
          </div>
          <div className="text-lg font-semibold">{stats.location}</div>
        </div>
      </div>

      {/* Processing Flow */}
      <div className="bg-gray-700 rounded-lg p-4">
        <div className="text-sm font-semibold mb-3">Processing Pipeline</div>
        <div className="space-y-2">
          {['Telemetry Analysis', 'Code Sample Analysis', 'Dark Web Feed Analysis'].map(
            (step, index) => (
              <div key={step} className="flex items-center gap-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    processing && index === 0 ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
                  }`}
                />
                <div className="text-sm">{step}</div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

