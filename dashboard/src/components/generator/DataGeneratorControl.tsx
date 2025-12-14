'use client';

import { useEffect, useState } from 'react';
import { Play, Square, Loader2, Zap, Code, Globe, Shield } from 'lucide-react';

interface DataGeneratorControlProps {}

export default function DataGeneratorControl({}: DataGeneratorControlProps) {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [activeGenerators, setActiveGenerators] = useState<any[]>([]);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    // Fetch available scenarios
    fetch('/api/generator/scenarios')
      .then((res) => res.json())
      .then((data) => {
        if (data.success && data.output) {
          // Parse scenarios from output
          const lines = data.output.split('\n');
          const scenarioList = lines
            .filter((line: string) => line.trim().startsWith('-'))
            .map((line: string) => line.trim().substring(2));
          setScenarios(scenarioList);
        }
      })
      .catch((err) => console.error('Error fetching scenarios:', err));

    // Poll for active generators
    const interval = setInterval(() => {
      fetch('/api/generator/active')
        .then((res) => res.json())
        .then((data) => {
          setActiveGenerators(Object.entries(data.active_generators || {}).map(([id, info]: [string, any]) => ({
            id,
            ...info
          })));
        })
        .catch((err) => console.error('Error fetching active generators:', err));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async (endpoint: string, params: any = {}) => {
    setLoading({ ...loading, [endpoint]: true });
    
    try {
      const queryParams = new URLSearchParams();
      if (params.count) queryParams.append('count', params.count.toString());
      if (params.duration) queryParams.append('duration', params.duration.toString());
      if (params.pattern) queryParams.append('pattern', params.pattern);
      
      const url = `/api/generator/${endpoint}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:49',message:'handleGenerate called',data:{endpoint,params,url},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      const response = await fetch(url, {
        method: 'POST',
      });
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:56',message:'Response received',data:{status:response.status,statusText:response.statusText,headers:Object.fromEntries(response.headers.entries()),contentType:response.headers.get('content-type')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      
      // Check if response is OK
      if (!response.ok) {
        const errorText = await response.text();
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:62',message:'Response not OK',data:{status:response.status,errorText:errorText.substring(0,200)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B2'})}).catch(()=>{});
        // #endregion
        throw new Error(`Server error: ${response.status} ${response.statusText}. ${errorText.substring(0, 100)}`);
      }
      
      const responseText = await response.text();
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:60',message:'Response text before JSON parse',data:{responseText:responseText.substring(0,200),length:responseText.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      let data;
      try {
        data = JSON.parse(responseText);
      } catch (parseError: any) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:67',message:'JSON parse error',data:{error:parseError.message,responseText:responseText.substring(0,500)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        throw new Error(`Invalid JSON response: ${responseText.substring(0, 100)}`);
      }
      
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:72',message:'JSON parsed successfully',data:{success:data.success,hasError:!!data.error},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      
      if (data.success) {
        // Show success notification (you can replace with a toast library)
        console.log(`✅ ${data.message || 'Generator started successfully!'}`);
      } else {
        console.error(`❌ Error: ${data.error || 'Failed to start generator'}`);
        alert(`❌ Error: ${data.error || 'Failed to start generator'}`);
      }
    } catch (error: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/285471ae-1206-43c6-850b-7cfa93f8f37b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DataGeneratorControl.tsx:87',message:'Exception caught',data:{error:error.message,stack:error.stack?.substring(0,200),name:error.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
      // #endregion
      console.error(`❌ Error: ${error}`);
      
      // Check if it's a network/connection error
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError') || error.name === 'TypeError') {
        alert(`❌ Cannot connect to backend server.\n\nPlease ensure the dashboard backend is running:\n1. Check Terminal 2 (Backend API)\n2. Restart with: cd /Users/rochitlen/Downloads/animus && ./start_dashboard.sh\n\nError: ${error.message}`);
      } else {
        alert(`❌ Error: ${error.message || 'Failed to start generator'}`);
      }
    } finally {
      setLoading({ ...loading, [endpoint]: false });
    }
  };

  const handleStop = async (taskId: string) => {
    try {
      const response = await fetch(`/api/generator/stop/${taskId}`, {
        method: 'POST',
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(`✅ ${data.message || 'Generator stopped successfully!'}`);
      } else {
        alert(`❌ Error: ${data.error || 'Failed to stop generator'}`);
      }
    } catch (error) {
      alert(`❌ Error: ${error}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => handleGenerate('generate/all', { duration: 300 })}
            disabled={loading['generate/all']}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            {loading['generate/all'] ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Zap className="w-5 h-5" />
            )}
            <span>Generate All (5min)</span>
          </button>

          <button
            onClick={() => handleGenerate('generate/telemetry', { count: 100 })}
            disabled={loading['generate/telemetry']}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            {loading['generate/telemetry'] ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Globe className="w-5 h-5" />
            )}
            <span>Telemetry (100)</span>
          </button>

          <button
            onClick={() => handleGenerate('generate/code', { count: 50 })}
            disabled={loading['generate/code']}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            {loading['generate/code'] ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Code className="w-5 h-5" />
            )}
            <span>Code (50)</span>
          </button>

          <button
            onClick={() => handleGenerate('generate/darkweb', { count: 30 })}
            disabled={loading['generate/darkweb']}
            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            {loading['generate/darkweb'] ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Shield className="w-5 h-5" />
            )}
            <span>Dark Web (30)</span>
          </button>
        </div>
      </div>

      {/* Attack Scenarios */}
      {scenarios.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Attack Scenarios</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {scenarios.map((scenario) => (
              <button
                key={scenario}
                onClick={() => handleGenerate(`scenario/${scenario}`, { duration: 300 })}
                disabled={loading[`scenario/${scenario}`]}
                className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
              >
                {loading[`scenario/${scenario}`] ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                <span className="capitalize">{scenario.replace(/_/g, ' ')}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Active Generators */}
      {activeGenerators.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Active Generators</h3>
          <div className="space-y-2">
            {activeGenerators.map((gen) => (
              <div
                key={gen.id}
                className="bg-gray-700 rounded-lg p-4 flex items-center justify-between"
              >
                <div>
                  <div className="font-semibold">{gen.id}</div>
                  <div className="text-sm text-gray-400">PID: {gen.pid}</div>
                </div>
                <button
                  onClick={() => handleStop(gen.id)}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                  <Square className="w-4 h-4" />
                  <span>Stop</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

