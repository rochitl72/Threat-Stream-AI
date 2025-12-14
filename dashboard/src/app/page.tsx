'use client';

import { useEffect, useState } from 'react';
import ArchitectureView from '@/components/architecture/ArchitectureView';
import KafkaTopicsMonitor from '@/components/kafka/KafkaTopicsMonitor';
import VertexAIProcessing from '@/components/vertexai/VertexAIProcessing';
import MITREMatrix from '@/components/mitre/MITREMatrix';
import ThreatTimeline from '@/components/threats/ThreatTimeline';
import SystemMetrics from '@/components/metrics/SystemMetrics';
import DataGeneratorControl from '@/components/generator/DataGeneratorControl';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Dashboard() {
  const [liveData, setLiveData] = useState<any>(null);
  const { data, connected } = useWebSocket('ws://localhost:8000/ws/live');

  useEffect(() => {
    if (data) {
      setLiveData(data);
    }
  }, [data]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">
                ThreatStream AI
              </h1>
              <p className="text-gray-400">
                Real-time Threat Intelligence & Monitoring Dashboard
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className={`px-4 py-2 rounded-lg ${connected ? 'bg-green-500' : 'bg-red-500'}`}>
                {connected ? '🟢 Connected' : '🔴 Disconnected'}
              </div>
            </div>
          </div>
        </header>

        {/* Architecture View - Full Width */}
        <section className="mb-8">
          <ArchitectureView data={liveData} />
        </section>

        {/* Data Generator Control Panel */}
        <section className="mb-6 bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Data Generator Control</h2>
          <DataGeneratorControl />
        </section>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Kafka Topics Monitor */}
          <section className="bg-gray-800 rounded-lg p-6 shadow-xl">
            <h2 className="text-2xl font-bold mb-4">Kafka Topics Monitor</h2>
            <KafkaTopicsMonitor data={liveData} />
          </section>

          {/* System Metrics */}
          <section className="bg-gray-800 rounded-lg p-6 shadow-xl">
            <h2 className="text-2xl font-bold mb-4">System Metrics</h2>
            <SystemMetrics />
          </section>
        </div>

        {/* Vertex AI Processing */}
        <section className="mb-6 bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Vertex AI Processing</h2>
          <VertexAIProcessing />
        </section>

        {/* MITRE ATT&CK Matrix */}
        <section className="mb-6 bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">MITRE ATT&CK for AI Matrix</h2>
          <MITREMatrix />
        </section>

        {/* Threat Timeline */}
        <section className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Threat Timeline</h2>
          <ThreatTimeline />
        </section>
      </div>
    </main>
  );
}

