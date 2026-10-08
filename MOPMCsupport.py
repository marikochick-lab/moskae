import re
import ctypes
import mmap
import platform
import builtins
import filesystem
import os
import UsersSupport as UsSup
USER_DIR = os.path.abspath(filesystem.ROOT)
PROGRAMS_PATH = f"/storage/emulated/0/MarikOS/users/admin/Programs"
class PermissionDeniedError(Exception):
    pass


class MOPMCError(Exception):
    """Ошибка выполнения .mopmc программы"""
    pass


class MOPMC:
    """
    Загрузчик программ .mopmc (MarikOS Program - Machine Code).

    Синтаксис файла ПОЧТИ совпадает с .mopp:

        [
        name:ИмяПрограммы
        version:1.0
        ]
        script{Main:x86_64}:"
        <машинный код x86-64 здесь>
        "
        script{Main:aarch64}:"
        <машинный код ARM64 здесь>
        "

    Разница с .mopp: вместо Python-кода внутри script{...} пишется
    машинный код в виде HEX-байтов, например:

        script{Main:x86_64}:"
        B8 2A 00 00 00   ; mov eax, 42
        C3               ; ret
        "

    Байты разделяются пробелами/переносами строк, всё после ";" на
    строке считается комментарием и игнорируется.

    ВАЖНО: машинный код (в отличие от Python-кода в .mopp)
    ПРИВЯЗАН К АРХИТЕКТУРЕ ПРОЦЕССОРА — байты для x86-64 (ПК) и
    aarch64 (большинство Android-телефонов) это совершенно разные
    инструкции. Поэтому у script-блока можно (и нужно, если хочется
    кроссплатформенности) указать архитектуру через ":имя_архитектуры"
    в имени блока: script{Main:x86_64} / script{Main:aarch64}.

    При запуске (run_script/run_main) MOPMC сам определяет текущую
    архитектуру (через platform.machine()) и берёт нужный блок:
      - сначала ищет "Имя:текущая_архитектура"
      - если не нашёл — берёт блок без указания архитектуры
        "Имя" (если он есть) как universal/fallback

    Если подходящего блока нет вообще — кидает понятную ошибку
    вместо попытки исполнить код для чужого CPU (что привело бы
    либо к неверному результату, либо к падению/segfault).

    ВНИМАНИЕ: код выполняется процессором напрямую (через mmap +
    ctypes), поэтому:
      - ошибка в байт-коде может привести к падению (segfault)
        всего процесса MarikOS — это особенность настоящего
        машинного кода, а не баг MOPMC;
      - функция вызывается без аргументов и должна вернуть int
        в регистре eax/rax (x86-64) или w0/x0 (aarch64) — обычная
        конвенция вызова C для этой платформы.
    """

    # Приводим platform.machine() к одному из этих двух канонических
    # имён, чтобы в .mopmc-файлах не нужно было гадать про алиасы
    # вроде "amd64"/"AMD64" или "arm64"/"aarch64".
    _ARCH_ALIASES = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "x64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64",
    }

    def __init__(self, filepath):
        self.filepath = filepath
        self.name = None
        self.version = None
        self.scripts = {}   # name -> bytes (машинный код)
        self.meta = {}
        self.text = ""

    # ---------- загрузка и разбор файла ----------

    def load(self):
        with open(self.filepath, "r", encoding="utf-8") as file:
            self.text = file.read()

            self._parse_info()
        self._parse_scripts()
        self._parse_meta

        return self

    def _parse_info(self):
        name = re.search(r'name\s*:\s*([^\n\]]+)', self.text)
        version = re.search(r'version\s*:\s*([^\n\]]+)', self.text)

        if name:
            self.name = name.group(1).strip().strip('"')

        if version:
            self.version = version.group(1).strip().strip('"')

    def _parse_scripts(self):
        """Тот же самый разбор блоков script{Name}:"..." что и в MOPP,
        но содержимое сохраняется как HEX-текст, а не как Python-код."""
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
                    hex_text = "\n".join(script_lines)
                    self.scripts[script_name] = self._hex_to_bytes(hex_text)

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

    @staticmethod
    def _hex_to_bytes(hex_text):
        """Превращает текст с hex-байтами (с комментариями через ';'
        и произвольными пробелами/переносами строк) в объект bytes."""
        clean_lines = []
        for line in hex_text.splitlines():
            # отрезаем комментарий после ';'
            code_part = line.split(";", 1)[0]
            clean_lines.append(code_part)

        clean_text = " ".join(clean_lines)
        tokens = clean_text.split()

        try:
            return bytes(int(tok, 16) for tok in tokens)
        except ValueError as error:
            raise MOPMCError(
                f"MOPMC: некорректный машинный код (не hex-байт): {error}"
            )

    # ---------- выполнение ----------

    @classmethod
    def current_arch(cls):
        machine = platform.machine().lower()
        return cls._ARCH_ALIASES.get(machine, machine)

    def get_script(self, name):
        """Возвращает байты машинного кода для скрипта `name`,
        выбирая блок под текущую архитектуру CPU:
          1) "name:текущая_архитектура", если есть;
          2) просто "name" (universal-блок), если есть;
          3) None, если ничего подходящего нет.
        """
        arch = self.current_arch()

        specific = self.scripts.get(f"{name}:{arch}")
        if specific is not None:
            return specific

        return self.scripts.get(name)

    def run_script(self, name):
        code = self.get_script(name)

        if code is None:
            available = ", ".join(sorted(self.scripts.keys())) or "нет блоков"
            raise MOPMCError(
                f"MOPMC: нет машинного кода для '{name}' под архитектуру "
                f"'{self.current_arch()}'. Доступные блоки: {available}. "
                f"Добавь script{{{name}:{self.current_arch()}}} в файл."
            )

        if not code:
            raise MOPMCError(f"MOPMC: script '{name}' пуст")

        return self._execute(code)

    def run_main(self):
        return self.run_script("Main")

    @staticmethod
    def _execute(code_bytes):
        """
        Кладёт байты машинного кода в исполняемую страницу памяти
        и вызывает их как функцию int func(void) — cdecl без
        аргументов, результат в eax/rax.
        """
        size = max(len(code_bytes), mmap.PAGESIZE)

        # RWX-страница памяти.
        # На некоторых системах (в частности Android/Termux с включённой
        # W^X-защитой SELinux) ОС может запретить исполняемую mmap-память
        # и вернуть OSError/PermissionError. Ловим это явно, чтобы такая
        # ошибка не роняла весь шелл, а превращалась в понятное сообщение.
        try:
            buf = mmap.mmap(
                -1,
                size,
                prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC
            )
        except (OSError, PermissionError, ValueError) as error:
            raise MOPMCError(
                f"MOPMC: система запретила исполняемую память (mmap): "
                f"{error}. Возможно, на этом устройстве включена защита "
                f"W^X и выполнение машинного кода недоступно."
            )

        buf.write(code_bytes)

        func_type = ctypes.CFUNCTYPE(ctypes.c_int64)
        address = ctypes.addressof(ctypes.c_char.from_buffer(buf))
        func = func_type(address)

        try:
            result = func()
        finally:
            buf.close()

        return result


def load_mopmc(filepath):
    program = MOPMC(filepath)
    program.load()
    result = program.run_main()
    return program, result    # ← кортеж