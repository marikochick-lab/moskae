import os
import sys
SYSTEM_PATH = "/storage/emulated/0/MarikOS/system"
sys.path.insert(0, SYSTEM_PATH)
import sc
import UsersSupport

def find_labels(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    	
    labels = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(":"):
        	labels[stripped[1:]] = i
    
    return labels
def run_mosf(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 1. Находим все метки ОДИН РАЗ
    labels = find_labels(path)
    
    # 2. Выполняем построчно с goto
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Пропускаем пустые, комментарии, метки
        if line == "" or line.startswith("#") or line.startswith("_#"):
            i += 1
            continue
        
        if line.startswith(":"):
            i += 1
            continue
        
        # 3. Проверяем goto
        if line.startswith("goto "):
            label = line[5:].strip()
            if label in labels:
                i = labels[label]
                continue
            else:
                print(f"[MOSF] Метка не найдена: {label}")
                break
        
        # 4. Обычная команда
        try:
            sc.exec_sc(UsersSupport.get_user(UsersSupport.cur_un), line)
        except Exception as e:
            print(f"[MOSF] Ошибка в '{line}': {e}")
        
        i += 1