import sys
import os

# Add backend directory to sys.path so all imports (models, agents, tools, database) work seamlessly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "VerifyAI", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
