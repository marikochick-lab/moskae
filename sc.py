try:
    sce = None
    si = "MarikOS Shell"
    import webbrowser
    import re
    # Все цвета
    COLORS = {
        # Сначала длинные (с bg_ и т.д.)
       "bg_red": '\033[41m\033[97m',
       "bg_green": '\033[42m\033[97m',
       "bg_blue": '\033[44m\033[97m',
       "bg_purple": '\033[45m\033[97m',
       "bg_yellow": '\033[43m\033[97m',
    
       # Потом короткие
       "red": '\033[91m',
       "green": '\033[92m',
       "blue": '\033[94m',
       "purple": '\033[95m',
       "yellow": '\033[93m',
       "bold": '\033[1m',
    }

    END = '\033[0m'

    def colorize(text):
        for color_name, code in COLORS.items():
            pattern = rf"{color_name}\[(.*?)\]"
            text = re.sub(pattern, f"{code}\\1{END}", text)
        return text
    
    import os
    import sys
    import time
    import json
	
    PROJECT_PATH = "/storage/emulated/0/MarikOS"
    SYSTEM_PATH = os.path.join(PROJECT_PATH, "system")
    SP_PATH = "/storage/emulated/0/MarikOS/ShellPacks"
    USERS_PATH = "/storage/emulated/0/MarikOS/users"
	
    sys.path.insert(0, PROJECT_PATH)
    sys.path.insert(0, SYSTEM_PATH)
    sys.path.insert(0, SP_PATH)
    
    import filesystem
    from ShellPacks import PackFileCommands
    from ShellPacks import PackPythonCommands
    import MOPPsupport
    import MOPBCsupport
    import MOLsupport
    import MOPMCsupport
    import MOmoreclient as mocl
    import UsersSupport
except Exception as e:
	print(f"Error in imports '{e}' ")
def tree(path, prefix=""):
    try:
        items = sorted(os.listdir(path))

        for i, item in enumerate(items):
            full_path = os.path.join(path, item)
            last = i == len(items) - 1

            print(prefix + ("└── " if last else "├── ") + item)

            if os.path.isdir(full_path):
                tree(
                    full_path,
                    prefix + ("    " if last else "│   ")
                )

    except PermissionError:
        print(prefix + "└── [ACCESS DENIED]")
def mos_error(pr, des):
	return f"""MarikOS Shell Error:
{pr}: {des}"""

def calc(aa, oppp, bb):
    if oppp == "+":
        rslt = int(aa) + int(bb)
        return rslt
    elif oppp == "-":
        rslt = int(aa) - int(bb)
        return rslt
    elif oppp == "/":
        rslt = int(aa) / int(bb)
        return rslt
    elif oppp == "*":
        rslt = int(aa) * int(bb)
        return rslt
    else:
        return mos_error("Syntax Error", "Invalid Operation")
import random
try:
    MOPMC_AVAILABLE = True
except Exception as _mopmc_import_error:
    MOPMCsupport = None
    MOPMC_AVAILABLE = False
    print("Warning: MOPMCsupport not loaded:", _mopmc_import_error)
shell = True
aa = 0
bb = 0
oppp = "+"
nn = "0"
tt = "0"
VERSHELL = 0.2
NAME = f"{mocl.NAMEOS} Shell"
ERDES = 0
ERPR = 0
ch = []
vars = {}
ucs = {}
def get_svar(svar):
	if svar in vars:
		return vars[svar]
	else:
		raise NameError(f"Variable '{svar}' not founded")
def scm_load():
    global ucs
    with open("scm_saved.json", "r", encoding="utf-8") as f:
        content = json.load(f)
        ucs.update(content)
def scm_save(cfs):
    with open("scm_saved.json", "w", encoding="utf-8") as f:
        json.dump(ucs, f, ensure_ascii=False, indent=2)
def expand_vars(text, variables, max_depth=5):
    """Заменяет %VarName% на значения из словаря variables.
    Поддерживает вложенные переменные (%A% внутри %B%).
    """
    for _ in range(max_depth):
        new_text = re.sub(
            r"%(\w+)%",
            lambda m: variables.get(m.group(1), m.group(0)),
            text
        )
        if new_text == text:
            break
        text = new_text
    return text
CD_PATH = f"/storage/emulated/0/MarikOS"
CCDP = f"S:{CD_PATH.removeprefix('/storage/emulated/0/MarikOS')}"
def ccdp_update():
    global CCDP
    CCDP = f"S:{CD_PATH.removeprefix('/storage/emulated/0/MarikOS')}"
