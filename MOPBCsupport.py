import os
import UsersSupport as UsSup

BASE_DIR = "/storage/emulated/0/MarikOS"
PROGRAMS_DIR = os.path.join(BASE_DIR, f"users/{UsSup.cur_un}/Programs")
STORAGE_DIR = os.path.join(BASE_DIR, f"users/{UsSup.cur_un}/storage")

class MOPBC:
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

            if line == "MOPBC":
                continue

            if line.startswith("version:"):
                self.version = line.split(":", 1)[1].strip()
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
                if command == "PUSH_STR":
                    value = argument.strip()

                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]

                    self.stack.append(value)

                elif command == "PUSH_INT":
                    try:
                        value = int(argument)
                        self.stack.append(value)
                    except ValueError:
                        print("Invalid integer: " + argument)

                elif command == "CALL":
                    if argument == "print":
                        if not self.stack:
                            print("MOPBC stack is empty")
                            break
                        else:
                            value = self.stack.pop()
                            print(value)
                    else:
                        print("Unknown function: " + argument)

                elif command == "POP":
                    if not self.stack:
                        print("MOPBC stack is empty")
                    else:
                        self.stack.pop()

                elif command == "HALT":
                    break

                else:
                    print("Unknown MOPBC instruction: " + command)

            except Exception as e:
                print(f"Ошибка выполнения инструкции '{instruction}': {e}")


def load_mopbc(program_name):
    if not program_name.endswith == ".mopbc":
    	program_name += ".mopbc"
    filepath = os.path.join(PROGRAMS_DIR, program_name)

    if not os.path.isfile(filepath):
        print(f"Программа '{program_name}' не найдена в {PROGRAMS_DIR}")
        return None

    program = MOPBC(filepath)
    result = program.load()

    if result is None:
        return None

    return program


def run(prog):
    program = load_mopbc(prog)
    program.run()