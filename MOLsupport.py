import os

BASE_DIR = "/storage/emulated/0/MarikOS"
STORAGE_DIR = os.path.join(BASE_DIR, "storage")


class MOL:
    def __init__(self, filepath):
        self.filepath = filepath
        self.version = None
        self.code = []
        self.stack = []

    def load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except Exception as e:
            print(f"Ошибка чтения файла '{self.filepath}': {e}")
            return None

        in_code = False

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line == "CODE":
                in_code = True
                continue

            if in_code:
                self.code.append(line)

        return self

    def run(self):
        for instruction in self.code:
            parts = instruction.split(" ", 1)

            command = parts[0]

            if len(parts) > 1:
                argument = parts[1]
            else:
                argument = ""

            try:
                if command == "CR.TXT":
                    value = argument.strip()

                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]

                    self.stack.append(value)

                elif command == "CR.NUM":
                    try:
                        value = int(argument)
                        self.stack.append(value)
                    except ValueError:
                        print("Invalid integer: " + argument)

                elif command == "EX.CALL":
                    if argument == "scrs":
                        if not self.stack:
                            print("MOPMC stack is empty")
                            break
                        else:
                            value = self.stack.pop()
                            print(value)
                    else:
                        print("Unknown function: " + argument)

                elif command == "POP":
                    if not self.stack:
                        print("MOL stack is empty")
                    else:
                        self.stack.pop()

                elif command == "END":
                    break

                else:
                    print("Unknown MOL instruction: " + command)

            except Exception as e:
                print(f"Ошибка выполнения инструкции '{instruction}': {e}")


def load_molscr(scr_name):
    if not scr_name.endswith(".mol"):
        scr_name += ".mol"

    filepath = os.path.join(STORAGE_DIR, scr_name)

    if not os.path.isfile(filepath):
        print(f"Скрипт '{scr_name}' не найден в {STORAGE_DIR}")
        return None

    program = MOL(filepath)
    result = program.load()

    if result is None:
        return None

    return program


def run(scr_n):
    program = load_molscr(scr_n)

    if program is not None:
        program.run()
    else:
    	print("Error: 42")