import time
from typing import Dict, List
from datetime import datetime, timezone
from urllib.parse import quote

try:
    import requests as req_lib
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from curl_cffi import requests as curl_req
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

from engines.evasion import EvasionEngine
from utils.colors import info, success

class FirewallBypassEngine:
    """Main engine for executing bypass attempts."""
    def __init__(self, target: str, port: int = 80, use_curl: bool = False):
        self.target = target
        self.port = port
        self.use_curl = use_curl
        self.session = None
        self.results = []

    def initialize_session(self):
        """Initialize HTTP session with evasion capabilities."""
        if self.use_curl and HAS_CURL_CFFI:
            self.session = curl_req.Session()
            self.session.impersonate = "chrome120"
        elif HAS_REQUESTS:
            self.session = req_lib.Session()
        else:
            raise ImportError("No HTTP library available")
        # Set evasion headers
        self.session.headers.update(EvasionEngine.polymorphic_headers())
        self.session.verify = False
        # Disable warnings
        if HAS_REQUESTS:
            req_lib.packages.urllib3.disable_warnings()

    def execute_bypass(self, payload: str, method: str = "GET",
                       custom_headers: Dict = None) -> Dict:
        """Execute single bypass attempt."""
        if not self.session:
            self.initialize_session()
        protocol = "https" if self.port == 443 else "http"
        url = f"{protocol}://{self.target}:{self.port}/"
        headers = EvasionEngine.polymorphic_headers()
        if custom_headers:
            headers.update(custom_headers)
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'payload': payload[:100] + '...' if len(payload) > 100 else payload,
            'method': method,
            'status': None,
            'success': False,
            'response_size': 0,
        }
        try:
            if method == "GET":
                # Inject payload in query parameters
                sep = '?' if '?' not in url else '&'
                test_url = f"{url}{sep}q={quote(payload)}&id=1"
                response = self.session.get(
                    test_url, headers=headers, timeout=30)
            else:
                # POST with payload in body
                response = self.session.post(
                    url, data={'q': payload}, headers=headers, timeout=30)
            result['status'] = response.status_code
            result['response_size'] = len(response.text)
            # Determine success (200-299 or 403 with specific patterns)
            if 200 <= response.status_code < 300:
                result['success'] = True
            elif response.status_code == 403 and 'blocked' not in response.text.lower():
                result['success'] = True  # 403 but not blocked by WAF
        except Exception as e:
            result['error'] = str(e)
            # Connection errors might indicate successful bypass (WAF dropped connection)
            if 'connection' in str(e).lower() or 'timeout' in str(e).lower():
                result['success'] = True
                result['status'] = 'DROPPED'
        return result

    def run_bypass_campaign(self, payloads: List[str], method: str = "GET",
                            delay: float = 0.1) -> List[Dict]:
        """Run comprehensive bypass campaign."""
        info(f"Starting bypass campaign against {self.target}:{self.port}")
        info(f"Total payloads: {len(payloads)}")
        successful_bypasses = []
        for i, payload in enumerate(payloads):
            # Apply dynamic adaptation
            if i > 0 and i % 10 == 0:
                # Re-initialize session periodically
                self.initialize_session()
            result = self.execute_bypass(payload, method)
            self.results.append(result)
            if result['success']:
                successful_bypasses.append(result)
                success(
                    f"Bypass #{len(successful_bypasses)}: {result['payload']}")
            # Rate limiting
            if delay > 0:
                time.sleep(delay)
        return successful_bypasses
