"""
Formal Sandbox - Isolated execution environment for attack testing.

CRITICAL: Production deployments MUST sandbox attack execution to prevent:
- Code execution vulnerabilities
- Network attacks
- Resource exhaustion
- Data exfiltration
"""

import docker
import tempfile
import json
from typing import Any, Dict, Optional
from datetime import datetime
import logging

from .base import PurpleAgent
from .models import Attack, TestResult, TestOutcome, create_result_id


class FormalSandbox:
    """
    Isolated execution environment using Docker containers.

    Security layers:
    1. Container isolation (separate kernel namespace)
    2. seccomp profile (syscall filtering)
    3. Network policies (no external access)
    4. Resource limits (CPU, memory, time)
    5. Read-only filesystem (except /tmp)
    """

    def __init__(
        self,
        image: str = 'python:3.10-slim',
        cpu_limit: float = 0.5,  # 0.5 CPUs
        memory_limit: str = '512m',
        timeout_seconds: int = 30,
        enable_network: bool = False
    ):
        """
        Initialize sandbox.

        Args:
            image: Docker image to use
            cpu_limit: CPU limit (fraction of CPU)
            memory_limit: Memory limit (e.g., '512m', '1g')
            timeout_seconds: Maximum execution time
            enable_network: Whether to allow network access (default: False)
        """
        self.image = image
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.timeout_seconds = timeout_seconds
        self.enable_network = enable_network
        self.logger = logging.getLogger("FormalSandbox")

        # Initialize Docker client
        try:
            self.client = docker.from_env()
            # Pull image if not exists
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                self.logger.info(f"Pulling image {image}...")
                self.client.images.pull(image)
        except Exception as e:
            self.logger.error(f"Docker initialization failed: {e}")
            raise RuntimeError(f"Docker not available: {e}")

    def execute_attack(
        self,
        attack: Attack,
        purple_agent_code: str,
        purple_agent_function: str = 'detect'
    ) -> TestResult:
        """
        Execute attack in sandboxed environment.

        Args:
            attack: Attack to execute
            purple_agent_code: Python code for purple agent
            purple_agent_function: Function name to call

        Returns:
            Test result
        """
        self.logger.info(f"Executing attack {attack.attack_id} in sandbox")

        # Create execution script
        script = self._create_execution_script(
            attack=attack,
            purple_agent_code=purple_agent_code,
            purple_agent_function=purple_agent_function
        )

        # Execute in container
        try:
            result = self._run_in_container(script, attack.attack_id)

            # Parse result
            test_result = self._parse_result(result, attack)
            return test_result

        except Exception as e:
            self.logger.error(f"Sandbox execution failed: {e}")

            # Return error result
            return TestResult(
                result_id=create_result_id(attack.attack_id, 'sandbox', datetime.now()),
                attack_id=attack.attack_id,
                purple_agent='sandbox_error',
                detected=False,
                confidence=0.0,
                detection_reason=f"Sandbox error: {e}",
                outcome=TestOutcome.FALSE_NEGATIVE  # Conservative: assume evasion
            )

    def _create_execution_script(
        self,
        attack: Attack,
        purple_agent_code: str,
        purple_agent_function: str
    ) -> str:
        """Create Python script for sandbox execution."""

        script = f"""
import json
import sys
from datetime import datetime

# Purple agent code
{purple_agent_code}

# Attack payload
attack_data = {json.dumps({
    'attack_id': attack.attack_id,
    'technique': attack.technique,
    'payload': attack.payload,
    'metadata': attack.metadata
})}

try:
    # Execute detection
    start_time = datetime.now()
    result = {purple_agent_function}(attack_data['payload'])
    end_time = datetime.now()

    # Format result
    output = {{
        'detected': result.get('is_vulnerable', False),
        'confidence': result.get('confidence', 0.5),
        'detection_reason': result.get('explanation', ''),
        'latency_ms': (end_time - start_time).total_seconds() * 1000,
        'error': None
    }}

except Exception as e:
    output = {{
        'detected': False,
        'confidence': 0.0,
        'detection_reason': f'Detection failed: {{str(e)}}',
        'latency_ms': 0.0,
        'error': str(e)
    }}

# Output result as JSON
print(json.dumps(output))
"""

        return script

    def _run_in_container(self, script: str, attack_id: str) -> Dict[str, Any]:
        """
        Run script in isolated container.

        Args:
            script: Python script to execute
            attack_id: Attack ID (for logging)

        Returns:
            Execution result dictionary
        """
        # Create temporary file with script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name

        try:
            # Write seccomp profile to temp file
            import tempfile
            import json
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as seccomp_file:
                json.dump(SECCOMP_PROFILE, seccomp_file)
                seccomp_path = seccomp_file.name

            # Container configuration
            container_config = {
                'image': self.image,
                'command': ['python', '/script/test.py'],
                'volumes': {
                    script_path: {'bind': '/script/test.py', 'mode': 'ro'},
                    seccomp_path: {'bind': '/seccomp.json', 'mode': 'ro'}
                },
                'network_mode': 'none' if not self.enable_network else 'bridge',
                'mem_limit': self.memory_limit,
                'nano_cpus': int(self.cpu_limit * 1e9),
                'read_only': True,
                'tmpfs': {'/tmp': 'rw,size=100m'},
                'detach': True,
                'remove': True,

                # Security options
                'security_opt': [
                    'no-new-privileges',
                    f'seccomp=/seccomp.json'  # Apply custom seccomp profile
                ],
                'cap_drop': ['ALL'],  # Drop all capabilities
                'cap_add': ['CHOWN', 'SETUID', 'SETGID'],  # Only essentials for Python

                # Additional isolation
                'pids_limit': 100,  # Limit number of processes
                'ulimits': [
                    docker.types.Ulimit(name='nofile', soft=1024, hard=1024),  # File descriptors
                    docker.types.Ulimit(name='nproc', soft=100, hard=100)  # Processes
                ]
            }

            # Run container
            container = self.client.containers.run(**container_config)

            # Wait for completion (with timeout)
            try:
                exit_code = container.wait(timeout=self.timeout_seconds)
                logs = container.logs().decode('utf-8')

                # Parse JSON output
                try:
                    result = json.loads(logs.strip().split('\n')[-1])
                    return result
                except json.JSONDecodeError:
                    return {
                        'detected': False,
                        'confidence': 0.0,
                        'detection_reason': f'Invalid output: {logs}',
                        'error': 'JSON parse error'
                    }

            except docker.errors.ContainerError as e:
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'detection_reason': f'Container error: {e}',
                    'error': str(e)
                }

        finally:
            # Cleanup
            import os
            try:
                os.unlink(script_path)
            except:
                pass
            try:
                os.unlink(seccomp_path)
            except:
                pass

    def _parse_result(self, result: Dict[str, Any], attack: Attack) -> TestResult:
        """Parse sandbox result into TestResult."""

        detected = result.get('detected', False)

        # Calculate outcome
        if attack.is_malicious:
            outcome = TestOutcome.TRUE_POSITIVE if detected else TestOutcome.FALSE_NEGATIVE
        else:
            outcome = TestOutcome.FALSE_POSITIVE if detected else TestOutcome.TRUE_NEGATIVE

        return TestResult(
            result_id=create_result_id(attack.attack_id, 'sandbox', datetime.now()),
            attack_id=attack.attack_id,
            purple_agent='sandboxed',
            detected=detected,
            confidence=result.get('confidence', 0.5),
            detection_reason=result.get('detection_reason', ''),
            outcome=outcome,
            latency_ms=result.get('latency_ms', 0.0),
            metadata={'sandbox_error': result.get('error')}
        )


