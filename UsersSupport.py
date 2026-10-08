import json
import os
import shutil
from datetime import datetime

# ======================
# ПУТИ
# ======================
SYSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(SYSTEM_DIR, "Users.json")
USERS_DIR = os.path.join(os.path.dirname(SYSTEM_DIR), "users")

cur_un = "admin"
# ======================
# ЗАГРУЗКА / СОХРАНЕНИЕ
# ======================
def load_users():
    """Загружает всех пользователей из Users.json"""
    if not os.path.exists(USERS_FILE):
        return {}
    
    # Проверяем размер файла
    if os.path.getsize(USERS_FILE) == 0:
        return {}
    
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Если файл повреждён — возвращаем пустой
        return {}


def save_users(users):
    """Сохраняет всех пользователей в Users.json"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ======================
# СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
# ======================
def create_user(name, password, role):
    """Создаёт нового пользователя"""
    users = load_users()
    
    if name in users:
        return f"Пользователь '{name}' уже существует!"
    
    if role not in ("admin", "user", "guest"):
        return f"Неизвестная роль: {role}"
    
    home = os.path.join(USERS_DIR, name)
    
    users[name] = {
        "password": password,
        "role": role,
        "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "home": home
    }
    
    # Создаём папки пользователя
    os.makedirs(os.path.join(home, "storage"), exist_ok=True)
    os.makedirs(os.path.join(home, "Programs"), exist_ok=True)
    
    save_users(users)
    return f"Пользователь '{name}' ({role}) создан!"


# ======================
# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
# ======================
def delete_user(name):
    """Удаляет пользователя и его папку"""
    users = load_users()
    
    if name not in users:
        return f"Пользователь '{name}' не найден!"
    
    elif name in users:
        user = get_user(name)
        role = user["role"]
        if role == "admin":
        	return f"Нельзя удалить администратора"
    
    # Удаляем папку
    home = users[name]["home"]
    if os.path.exists(home):
        shutil.rmtree(home)
    
    del users[name]
    save_users(users)
    return f"Пользователь '{name}' удалён!"


# ======================
# ВХОД
# ======================
def login(name, password):
    """Проверяет логин и пароль"""
    users = load_users()
    
    if name not in users:
        return None, f"Пользователь '{name}' не найден"
    
    if users[name]["password"] != password:
        return None, "Неверный пароль"
    
    cur_un = name
    return users[name], f"Добро пожаловать, {name}!"


# ======================
# СПИСОК ПОЛЬЗОВАТЕЛЕЙ
# ======================
def list_users():
    """Возвращает список пользователей"""
    users = load_users()
    return list(users.keys())


def get_user(name):
    """Возвращает данные пользователя"""
    users = load_users()
    return users.get(name)


# ======================
# ПРАВА
# ======================
def can_manage_os(user_data):
    """Может ли пользователь управлять ОС"""
    if not user_data:
        return False
    return user_data.get("role") == "admin"


def can_use_system(user_data):
    """Может ли пользователь использовать систему"""
    if not user_data:
        return False
    return user_data.get("role") in ("admin", "user")


def is_guest(user_data):
    """Гость ли это"""
    if not user_data:
        return False
    return user_data.get("role") == "guest"


# ======================
# ОЧИСТКА ГОСТЯ
# ======================
def cleanup_guest(user_data):
    """Удаляет данные гостя"""
    if not user_data or not is_guest(user_data):
        return
    
    home = user_data["home"]
    if os.path.exists(home):
        shutil.rmtree(home, ignore_errors=True)


# ======================
# ПЕРВЫЙ ЗАПУСК
# ======================
def init_first_user():
    """Создаёт admin, если Users.json пуст"""
    users = load_users()
    if not users:
        create_user("admin", "", "admin")
        return "Создан пользователь 'admin' по умолчанию"
    return None