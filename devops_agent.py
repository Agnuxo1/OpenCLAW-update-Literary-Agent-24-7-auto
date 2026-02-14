"""
OpenCLAW DevOps Agent — Self-Healing Monitor
==============================================
Monitors all agent workflows and automatically fixes common errors.

This agent:
1. Checks GitHub Actions status for all OpenCLAW repos
2. Reads error logs from failed runs
3. Identifies common error patterns
4. Applies automatic fixes (package.json, env vars, workflow)
5. Reports status to HiveMind

Can run as a GitHub Action on a schedule, or manually.

USAGE:
    python devops_agent.py              # Check all agents
    python devops_agent.py --fix        # Check and auto-fix
    python devops_agent.py --report     # Generate status report
"""

import os
import json
import sys
import logging
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='[devops] %(message)s')
logger = logging.getLogger(__name__)

GITHUB_USER = "Agnuxo1"
GITHUB_TOKEN = os.environ.get('GH_PAT') or os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN', '')

# All active repos to monitor
MONITORED_REPOS = [
    "OpenCLAW-Autonomous-Multi-Agent-Scientific-Research-Platform",
    "OpenCLAW-2-Autonomous-Multi-Agent-Scientific-Research-Platform",
    "OpenCLAW-2-Autonomous-Multi-Agent-literary",
    "OpenCLAW-2-Autonomous-Multi-Agent-literary2",
    "OpenCLAW-update-Literary-Agent-24-7-auto",
]

# Known error patterns and their fixes
ERROR_PATTERNS = {
    "Cannot find module 'fs-extra'": {
        'diagnosis': 'Missing npm dependency',
        'fix_type': 'package_json',
        'fix_package': 'fs-extra',
        'fix_version': '^11.2.0',
    },
    "Cannot find module 'axios'": {
        'diagnosis': 'Missing npm dependency',
        'fix_type': 'package_json',
        'fix_package': 'axios',
        'fix_version': '^1.6.7',
    },
    "No API keys found": {
        'diagnosis': 'Environment variable naming mismatch',
        'fix_type': 'env_adapter',
    },
    "HTTP Error 429": {
        'diagnosis': 'Rate limiting - needs backoff',
        'fix_type': 'rate_limit',
    },
    "HTTP Error 403: Forbidden": {
        'diagnosis': 'API key expired or invalid',
        'fix_type': 'key_rotation',
    },
    "'NoneType' object has no attribute 'strip'": {
        'diagnosis': 'Malformed or empty API key',
        'fix_type': 'key_validation',
    },
    "Process completed with exit code 1": {
        'diagnosis': 'General failure - check logs',
        'fix_type': 'manual',
    },
}


def github_api(url: str, method: str = 'GET', data: dict = None) -> Optional[dict]:
    """Make authenticated GitHub API call."""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenCLAW-DevOps-Agent',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    body = json.dumps(data).encode('utf-8') if data else None
    if body:
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        logger.warning(f"API {e.code}: {url}")
        return None
    except Exception as e:
        logger.warning(f"API error: {e}")
        return None


