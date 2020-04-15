#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import typing
from pathlib import Path


class JetBrainsTool:
    name: str
    path: Path

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def _find_executable(self) -> Path:
        if self.name == 'AndroidStudio':
            exe_name = 'studio'
        else:
            exe_name = self.name

        exes = list(self.path.glob(f'ch-0/*/bin/{exe_name}64.exe'))
        if len(exes) == 0:
            raise Exception(f'Could not find executable in "{self.name}"')

        return exes[0]

    def generate_script(self, output_dir: Path) -> None:
        def escape_separator(win_path: Path) -> str:
            return str(win_path).replace('\\', '\\\\')

        escaped_path = escape_separator(self._find_executable())
        template = f'''#!/usr/bin/env bash
exec cmd "/c start {escaped_path} $@"
'''

        output_script = output_dir / self.name.lower()

        print(f'Generate {output_script}')
        with output_script.open('w') as f:
            f.write(template)

        output_script.chmod(0o755)


def is_plugin(name: str) -> bool:
    return re.match(r'resharper|dot', name, re.IGNORECASE) is not None


def collect_installed_jetbrains_tools() -> typing.List[JetBrainsTool]:
    tools: typing.List[JetBrainsTool] = []
    install_dir = Path(os.environ['LOCALAPPDATA'], 'JetBrains', 'Toolbox', 'apps')
    for entry in install_dir.iterdir():
        if entry.name == 'Toolbox':
            continue

        if is_plugin(entry.name):
            continue

        # IDE has multiple editions(e.g. Pycharm), it contains '-'(e.g. Pycharm-P)
        if '-' in entry.name:
            tool_name, _ = entry.name.split('-')
        else:
            tool_name = entry.name

        tools.append(JetBrainsTool(name=tool_name, path=Path(install_dir, entry.name)))

    return tools


def unix_path_to_win_path(unix_path: str) -> str:
    proc = subprocess.Popen(['cygpath', '-d', f"'{unix_path}'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    proc.wait()
    win_path: str = proc.communicate()[0].decode('utf-8')
    return win_path.strip()


def is_git_bash() -> bool:
    return os.getenv('MSYSTEM') is not None


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: generate-win-jetbrains-shell-script.py directory')
        sys.exit(0)

    if is_git_bash():
        output_dir = unix_path_to_win_path(sys.argv[1])
    else:
        output_dir = sys.argv[1]

    tools = collect_installed_jetbrains_tools()
    if len(tools) == 0:
        print("There is no JetBrains IDE", file=sys.stderr)
        return 1

    for tool in tools:
        tool.generate_script(Path(output_dir))

    return 0


if __name__ == '__main__':
    sys.exit(main())
