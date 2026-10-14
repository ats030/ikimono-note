"""Run source tests without inheriting operator settings or cloud credentials."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='ikimono-portfolio-tests-') as directory:
        environment = {name: os.environ[name] for name in ('PATH', 'LANG', 'SYSTEMROOT') if name in os.environ}
        environment.update({
            'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
            'IKIMONO_SETTINGS_PATH': str(Path(directory) / 'settings.json'),
            'IKIMONO_SHARE_DB': str(Path(directory) / 'shares.db'),
            'IKIMONO_USER_DB': str(Path(directory) / 'users.db'),
        })
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q',
                                 '-p', 'anyio.pytest_plugin', '--tb=short'], cwd=ROOT, env=environment)
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
