"""Run the local review profile with project-local state and no inherited keys."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = ROOT / '.local'
    state.mkdir(exist_ok=True)
    environment = {name: os.environ[name] for name in ('PATH', 'LANG', 'SYSTEMROOT') if name in os.environ}
    environment.update({
        'IKIMONO_SETTINGS_PATH': str(state / 'settings.json'),
        'IKIMONO_SHARE_DB': str(state / 'shares.db'),
        'IKIMONO_USER_DB': str(state / 'users.db'),
        'IKIMONO_PUBLIC_MODE': '0',
        'IKIMONO_LOGIN_REQUIRED': '0',
        'IKIMONO_BROWSER_PHOTOS': '0',
        'IKIMONO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
        'OLLAMA_URL': 'http://localhost:11434',
    })
    # Binding stays local because the operator profile permits settings writes.
    os.chdir(ROOT)
    os.execve(sys.executable, [
        sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8531',
    ], environment)


if __name__ == '__main__':
    main()
