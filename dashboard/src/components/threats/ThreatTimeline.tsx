'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, Shield, Activity } from 'lucide-react';

interface ThreatTimelineProps {}

export default function ThreatTimeline({}: ThreatTimelineProps) {
  const [threats, setThreats] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    // Fetch recent threats
    fetch('/api/threats?limit=10')
      .then((res) => res.json())
      .then((data) => setThreats(data))
      .catch((err) => console.error('Error fetching threats:', err));

    // Fetch recent alerts
    fetch('/api/threats/alerts/recent?limit=10')
      .then((res) => res.json())
      .then((data) => setAlerts(data))
      .catch((err) => console.error('Error fetching alerts:', err));
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-600';
      case 'high':
        return 'bg-orange-600';
      case 'medium':
        return 'bg-yellow-600';
      case 'low':
        return 'bg-green-600';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Recent Alerts */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <h3 className="text-lg font-semibold">Recent Alerts</h3>
        </div>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {alerts.length > 0 ? (
            alerts.map((alert, index) => (
              <div
                key={index}
                className="bg-gray-700 rounded-lg p-4 border-l-4 border-red-500"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold">{alert.threat_type || 'Unknown Threat'}</div>
                  <div
                    className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(
                      alert.severity
                    )}`}
                  >
                    {alert.severity?.toUpperCase() || 'UNKNOWN'}
                  </div>
                </div>
                <div className="text-sm text-gray-400">{alert.description || 'No description'}</div>
                <div className="text-xs text-gray-500 mt-2">
                  {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Unknown time'}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center text-gray-400 py-8">No alerts yet</div>
          )}
        </div>
      </div>

      {/* Threat Profiles */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold">Threat Profiles</h3>
        </div>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {threats.length > 0 ? (
            threats.map((threat, index) => (
              <div
                key={index}
                className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold">
                    {threat.threat_type || 'Unknown Threat'}
                  </div>
                  <div
                    className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(
                      threat.severity
                    )}`}
                  >
                    {threat.severity?.toUpperCase() || 'UNKNOWN'}
                  </div>
                </div>
                <div className="text-sm text-gray-400">
                  Confidence: {(threat.confidence_score * 100).toFixed(1)}%
                </div>
                {threat.autonomous_system_indicators?.length > 0 && (
                  <div className="mt-2 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    <span className="text-xs text-purple-400">
                      Autonomous System Detected
                    </span>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center text-gray-400 py-8">No threats detected yet</div>
          )}
        </div>
      </div>
    </div>
  );
}