class SandboxedPurpleAgent:
    """
    Wrapper that runs any purple agent in sandbox.
    """

    def __init__(self, purple_agent: PurpleAgent, sandbox: FormalSandbox):
        """
        Initialize sandboxed wrapper.

        Args:
            purple_agent: Purple agent to wrap
            sandbox: Sandbox instance
        """
        self.purple_agent = purple_agent
        self.sandbox = sandbox
        self.name = f"{purple_agent.get_name()}_sandboxed"

    def detect(self, attack: Attack) -> TestResult:
        """Execute detection in sandbox."""

        # Extract purple agent code
        # TODO: Serialize purple agent to code string
        purple_agent_code = self._serialize_purple_agent()

        # Execute in sandbox
        result = self.sandbox.execute_attack(
            attack=attack,
            purple_agent_code=purple_agent_code
        )

        return result

    def _serialize_purple_agent(self) -> str:
        """
        Serialize purple agent to executable code.

        Supports:
        - Pattern-based detectors (SimplePatternPurpleAgent)
        - Function-based detectors (callable with dict return)
        - Custom detectors (with detect() method)
        """
        from ..scenarios.sql_injection import SimplePatternPurpleAgent
        import inspect
        import base64
        import pickle

        # Type 1: SimplePatternPurpleAgent (pattern-based)
        if isinstance(self.purple_agent, SimplePatternPurpleAgent):
            patterns = self.purple_agent.patterns
            code = f"""
import json

def detect(payload):
    '''Pattern-based SQL injection detector.'''
    patterns = {patterns}

    payload_upper = str(payload).upper()
    detected_patterns = []

    for pattern in patterns:
        if pattern.upper() in payload_upper:
            detected_patterns.append(pattern)

    is_vulnerable = len(detected_patterns) > 0
    confidence = min(1.0, len(detected_patterns) * 0.3)

    return {{
        'is_vulnerable': is_vulnerable,
        'confidence': confidence,
        'explanation': f'Detected patterns: {{detected_patterns}}' if detected_patterns else 'No patterns detected',
        'patterns': detected_patterns
    }}
"""
            return code

        # Type 2: Callable with dict return
        elif callable(getattr(self.purple_agent, 'detector_function', None)):
            # Extract function source
            try:
                func = self.purple_agent.detector_function
                source = inspect.getsource(func)

                code = f"""
{source}

def detect(payload):
    return detector_function(payload)
"""
                return code
            except:
                pass

        # Type 3: Custom detector with detect() method
        elif hasattr(self.purple_agent, 'detect'):
            # Try to serialize the entire class
            try:
                # Get class source
                source = inspect.getsource(self.purple_agent.__class__)

                # Serialize instance state
                state = self.purple_agent.__dict__
                state_b64 = base64.b64encode(pickle.dumps(state)).decode('ascii')

                code = f"""
import base64
import pickle

# Purple agent class
{source}

# Restore state
state = pickle.loads(base64.b64decode('{state_b64}'))
agent = {self.purple_agent.__class__.__name__}.__new__({self.purple_agent.__class__.__name__})
agent.__dict__.update(state)

def detect(payload):
    from datetime import datetime
    # Create minimal attack object
    class Attack:
        def __init__(self, payload):
            self.attack_id = 'sandbox_test'
            self.scenario = 'test'
            self.technique = 'test'
            self.payload = payload
            self.metadata = {{}}
            self.is_malicious = True

    attack = Attack(payload)
    result = agent.detect(attack)

    return {{
        'is_vulnerable': result.detected,
        'confidence': result.confidence,
        'explanation': result.detection_reason or ''
    }}
"""
                return code
            except Exception as e:
                raise NotImplementedError(f"Cannot serialize purple agent of type {type(self.purple_agent)}: {e}")

        # Fallback: Generic pattern matching
        code = """
def detect(payload):
    '''Fallback generic detector.'''
    dangerous_patterns = ["'", '"', ';', '--', '/*', '*/', 'UNION', 'SELECT', 'DROP', 'INSERT', 'UPDATE', 'DELETE']

    payload_upper = str(payload).upper()
    detected = any(pattern.upper() in payload_upper for pattern in dangerous_patterns)

    return {
        'is_vulnerable': detected,
        'confidence': 0.5,
        'explanation': 'Generic pattern matching (fallback)'
    }
"""
        return code

    def get_name(self) -> str:
        return self.name

    def reset(self):
        self.purple_agent.reset()


