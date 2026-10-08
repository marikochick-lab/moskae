import os
import shutil
import UsersSupport as UsSup
# Корневая папка файловой системы MarikOS
ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")


def init_filesystem():
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    os.makedirs(ROOT, exist_ok=True)


def get_path(path):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    path = path.strip()

    # Не позволяем выйти за пределы storage
    full_path = os.path.abspath(os.path.join(ROOT, path))
    root_path = os.path.abspath(ROOT)

    if not (full_path == root_path or full_path.startswith(root_path + os.sep)):
        raise ValueError("Недопустимый путь!")

    return full_path


def ls(path="."):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        folder = get_path(path)

        if not os.path.isdir(folder):
            print("Это не папка.")
            return

        items = os.listdir(folder)

        if not items:
            print("(пусто)")
            return

        for item in items:
            full = os.path.join(folder, item)

            if os.path.isdir(full):
                print(f"[DIR]  {item}")
            else:
                print(f"[FILE] {item}")

    except Exception as e:
        print("Ошибка:", e)


def mkdir(name):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        path = get_path(name)
        os.makedirs(path)
        print(f"Папка создана: {name}")

    except FileExistsError:
        print("Такая папка уже существует.")
    except Exception as e:
        print("Ошибка:", e)


def create_file(name):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        path = get_path(name)

        with open(path, "w", encoding="utf-8") as f:
            pass

        print(f"Файл создан: {name}")

    except Exception as e:
        print("Ошибка:", e)


def write_file(name, text):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        path = get_path(name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        print("Файл сохранён.")

    except FileNotFoundError:
        print("Файл не найден.")
    except Exception as e:
        print("Ошибка:", e)


def read_file(name):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        path = get_path(name)

        with open(path, "r", encoding="utf-8") as f:
            print(f.read())

    except FileNotFoundError:
        print("Файл не найден.")
    except Exception as e:
        print("Ошибка:", e)


def delete(path):
    ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"users/{UsSup.cur_un}/storage")
    try:
        full_path = get_path(path)

        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Объект не найден.")
            return

        print(f"Удалено: {path}")

    except Exception as e:
        print("Ошибка:", e)