import re
import os
import builtins
import UsersSupport
import filesystem  # чтобы взять тот же ROOT, что и у файловой системы

USER_DIR = os.path.abspath(filesystem.ROOT)


class PermissionDeniedError(Exception):
    pass


def _safe_open(path, mode="r", *args, **kwargs):
    if os.path.isabs(path):
        full_path = os.path.abspath(path)
    else:
        full_path = os.path.abspath(os.path.join(USER_DIR, path))

    if not (full_path == USER_DIR or full_path.startswith(USER_DIR + os.sep)):
        raise PermissionDeniedError(
            f"Превышение прав программы: доступ к '{path}' запрещён"
        )

    return builtins.open(full_path, mode, *args, **kwargs)


class MOPP:
    def __init__(self, filepath):
        self.filepath = filepath
        self.name = None
        self.version = None
        self.scripts = {}
        self.meta = {}

    def load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                self.text = file.read()
        except Exception as e:
            print(f"Ошибка чтения программы '{self.filepath}': {e}")
            return None

        self._parse_info()
        self._parse_scripts()
        self._parse_meta()

        return self

    def _parse_info(self):
        name = re.search(r'name\s*:\s*([^\n\]]+)', self.text)
        version = re.search(r'version\s*:\s*([^\n\]]+)', self.text)

        if name:
            self.name = name.group(1).strip().strip('"')
        if version:
            self.version = version.group(1).strip().strip('"')

    def _parse_scripts(self):
        lines = self.text.splitlines()

        inside_script = False
        script_name = None
        script_lines = []

        for line in lines:
            stripped = line.strip()

            if not inside_script:
                if stripped.startswith("script{") and "}:" in stripped:
                    start = stripped.find("script{") + len("script{")
                    end = stripped.find("}:")
                    script_name = stripped[start:end].strip()
                    after_colon = stripped[end + 2:].strip()

                    if after_colon == '"':
                        inside_script = True
                        script_lines = []
            else:
                if stripped == '"':
                    self.scripts[script_name] = "\n".join(script_lines)
                    inside_script = False
                    script_name = None
                    script_lines = []
                else:
                    script_lines.append(line)

    def _parse_meta(self):
        meta_matches = re.finditer(
            r'meta\s*\{([^}]+)\}\s*:\s*\[([\s\S]*?)\]',
            self.text
        )

        for match in meta_matches:
            meta_name = match.group(1).strip()
            meta_content = match.group(2)

            values = re.findall(r'(\w+)\s*:\s*"([^"]*)"', meta_content)

            self.meta[meta_name] = {}
            for key, value in values:
                self.meta[meta_name][key] = value

    def get_script(self, name):
        return self.scripts.get(name)

    def run_script(self, name):
        code = self.get_script(name)

        if code is None:
            print(f"MOPP: скрипт '{name}' не найден")
            return

        safe_builtins = dict(vars(builtins))
        safe_builtins["open"] = _safe_open

        safe_globals = {"__builtins__": safe_builtins}

        try:
            exec(code, safe_globals)
        except PermissionDeniedError as e:
            print("Ошибка прав доступа:", e)
        except Exception as e:
            print("Ошибка выполнения программы:", e)

    def run_main(self):
        self.run_script("Main")


def load_mopp(filepath):
    program = MOPP(filepath)
    result = program.load()

    if result is None:
        return None

    return program