# Custom seccomp profile for secure sandbox
SECCOMP_PROFILE = {
    "defaultAction": "SCMP_ACT_ERRNO",
    "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86", "SCMP_ARCH_X32"],
    "syscalls": [
        # Essential I/O syscalls
        {
            "names": [
                "read", "write", "open", "openat", "close",
                "stat", "fstat", "lstat", "stat64", "fstat64", "lstat64",
                "access", "faccessat", "readlink", "readlinkat"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # Memory management
        {
            "names": [
                "mmap", "mmap2", "munmap", "mprotect", "brk",
                "mremap", "madvise", "mbind"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # Process management (safe subset)
        {
            "names": [
                "exit", "exit_group", "wait4", "waitpid",
                "getpid", "getppid", "getuid", "getgid",
                "geteuid", "getegid", "getgroups"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # Python runtime essentials
        {
            "names": [
                "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
                "sigaltstack", "getcwd", "chdir", "fchdir",
                "getdents", "getdents64", "ioctl", "fcntl", "fcntl64",
                "poll", "select", "pselect6", "ppoll", "epoll_create",
                "epoll_wait", "epoll_ctl"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # Time operations
        {
            "names": [
                "time", "gettimeofday", "clock_gettime", "clock_getres",
                "nanosleep", "clock_nanosleep"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # File metadata
        {
            "names": [
                "umask", "chmod", "fchmod", "fchmodat",
                "utime", "utimes", "futimesat", "utimensat"
            ],
            "action": "SCMP_ACT_ALLOW"
        },
        # BLOCK: Network operations
        {
            "names": [
                "socket", "socketpair", "connect", "bind", "listen", "accept", "accept4",
                "sendto", "recvfrom", "sendmsg", "recvmsg", "shutdown",
                "getsockname", "getpeername", "getsockopt", "setsockopt"
            ],
            "action": "SCMP_ACT_ERRNO"
        },
        # BLOCK: Process creation/execution
        {
            "names": [
                "execve", "execveat", "fork", "vfork", "clone", "clone3"
            ],
            "action": "SCMP_ACT_ERRNO"
        },
        # BLOCK: Dangerous operations
        {
            "names": [
                "ptrace", "process_vm_readv", "process_vm_writev",
                "personality", "unshare", "mount", "umount", "umount2",
                "pivot_root", "chroot", "reboot", "swapon", "swapoff",
                "init_module", "delete_module", "iopl", "ioperm",
                "create_module", "get_kernel_syms", "query_module"
            ],
            "action": "SCMP_ACT_ERRNO"
        }
    ]
}