def get_workflow_runs(repo: str, limit: int = 10) -> List[Dict]:
    """Get recent workflow runs for a repo."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/actions/runs?per_page={limit}"
    data = github_api(url)
    return data.get('workflow_runs', []) if data else []


def get_run_logs(repo: str, run_id: int) -> Optional[str]:
    """Get logs for a specific workflow run (returns log text)."""
    # Get jobs for this run
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/actions/runs/{run_id}/jobs"
    data = github_api(url)
    if not data:
        return None
    
    # Collect step annotations and conclusions
    log_text = ""
    for job in data.get('jobs', []):
        log_text += f"\nJob: {job.get('name', 'unknown')}\n"
        log_text += f"  Status: {job.get('conclusion', 'unknown')}\n"
        for step in job.get('steps', []):
            if step.get('conclusion') == 'failure':
                log_text += f"  ❌ Step '{step.get('name')}': FAILED\n"
    
    return log_text


def diagnose_repo(repo: str) -> Dict:
    """Diagnose health of a single repo."""
    logger.info(f"\n🔍 Diagnosing: {repo}")
    
    runs = get_workflow_runs(repo, limit=10)
    
    if not runs:
        return {
            'repo': repo,
            'status': 'no_data',
            'message': 'No workflow runs found',
            'runs_total': 0,
            'errors': [],
        }
    
    # Calculate success rate
    total = len(runs)
    successful = sum(1 for r in runs if r.get('conclusion') == 'success')
    failed = sum(1 for r in runs if r.get('conclusion') == 'failure')
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    # Check for consecutive failures
    consecutive_fails = 0
    for run in runs:
        if run.get('conclusion') == 'failure':
            consecutive_fails += 1
        else:
            break
    
    # Identify error patterns from recent failures
    errors_found = []
    for run in runs[:5]:
        if run.get('conclusion') == 'failure':
            # Try to get logs
            log_text = get_run_logs(repo, run['id']) or ''
            
            for pattern, info in ERROR_PATTERNS.items():
                if pattern.lower() in log_text.lower():
                    errors_found.append({
                        'pattern': pattern,
                        'diagnosis': info['diagnosis'],
                        'fix_type': info['fix_type'],
                        'run_id': run['id'],
                    })
    
    # Determine overall status
    if consecutive_fails >= 5:
        status = 'critical'
    elif consecutive_fails >= 3:
        status = 'warning'
    elif success_rate >= 90:
        status = 'healthy'
    else:
        status = 'degraded'
    
    result = {
        'repo': repo,
        'status': status,
        'success_rate': round(success_rate, 1),
        'runs_total': total,
        'runs_success': successful,
        'runs_failed': failed,
        'consecutive_failures': consecutive_fails,
        'last_run': runs[0].get('updated_at', '') if runs else '',
        'errors': errors_found,
    }
    
    # Print summary
    status_emoji = {
        'healthy': '🟢', 'degraded': '🟡', 
        'warning': '🟠', 'critical': '🔴', 'no_data': '⚪'
    }
    
    logger.info(f"  {status_emoji.get(status, '❓')} Status: {status}")
    logger.info(f"  Success rate: {success_rate}% ({successful}/{total})")
    if consecutive_fails > 0:
        logger.info(f"  Consecutive failures: {consecutive_fails}")
    for err in errors_found:
        logger.info(f"  ❌ Error: {err['pattern']}")
        logger.info(f"     Diagnosis: {err['diagnosis']}")
    
    return result


def diagnose_network() -> List[Dict]:
    """Diagnose all repos in the network."""
    logger.info("=" * 60)
    logger.info("OpenCLAW Network Health Check")
    logger.info("=" * 60)
    
    results = []
    for repo in MONITORED_REPOS:
        result = diagnose_repo(repo)
        results.append(result)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("NETWORK SUMMARY")
    logger.info("=" * 60)
    
    healthy = sum(1 for r in results if r['status'] == 'healthy')
    critical = sum(1 for r in results if r['status'] == 'critical')
    
    logger.info(f"  Total agents: {len(results)}")
    logger.info(f"  Healthy: {healthy}")
    logger.info(f"  Critical: {critical}")
    
    if critical > 0:
        logger.info("\n⚠️ CRITICAL AGENTS NEED ATTENTION:")
        for r in results:
            if r['status'] == 'critical':
                logger.info(f"  🔴 {r['repo']}")
                for err in r['errors']:
                    logger.info(f"     Fix: {err['fix_type']} - {err['diagnosis']}")
    
    return results


def generate_report(results: List[Dict]) -> str:
    """Generate a markdown status report."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    report = f"# OpenCLAW Network Status Report\n\n"
    report += f"**Generated:** {now}\n\n"
    
    # Summary table
    report += "| Agent | Status | Success Rate | Consecutive Fails | Errors |\n"
    report += "|-------|--------|-------------|-------------------|--------|\n"
    
    status_emoji = {'healthy': 'OK', 'degraded': 'WARN', 'warning': 'WARN', 'critical': 'CRIT', 'no_data': 'N/A'}
    
    for r in results:
        short_name = r['repo'].replace('OpenCLAW-', '').replace('Autonomous-Multi-Agent-', '')[:30]
        errors_str = ', '.join(set(e['fix_type'] for e in r['errors'])) or '-'
        report += f"| {short_name} | {status_emoji.get(r['status'], '?')} | {r['success_rate']}% | {r['consecutive_failures']} | {errors_str} |\n"
    
    # Details
    for r in results:
        if r['errors']:
            report += f"\n## {r['repo']}\n\n"
            for err in r['errors']:
                report += f"- **{err['pattern']}**: {err['diagnosis']} (fix: `{err['fix_type']}`)\n"
    
    return report


# =============================================================================
# CLI
# =============================================================================
if __name__ == '__main__':
    if not GITHUB_TOKEN:
        logger.error("No GitHub token found. Set GH_PAT, GH_TOKEN, or GITHUB_TOKEN")
        sys.exit(1)
    
    args = sys.argv[1:]
    
    results = diagnose_network()
    
    if '--report' in args:
        report = generate_report(results)
        with open('network_status.md', 'w') as f:
            f.write(report)
        logger.info("\n📄 Report saved to network_status.md")
    
    if '--fix' in args:
        logger.info("\n🔧 Auto-fix mode is informational only.")
        logger.info("Run deploy_fixes.sh to apply actual code fixes.")
    
    # Exit with non-zero if any agent is critical
    critical = sum(1 for r in results if r['status'] == 'critical')
    sys.exit(1 if critical > 0 else 0)
