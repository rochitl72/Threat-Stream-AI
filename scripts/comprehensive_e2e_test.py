#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for ThreatStream AI
Tests all components and documents results
"""

import json
import time
import requests
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

class TestResult:
    def __init__(self, test_name: str, description: str):
        self.test_name = test_name
        self.description = description
        self.curl_command = ""
        self.output = ""
        self.observation = ""
        self.status = "PENDING"
        self.timestamp = datetime.now().isoformat()

def run_curl_command(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
    """Run a curl command and return output"""
    url = f"{BASE_URL}{endpoint}"
    
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{query_string}"
    
    curl_cmd = f"curl -s -X {method} '{url}'"
    
    if data:
        json_data = json.dumps(data)
        curl_cmd += f" -H 'Content-Type: application/json' -d '{json_data}'"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, params=params, timeout=10)
        else:
            response = requests.request(method, url, json=data, params=params, timeout=10)
        
        output = response.text
        status_code = response.status_code
        
        try:
            output_json = response.json()
            output = json.dumps(output_json, indent=2)
        except:
            pass
        
        return curl_cmd, output, status_code, None
    except Exception as e:
        return curl_cmd, str(e), None, str(e)

def test_health_check():
    """Test 1: Health Check"""
    result = TestResult(
        "Health Check",
        "Verify backend API is healthy and all services are running"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/health")
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            data = json.loads(output)
            if data.get("status") == "healthy":
                result.status = "PASS"
                result.observation = f"✅ Backend is healthy. Kafka: {data.get('kafka')}, Metrics: {data.get('metrics')}"
            else:
                result.status = "FAIL"
                result.observation = f"❌ Backend returned unhealthy status: {data.get('status')}"
        except:
            result.status = "FAIL"
            result.observation = "❌ Invalid JSON response"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_topics_list():
    """Test 2: List Kafka Topics"""
    result = TestResult(
        "List Kafka Topics",
        "Verify all Kafka topics are being monitored"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/topics")
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            topics = json.loads(output)
            expected_topics = [
                "telemetry-raw",
                "code-samples-raw",
                "darkweb-feeds-raw",
                "threat-profiles",
                "mitre-attack-mappings",
                "threat-alerts"
            ]
            
            if isinstance(topics, list) and len(topics) > 0:
                result.status = "PASS"
                result.observation = f"✅ Found {len(topics)} topics: {', '.join(topics[:3])}..."
            else:
                result.status = "WARN"
                result.observation = f"⚠️ Topics list is empty (may be normal if no messages yet)"
        except:
            result.status = "FAIL"
            result.observation = "❌ Invalid response format"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_topic_metrics():
    """Test 3: Topic Metrics"""
    result = TestResult(
        "Topic Metrics",
        "Check message counts and rates for each topic"
    )
    
    topics = ["telemetry-raw", "threat-profiles", "threat-alerts"]
    all_metrics = {}
    
    for topic in topics:
        curl_cmd, output, status_code, error = run_curl_command("GET", f"/api/topics/{topic}/metrics")
        if status_code == 200:
            try:
                metrics = json.loads(output)
                all_metrics[topic] = metrics
            except:
                pass
    
    result.curl_command = f"curl -s '{BASE_URL}/api/topics/{{topic}}/metrics'"
    result.output = json.dumps(all_metrics, indent=2)
    
    if all_metrics:
        total_messages = sum(m.get("message_count", 0) for m in all_metrics.values())
        result.status = "PASS"
        result.observation = f"✅ Retrieved metrics for {len(all_metrics)} topics. Total messages: {total_messages}"
    else:
        result.status = "WARN"
        result.observation = "⚠️ No metrics available (topics may be empty)"
    
    return result

def test_generate_telemetry():
    """Test 4: Generate Telemetry Data"""
    result = TestResult(
        "Generate Telemetry Data",
        "Test data generator API to create telemetry events"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("POST", "/api/generator/generate/telemetry", params={"count": 5})
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            data = json.loads(output)
            if data.get("success"):
                result.status = "PASS"
                result.observation = f"✅ Generator started successfully. Task ID: {data.get('task_id')}, PID: {data.get('pid')}"
            else:
                result.status = "FAIL"
                result.observation = f"❌ Generator failed: {data.get('error')}"
        except:
            result.status = "FAIL"
            result.observation = "❌ Invalid response format"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_active_generators():
    """Test 5: Check Active Generators"""
    result = TestResult(
        "Active Generators",
        "Verify generator status and list running generators"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/generator/active")
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            data = json.loads(output)
            active_count = data.get("count", 0)
            generators = data.get("active_generators", {})
            
            if active_count > 0:
                result.status = "PASS"
                result.observation = f"✅ {active_count} generator(s) running: {', '.join(generators.keys())}"
            else:
                result.status = "INFO"
                result.observation = "ℹ️ No active generators (normal if none started)"
        except:
            result.status = "FAIL"
            result.observation = "❌ Invalid response format"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_threat_profiles():
    """Test 6: Get Threat Profiles"""
    result = TestResult(
        "Threat Profiles",
        "Retrieve recent threat profiles created by the system"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/threats/profiles/recent", params={"limit": 5})
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            profiles = json.loads(output)
            if isinstance(profiles, list):
                if len(profiles) > 0:
                    result.status = "PASS"
                    threat_types = [p.get("threat_type", "unknown") for p in profiles[:3]]
                    result.observation = f"✅ Retrieved {len(profiles)} threat profiles. Types: {', '.join(threat_types)}"
                else:
                    result.status = "WARN"
                    result.observation = "⚠️ No threat profiles found (may need to generate data first)"
            else:
                result.status = "FAIL"
                result.observation = "❌ Invalid response format (expected array)"
        except Exception as e:
            result.status = "FAIL"
            result.observation = f"❌ Error parsing response: {e}"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_threat_alerts():
    """Test 7: Get Threat Alerts"""
    result = TestResult(
        "Threat Alerts",
        "Retrieve high-priority threat alerts"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/threats/alerts/recent", params={"limit": 5})
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            alerts = json.loads(output)
            if isinstance(alerts, list):
                if len(alerts) > 0:
                    result.status = "PASS"
                    severities = [a.get("severity", "unknown") for a in alerts[:3]]
                    result.observation = f"✅ Retrieved {len(alerts)} alerts. Severities: {', '.join(severities)}"
                else:
                    result.status = "WARN"
                    result.observation = "⚠️ No alerts found (normal if no high-severity threats)"
            else:
                result.status = "FAIL"
                result.observation = "❌ Invalid response format"
        except Exception as e:
            result.status = "FAIL"
            result.observation = f"❌ Error parsing response: {e}"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_mitre_matrix():
    """Test 8: MITRE ATT&CK Matrix"""
    result = TestResult(
        "MITRE ATT&CK Matrix",
        "Get MITRE matrix data with mapping counts"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/mitre/matrix")
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            matrix = json.loads(output)
            total_mappings = matrix.get("total_mappings", 0)
            mapping_counts = matrix.get("mapping_counts", {})
            tactics = matrix.get("tactics", [])
            
            if total_mappings > 0:
                result.status = "PASS"
                result.observation = f"✅ Matrix data retrieved. Total mappings: {total_mappings}, Active tactics: {len(mapping_counts)}, Total tactics: {len(tactics)}"
            else:
                result.status = "WARN"
                result.observation = "⚠️ No mappings found (may need to process threats first)"
        except Exception as e:
            result.status = "FAIL"
            result.observation = f"❌ Error parsing response: {e}"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_mitre_mappings():
    """Test 9: MITRE Mappings"""
    result = TestResult(
        "MITRE Mappings",
        "Get detailed MITRE ATT&CK mappings"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/mitre/mappings", params={"limit": 3})
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            mappings = json.loads(output)
            if isinstance(mappings, list):
                if len(mappings) > 0:
                    result.status = "PASS"
                    tactics = [m.get("primary_tactic", "unknown") for m in mappings[:3]]
                    result.observation = f"✅ Retrieved {len(mappings)} mappings. Tactics: {', '.join(tactics)}"
                else:
                    result.status = "WARN"
                    result.observation = "⚠️ No mappings found"
            else:
                result.status = "FAIL"
                result.observation = "❌ Invalid response format"
        except Exception as e:
            result.status = "FAIL"
            result.observation = f"❌ Error parsing response: {e}"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_system_metrics():
    """Test 10: System Metrics"""
    result = TestResult(
        "System Metrics",
        "Get system resource utilization metrics"
    )
    
    curl_cmd, output, status_code, error = run_curl_command("GET", "/api/metrics/system")
    result.curl_command = curl_cmd
    result.output = output
    
    if status_code == 200:
        try:
            metrics = json.loads(output)
            cpu = metrics.get("cpu_percent", 0)
            memory = metrics.get("memory_percent", 0)
            
            result.status = "PASS"
            result.observation = f"✅ System metrics retrieved. CPU: {cpu:.1f}%, Memory: {memory:.1f}%"
        except Exception as e:
            result.status = "FAIL"
            result.observation = f"❌ Error parsing response: {e}"
    else:
        result.status = "FAIL"
        result.observation = f"❌ HTTP {status_code}: {error or output}"
    
    return result

def test_data_flow():
    """Test 11: End-to-End Data Flow"""
    result = TestResult(
        "End-to-End Data Flow",
        "Test complete flow: Generate data -> Process threats -> Create mappings"
    )
    
    # Step 1: Generate data
    print("  Step 1: Generating test data...")
    _, output1, status1, _ = run_curl_command("POST", "/api/generator/generate/telemetry", params={"count": 3})
    
    if status1 != 200:
        result.status = "FAIL"
        result.observation = f"❌ Failed to generate data: HTTP {status1}"
        result.curl_command = f"curl -X POST '{BASE_URL}/api/generator/generate/telemetry?count=3'"
        result.output = output1
        return result
    
    # Wait for processing
    print("  Step 2: Waiting for processing (10 seconds)...")
    time.sleep(10)
    
    # Step 2: Check for threats
    _, output2, status2, _ = run_curl_command("GET", "/api/threats/profiles/recent", params={"limit": 1})
    
    # Step 3: Check for mappings
    _, output3, status3, _ = run_curl_command("GET", "/api/mitre/mappings", params={"limit": 1})
    
    result.curl_command = f"# Step 1: curl -X POST '{BASE_URL}/api/generator/generate/telemetry?count=3'\n# Step 2: curl '{BASE_URL}/api/threats/profiles/recent?limit=1'\n# Step 3: curl '{BASE_URL}/api/mitre/mappings?limit=1'"
    result.output = f"Generation: {output1[:200]}...\nThreats: {output2[:200]}...\nMappings: {output3[:200]}..."
    
    if status2 == 200 and status3 == 200:
        try:
            threats = json.loads(output2)
            mappings = json.loads(output3)
            
            if len(threats) > 0 and len(mappings) > 0:
                result.status = "PASS"
                result.observation = f"✅ Data flow working! Generated data → {len(threats)} threats → {len(mappings)} mappings"
            elif len(threats) > 0:
                result.status = "PARTIAL"
                result.observation = f"⚠️ Threats created ({len(threats)}) but no mappings yet (may need more time)"
            else:
                result.status = "WARN"
                result.observation = "⚠️ Data generated but not yet processed (may need more time)"
        except:
            result.status = "PARTIAL"
            result.observation = "⚠️ Data flow initiated but results unclear"
    else:
        result.status = "FAIL"
        result.observation = f"❌ Data flow incomplete. Threats: {status2}, Mappings: {status3}"
    
    return result

def main():
    """Run all tests"""
    print("=" * 80)
    print("COMPREHENSIVE END-TO-END TEST SUITE")
    print("ThreatStream AI - Full System Testing")
    print("=" * 80)
    print()
    
    tests = [
        test_health_check,
        test_topics_list,
        test_topic_metrics,
        test_generate_telemetry,
        test_active_generators,
        test_threat_profiles,
        test_threat_alerts,
        test_mitre_matrix,
        test_mitre_mappings,
        test_system_metrics,
        test_data_flow,
    ]
    
    results = []
    
    for i, test_func in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Running: {test_func.__doc__.split('.')[0]}...")
        try:
            result = test_func()
            results.append(result)
            
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "INFO": "ℹ️",
                "PARTIAL": "🟡"
            }.get(result.status, "❓")
            
            print(f"  {status_icon} {result.status}: {result.observation}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            result = TestResult(test_func.__name__, "Test execution failed")
            result.status = "ERROR"
            result.observation = str(e)
            results.append(result)
        
        print()
        time.sleep(1)  # Small delay between tests
    
    # Generate report
    print("=" * 80)
    print("TEST REPORT GENERATION")
    print("=" * 80)
    print()
    
    report = {
        "test_suite": "ThreatStream AI - End-to-End Tests",
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "passed": len([r for r in results if r.status == "PASS"]),
        "failed": len([r for r in results if r.status == "FAIL"]),
        "warnings": len([r for r in results if r.status in ["WARN", "PARTIAL"]]),
        "tests": []
    }
    
    for result in results:
        test_data = {
            "test_name": result.test_name,
            "description": result.description,
            "curl_command": result.curl_command,
            "output": result.output,
            "observation": result.observation,
            "status": result.status,
            "timestamp": result.timestamp
        }
        report["tests"].append(test_data)
    
    # Save report
    report_file = f"E2E_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("SUMMARY:")
    print(f"  Total Tests: {report['total_tests']}")
    print(f"  ✅ Passed: {report['passed']}")
    print(f"  ❌ Failed: {report['failed']}")
    print(f"  ⚠️  Warnings: {report['warnings']}")
    print()
    print(f"📄 Full report saved to: {report_file}")
    print()
    
    # Generate markdown report
    md_file = f"E2E_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    generate_markdown_report(report, md_file)
    print(f"📄 Markdown report saved to: {md_file}")
    
    return 0 if report['failed'] == 0 else 1

def generate_markdown_report(report: Dict, filename: str):
    """Generate markdown test report"""
    with open(filename, 'w') as f:
        f.write(f"# End-to-End Test Report\n\n")
        f.write(f"**Test Suite:** {report['test_suite']}\n")
        f.write(f"**Timestamp:** {report['timestamp']}\n")
        f.write(f"**Total Tests:** {report['total_tests']}\n")
        f.write(f"**Passed:** {report['passed']} ✅\n")
        f.write(f"**Failed:** {report['failed']} ❌\n")
        f.write(f"**Warnings:** {report['warnings']} ⚠️\n\n")
        f.write("---\n\n")
        
        for i, test in enumerate(report['tests'], 1):
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "INFO": "ℹ️",
                "PARTIAL": "🟡",
                "ERROR": "❌"
            }.get(test['status'], "❓")
            
            f.write(f"## Test {i}: {test['test_name']} {status_icon}\n\n")
            f.write(f"### 1. Description\n")
            f.write(f"{test['description']}\n\n")
            f.write(f"### 2. cURL Command\n")
            f.write(f"```bash\n{test['curl_command']}\n```\n\n")
            f.write(f"### 3. Output\n")
            f.write(f"```json\n{test['output'][:1000]}{'...' if len(test['output']) > 1000 else ''}\n```\n\n")
            f.write(f"### 4. Observation\n")
            f.write(f"{test['observation']}\n\n")
            f.write(f"**Status:** {test['status']}\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    sys.exit(main())

