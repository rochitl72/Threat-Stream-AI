'use client';

import { useEffect, useState } from 'react';

interface MITREMatrixProps {}

// Map tactic IDs to display names
const TACTIC_DISPLAY_NAMES: Record<string, string> = {
  'TA0001-AI': 'AI MODEL ACCESS',
  'TA0002-AI': 'AI MODEL EXPLOITATION',
  'TA0003-AI': 'AI MODEL POISONING',
  'TA0005-AI': 'ADVERSARIAL EXAMPLES',
  'TA0001': 'INITIAL ACCESS',
  'TA0002': 'EXECUTION',
  'TA0003': 'PERSISTENCE',
  'TA0004': 'PRIVILEGE ESCALATION',
  'TA0005': 'DEFENSE EVASION',
  'TA0006': 'CREDENTIAL ACCESS',
  'TA0007': 'DISCOVERY',
  'TA0008': 'LATERAL MOVEMENT',
  'TA0009': 'COLLECTION',
  'TA0010': 'EXFILTRATION',
  'TA0011': 'COMMAND AND CONTROL',
  'TA0040': 'IMPACT',
};

export default function MITREMatrix({}: MITREMatrixProps) {
  const [matrix, setMatrix] = useState<any>(null);
  const [selectedTactic, setSelectedTactic] = useState<string | null>(null);

  useEffect(() => {
    // Fetch MITRE matrix data
    const fetchMatrix = () => {
      fetch('/api/mitre/matrix')
        .then((res) => res.json())
        .then((data) => setMatrix(data))
        .catch((err) => console.error('Error fetching MITRE matrix:', err));
    };

    fetchMatrix();
    // Refresh every 5 seconds
    const interval = setInterval(fetchMatrix, 5000);
    return () => clearInterval(interval);
  }, []);

  // Get AI-specific tactics from API or use defaults
  const tactics = matrix?.tactics?.filter((t: string) => t.includes('-AI')) || [
    'TA0001-AI',
    'TA0002-AI',
    'TA0003-AI',
    'TA0005-AI',
  ];

  const techniques = [
    'T0001 - Model Theft',
    'T0002 - Adversarial Examples',
    'T0003 - Data Poisoning',
    'T0004 - Model Inversion',
    'T0005 - Autonomous Propagation',
  ];

  return (
    <div className="space-y-4">
      {/* Matrix Grid */}
      <div className="bg-gray-700 rounded-lg p-4">
        <div className="text-sm font-semibold mb-4">MITRE ATT&CK for AI Matrix</div>
        <div className="grid grid-cols-5 gap-2">
          {tactics.map((tactic) => (
            <div
              key={tactic}
              className={`p-3 rounded-lg cursor-pointer transition-all ${
                selectedTactic === tactic
                  ? 'bg-blue-600 border-2 border-blue-400'
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
              onClick={() => setSelectedTactic(tactic === selectedTactic ? null : tactic)}
            >
              <div className="text-xs font-semibold text-center">
                {TACTIC_DISPLAY_NAMES[tactic] || tactic.replace(/_/g, ' ')}
              </div>
              {matrix?.mapping_counts?.[tactic] && (
                <div className="text-center mt-2 text-lg font-bold text-yellow-400">
                  {matrix.mapping_counts[tactic]}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Tactic Details */}
      {selectedTactic && (
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-lg font-semibold mb-3">
            {TACTIC_DISPLAY_NAMES[selectedTactic] || selectedTactic.replace(/_/g, ' ')} - Techniques
          </div>
          <div className="space-y-2">
            {techniques.map((technique) => (
              <div
                key={technique}
                className="bg-gray-600 rounded p-2 text-sm hover:bg-gray-500 cursor-pointer"
              >
                {technique}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Mappings</div>
          <div className="text-2xl font-bold">
            {matrix?.total_mappings || 0}
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Active Tactics</div>
          <div className="text-2xl font-bold">
            {matrix?.mapping_counts ? Object.keys(matrix.mapping_counts).length : 0}
          </div>
        </div>
        <div className="bg-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">AI-Specific</div>
          <div className="text-2xl font-bold text-purple-400">Yes</div>
        </div>
      </div>
    </div>
  );
}

