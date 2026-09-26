import subprocess
import time
import tempfile
import os

class CodeExecutor:
    def execute(self, code: str, language: str = 'python', timeout: int = 10) -> dict:
        if language != 'python':
            return {
                "code": code,
                "output": "",
                "success": False,
                "error": "Only Python is supported currently.",
                "execution_time": 0
            }
            
        # Basic static analysis to ban imports
        banned_imports = ['os', 'sys', 'subprocess', 'shutil']
        for bi in banned_imports:
            if f"import {bi}" in code or f"from {bi}" in code:
                return {
                    "code": code,
                    "output": "",
                    "success": False,
                    "error": f"Import of {bi} is restricted for security.",
                    "execution_time": 0
                }

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write(code)
            temp_path = f.name

        start_time = time.time()
        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            exec_time = time.time() - start_time
            success = result.returncode == 0
            return {
                "code": code,
                "output": result.stdout if success else result.stderr,
                "success": success,
                "error": result.stderr if not success else None,
                "execution_time": exec_time
            }
        except subprocess.TimeoutExpired:
            return {
                "code": code,
                "output": "",
                "success": False,
                "error": f"Execution timed out after {timeout} seconds.",
                "execution_time": timeout
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
