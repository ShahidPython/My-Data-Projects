import os, time
from datetime import datetime, timedelta
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import mixer

class Alarm:
    def __init__(self):
        mixer.init()
        self.sound = None
        self.time = None
    
    def set_time(self):
        # Color definitions
        header = '\033[1;33m'  # Bold yellow
        option1 = '\033[38;5;214m'  # Orange
        option2 = '\033[38;5;117m'  # Light blue
        error = '\033[91m'  # Light red
        reset = '\033[0m'
        
        while True:
            fmt = input(f"{header}=== PyAlarm ==={reset}\nTime format ({option1}12{reset}/{option2}24{reset}): ")
            if fmt in ('12', '24'): break
        while True:
            try:
                t = input(f"Enter time (HH:MM{' AM/PM' if fmt=='12' else ''}): ")
                self.time = datetime.strptime(t.upper(), '%I:%M %p' if fmt=='12' else '%H:%M').time()
                break
            except: 
                example = f"{option1}2:30 PM{reset}" if fmt=='12' else f"{option2}14:30{reset}"
                print(f"{error}Invalid format. Example: {example}")

    def set_sound(self):
        error = '\033[91m'  # Light red
        reset = '\033[0m'
        while True:
            p = input("Sound file path [Enter for beep]: ").strip()
            if not p or os.path.exists(p): return p if p else None
            print(f"{error}File not found: {p}{reset}")

    def run(self):
        # Color definitions
        status = '\033[1;33m'  # Bold yellow
        alarm = '\033[1;31m'   # Bold red
        reset = '\033[0m'
        
        self.set_time()
        self.sound = self.set_sound()
        print(f"\n{status}Alarm set for {self.time.strftime('%H:%M')}{reset}\nWaiting... (Ctrl+C to cancel)")
        try:
            while True:
                if datetime.now().time() >= self.time:
                    print(f"\n{alarm}🚨 ALARM! Press Q to stop or S to snooze 🚨{reset}")
                    if self.sound:
                        s = mixer.Sound(self.sound)
                        c = s.play(loops=-1)
                        try:
                            import keyboard
                            while c.get_busy():
                                if keyboard.is_pressed('q'): c.stop(); return
                                if keyboard.is_pressed('s'): c.stop(); break
                                time.sleep(0.1)
                        except: pass
                    else: print('\a'*3)
                    if not self.sound or not c.get_busy():
                        self.time = (datetime.now() + timedelta(minutes=5)).time()
                        print(f"{status}⏰ Snoozed to {self.time.strftime('%H:%M')}{reset}")
                time.sleep(30)
        except KeyboardInterrupt: print(f"\n{status}Alarm cancelled{reset}")
        finally: mixer.quit()

if __name__ == "__main__": Alarm().run()