command_queue = []
def CD(newcd):
	global CD_PATH
	CD_PATH = newcd
def exec_sc(su_data, shellcomline):
    global CD_PATH, CCDP, PROJECT_PATH
    if " && " in shellcomline:
    	commands = shellcomline.split(" && ", 100)
    	for cmd in commands:
    		command_queue.append(cmd.strip(" && "))
    	return
    parts = shellcomline.split(" ", 1)
    
    command = parts[0]

    if len(parts) > 1:
        argument = parts[1]
    else:
        argument = ""
    argsLst = argument.split(",, ", 10)

    for i in range(len(argsLst)):
        argsLst[i] = argsLst[i].strip(",, ")
    ch.append(shellcomline)
    
    for i in range(len(argsLst)):
        newal = expand_vars(argsLst[i], vars)
        argsLst[i] = newal
    
    shellcomline = expand_vars(shellcomline, vars)
    parts = shellcomline.split(" ", 1)
    command = parts[0]
    if len(parts) > 1:
        argument = parts[1]
    else:
        argument = ""
    argsLst = argument.split(",, ", 10)
    
    
    if command == "echo":
        global sce
        if argument == "":
            print("Syntax Error")
        else:
            expanded = expand_vars(argument, vars)
            if not sce is None:
            	print(colorize(f"{expanded} purple[{sce}]"))
            else:
            	print(colorize(expanded))

    elif command == "test":
        print(argument, "Test")

    elif command == "exit":
        if not su_data is None:
            if su_data["role"] == "guest":
        	    print(f"В аккаунте гостя нельзя выйти с помощью exit. Попробуйте glo {sun}")
            else:
            	pass
        else:
            if su_data is None:
                exit()
            else:
            	if not su_data["role"] == "guest":
            		exit()
            

    elif command == "MathCalc":
        sa = argument.split(" ", 2)
        print(calc(sa[0], sa[1], sa[2]))
   
    elif command == "testShell":
    	print(aa, bb, oppp, argument, shellcomline, command, shell)
    
    elif command == "FalseShell":
    	if su_data["role"] == "guest":
    		print(f"В аккаунте гостя нельзя выйти с помощью FalseShell. Попробуйте glo {sun}")
    	else:
    	    shell = False
    
    elif command in ("cr.file", "del.file", "setWRF.name", "setWRF.text"):
        PackFileCommands.file_commands(command, argument)
    
    elif command == "wr.file":
    	PackFileCommands.wrf(argsLst[0], argsLst[1])

    elif command == "clear":
        os.system("cls" if os.name == "nt" else "clear")
    
    elif command == "help":
    	 print("""File:
  cr.file <name>       Создать файл
  wr.file              Записать файл
  del.file <name>      Удалить файл

Math:
  MathCalc <число>/, <операция>/, <число>   Решить математический  пример

Programs:
  run.py <name>            Запустить .mopp программу (Python)
  runmc <name>         Запустить .mopmc программу (Machine Code)
  run.pbc <name>           Запустить .mopbc программу (Байт код)

System:
  clear                    Очистить от команд и лого
  exit                      Выйти
  echo <text>       Вывести текст
  testShell             Тест терминала
  test             Тест вывода и аргумента
  FalseShell          Выключить терминал""")
  
    elif command == "pyt>":
    	 PackPythonCommands.pytcom(argument)
    
    elif command == "run.py":
        if argument == "":
            print("Syntax Error")
        else:
            program_path = os.path.join(MOPMCsupport.PROGRAMS_PATH, argument)

            if not program_path.endswith(".mopp"):
                program_path += ".mopp"

            try:
                program = MOPPsupport.load_mopp(program_path)
                program.run_main()

            except FileNotFoundError:
                print("Program not found:", argument)

            except Exception as error:
                print("Program error:", error)

    elif command == "echo.":
        print(" ")
    
    elif command == "read.file":
        filesystem.read_file(argument)
    
    elif command == "run.pbc":
    	MOPBCsupport.run(argument)
    
    elif command == "run.mol.scr":
    	MOLsupport.run(argument)
    
    elif command == "runmc":
        if not MOPMC_AVAILABLE:
            print("MOPMC недоступен на этом устройстве (см. предупреждение при запуске)")
        elif argument == "":
            print("Syntax Error")
        else:
            program_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                f"users/{UsersSupport.cur_un}/Programs",
                argument
            )
            print(f"[DEBUG] Ищу: {program_path}")
            print(f"[DEBUG] Существует: {os.path.exists(program_path)}")

            if not program_path.endswith(".mopmc"):
                program_path += ".mopmc"

            try:
                program = MOPMCsupport.load_mopmc(program_path)
                result = program.run_main()
                print(f"[MOPMC] Программа завершена, результат: {result}")

            except FileNotFoundError:
                print("Program not found:", argument)

            except MOPMCsupport.MOPMCError as error:
                print("MOPMC Error:", error)

            except Exception as error:
                print("Program error:", error)
    
    elif command == "errorTr":
    	raise Exception(argument)
    
    elif command == "error":
    	try:
    	    print(mos_error(argsLst[0], argsLst[1]))
    	except IndexError:
    		print(mos_error("ArgsError", "Необходим второй элемент"))
    
    elif command == "client.er":
    	mocl.mo_error("ByUser", argument)
    
    elif command == "sinfo":
    	print(f"Name: {mocl.NAMEOS}")
    	print(f"Version: {mocl.VEROS}")
    
    elif command == "var":
    	try:
    	    ap = argument.split(" = ", 1)
    	    nn = ap[1].split(" ", 1)
    	    if nn[0] == "inp":
    	    	inputed = input(nn[1])
    	    	vars[ap[0]] = inputed
    	    else:
    	    	vars[ap[0]] = ap[1]
    	except Exception as er:
    		print(mos_error(type(er).__name__, er))
    
    elif command == "readvar":
    	try:
    	    print(vars[argument])
    	except Exception as er:
    		error = f"{type(er).__name__}:{er}"
    		mos_error("PythonEr", f"{error}")
    
    elif command == "tree":
        try:
            if argument == "":
                tree(CD_PATH)
            else:
                tree(os.path.join(PROJECT_PATH, argument))
        except FileNotFoundError:
        	print(mos_error("DirError", "No such file or directory"))
    
    elif command == "cd":
        CDT = os.path.join(PROJECT_PATH, argument)
        if argument == "..":
        	print(mos_error("DirError", "Нельзя выйти за пределы MarikOS"))
        elif not os.path.isdir(CDT):
            print("Папка не существует")
        else:
            CD_PATH = os.path.join(PROJECT_PATH, argument)
            ccdp_update()
    
    elif command == "cd+":
    	if argument == "..":
    		print(mos_error("SyntaxError", ".. недопустим при такой команде"))
    	else:
    	    if not os.path.exists(os.path.join(CD_PATH, argument)):
    	    	print(mos_error("DirError", "No such file or directory"))
    	    else:
    	    	CD_PATH = os.path.join(CD_PATH,argument)
    	    	ccdp_update()
    
    
    elif command == "cd-":
        new_path = os.path.abspath(os.path.join(CD_PATH, ".."))

        if os.path.commonpath([new_path, PROJECT_PATH]) != os.path.abspath(PROJECT_PATH):
            print(mos_error("DirError", "Нельзя выйти за пределы MarikOS"))
        else:
            CD_PATH = new_path
            ccdp_update()
    
    elif command == "ccdp":
        relative_path = os.path.relpath(CD_PATH, PROJECT_PATH)

        if relative_path == ".":
            print("/")
        else:
            print("/" + relative_path.replace(os.sep, "/"))
    
    elif command == "comhis":
    	print(ch)
    
    elif command == "whome":
    	if not su_data is None:
    	    print("User:", sun)
    
    elif command == "cu_test":
    	print(UsersSupport.cur_un)
    
    elif command == "login":
        try:
            print("Input your username")
            sun = input("Your username: ")
            su_data = UsersSupport.get_user(sun)
        
            if su_data is None:
                print(mos_error("UserError", "This user not geted"))
                exit()
            else:
                UsersSupport.cur_un = sun
                os.system("cls" if os.name == "nt" else "clear")
        
            if su_data["password"] == "":
                pass
            else:
                spw = input("Input password:")
                os.system("cls" if os.name == "nt" else "clear")
            
                if spw != su_data["password"]:
                    print(mos_error("UserError", "Invalid password"))
                    exit()
                
        except Exception as er:
            print(mos_error("UnkError", f"Error: {er}"))
        finally:
            print("="*40)
            print(" "*9, f"{NAME}. v:{VERSHELL}")
            print("="*40)
    
    elif command == "glo":
    	UsersSupport.cleanup_guest(UsersSupport.get_user(argument))
    	UsersSupport.delete_user(argument)
    	exit()
    
    elif command == "add.user":
    	if not su_data is None:
    	    if su_data["role"] != "admin":
    		    print(mos_error("UserError", "У вас недостаточно прав для этого действия"))
    	    else:
    	        if argsLst[1] == "":
    	    	    print("Если вы не хотите ставить пароль то лучше вместо пустоты писать None")
    	        elif argsLst[1] == "None":
    	    	    UsersSupport.create_user(argsLst[0], "", argsLst[2])
    	        else:
    	            UsersSupport.create_user(argsLst[0], argsLst[1], argsLst[2])
    	else:
        	print(mos_error("UserError", "You don't have account"))
    
    elif command == "myrole":
    	if not su_data is None:
    	    print(f"Role: {su_data['role']}")
    
    elif command == "rest":
    	st = int(argsLst[0])
    	unit = str(argsLst[1])
    	min = 60
    	hr = min * 60
    	if unit == "sec":
    		time.sleep(st)
    	elif unit == "min":
    		time.sleep(min * st)
    	elif unit == "hr":
    	    time.sleep(hr * st)
    	else:
    		print(mos_error("SyntaxError", f"Неизвестная единица: {unit}"))
    
    elif command == "run.mosf":
        import mosf
        mosf.run_mosf(os.path.join(CD_PATH, argument))
    
    elif command == "if":
        parts = argument.split(",, ", 1)
        condition = parts[0]
        action = parts[1]
        
        cond_parts = condition.split(" = ", 1)
        left = expand_vars(cond_parts[0], vars)
        right = expand_vars(cond_parts[1], vars)
        if right == "$*$":
        	condition_true = True
        elif left == "$*$":
        	condition_true = True
        elif left == right:
            # Кладём в очередь, а не вызываем
            command_queue.append(action)
    
    elif command == "inp":
    	input(argument)
    
    elif command == "url":
    	if argument == "":
        	print(mos_error("SyntaxError", "web <url>"))
    	else:
        	# Если нет http:// или https:// — добавляем
        	url = argument
        	if not url.startswith("http://") and not url.startswith("https://"):
        		url = "https://" + url
        
    	try:
            webbrowser.open(url)
            print(colorize(f"green[Открываю: {url}]"))
    	except Exception as e:
            print(mos_error("WebError", str(e)))
    
    elif command == "gsearch":
    	query = argument.replace(" ", "+")
    	webbrowser.open(f"https://google.com/search?q={query}")
    
    elif command == "ss":
    	unit = argsLst[0]
    	Mearning = argsLst[1]
    	if unit == "/si":
    		si = Mearning
    	if unit == "/sce":
    		sce = Mearning
    
    elif command.startswith("_#"):
    	pass
    
    elif shellcomline == "find matrix":
    	print("MATRIX LOADED")
    	while True:
    		syms = "ABCabcDEFdefАБВабвГДЖеё"
    		print(f"{random.choice(syms)}{random.choice(syms)}{random.choice(syms)}")
    
    elif command == "scm":
    	if argument == "":
    		print(mos_error("SyntaxError", "Нету аргумента"))
    	else:
    		ucs[argsLst[0]] = argsLst[1]
    
    elif command in ucs:
    	command_queue.append(ucs[command])
    
    elif command == "loop":
    	loop = 0
    	mt = int(argsLst[0])
    	coms = argsLst[1]
    	while loop != mt:
    		loop = loop + 1
    		import sc2
    		sc2.ce(coms)
    
    elif command == "mkdir":
    	if argument == "":
    		print(mos_error("SyntaxError", "Нету аргумента"))
    	else:
    		path = os.path.join(CD_PATH, argument)
    		try:
    			os.makedirs(path, exist_ok=True)
    			print("MKDIR succesful")
    		except FileExistsError:
    			print(mos_error("DirError", "Папка уже существует"))
    		except Exception as e:
    			print(mos_error(type(e).__name__, e))
    		
    elif command == "save_scm":
        try:
            scm_save(ucs[argument])
        except KeyError:
            print(mos_error("NameError", f"Name '{argument}' not found"))
    
    elif not shellcomline == "":
        if all(c in (" ", "	", "\t") for c in shellcomline):
        	print("Это пустота.")
        else:
            print(f"Команды {command} нету в терминале, всех паках и ваших командах (ucs). ")