from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import threading
import sys
import sc

class KivyOutput:
    def __init__(self, label):
        self.label = label
    
    def write(self, text):
        self.label.text += text
    
    def flush(self):
        pass

class KivyInput:
    def __init__(self):
        self.buffer = ""
        self.event = threading.Event()
        self.waiting = False
    
    def readline(self):
        self.waiting = True
        self.event.clear()
        self.event.wait()
        self.waiting = False
        line = self.buffer
        self.buffer = ""
        return line + "\n"
    
    def feed(self, text):
        self.buffer = text
        self.event.set()

class MOS_App(App):
    def on_enter(self, instance):
        command = instance.text.strip()
        instance.text = ""
    
        self.output.text += f"\n> {command}\n"
    
        # Если сейчас ждём ввод для input() — отдаём туда
        if self.stdin.waiting:
            pass  # ничего не делаем
    
        # Запускаем команду в отдельном потоке
        def run():
            try:
                sc.exec_sc(None, command)
            except SystemExit:
                App.get_running_app().stop()
            except Exception as e:
                self.output.text += f"\nОшибка: {e}\n"
    
        threading.Thread(target=run, daemon=True).start()
    def build(self):
        
        self.ctv = "MarikOS Shell Kivy App Edition\n"
        
        layout = BoxLayout(orientation="vertical")
        
        self.output = Label(
            text=self.ctv,
            size_hint=(None, None),
            halign="left",
            valign="top",
            )
        self.output.bind(texture_size=self.output.   setter("size"))

        scroll = ScrollView()
        scroll.add_widget(self.output)
        layout.add_widget(scroll)
        sys.stdout = KivyOutput(self.output)
        self.stdin = KivyInput()
        sys.stdin = self.stdin
        self.input = TextInput(hint_text="Введите команду...", multiline=False)
        self.input.bind(on_text_validate=self.on_enter)
        
        layout.add_widget(self.input)
        
        return layout
    

MOS_App().run()