from kivy.app import App
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, FadeTransition
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder

from Saraksts import saraksts_11_DIT, stundu_laiki
from datetime import datetime, time
from datetime import timedelta

from datetime import datetime

import time

from kivy.config import Config
Config.set('graphics', 'width', '250')
Config.set('graphics', 'height', '500')

__version__ = "1.0"
class BeigasApp(App):
    screenm = ScreenManager(transition=NoTransition())

    def build(self):
        self.fscreen = MainWidget()
        screen = Screen(name="lesson")
        screen.add_widget(self.fscreen)
        self.screenm.add_widget(screen)

        self.secscreen = Break()
        screen = Screen(name="break")
        screen.add_widget(self.secscreen)
        self.screenm.add_widget(screen)

        self.screen3 = Weekend()
        screen = Screen(name="weekend")
        screen.add_widget(self.screen3)
        self.screenm.add_widget(screen)

        self.screen4 = Free()
        screen = Screen(name="free")
        screen.add_widget(self.screen4)
        self.screenm.add_widget(screen)

        return self.screenm


date = datetime.now()

Builder.load_file("beigas.kv")


class MainWidget(Screen):
    day = date.weekday()
    hrs = date.hour
    min = date.minute

    current_lesson_txt = StringProperty("Sobrideja stunda")
    current_lesson_ends_in_txt = StringProperty()

    next_lesson = StringProperty()
    next_lesson_kab = StringProperty()
    next_lesson_starts_in = StringProperty()
    break_ends_in = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 5)
        print(self.what_is_now())
        Clock.schedule_once(self.innit_screen, 5)

    def current_lesson_index(self):
        if self.day < 5:
            for i in range(0, len(saraksts_11_DIT[self.day])):
                if stundu_laiki[i][0][0] == self.hrs == stundu_laiki[i][1][0]:
                    if stundu_laiki[i][0][1] <= self.min <= stundu_laiki[i][1][1]:
                        return i
                elif stundu_laiki[i][0][0] <= self.hrs <= (stundu_laiki[i][1][0]):
                    if stundu_laiki[i][0][0] == self.hrs and stundu_laiki[i][0][1] <= self.min:
                        return i
                    if stundu_laiki[i][1][0] == self.hrs and self.min <= stundu_laiki[i][1][1]:
                        return i
        return -1

    def change_screen(self):
        BeigasApp.screenm.current = self.what_is_now()
        print(f"Current screen: {BeigasApp.screenm.current}")

    def innit_screen(self, dt):
        BeigasApp.screenm.current = self.what_is_now()
        print(f"Current screen: {BeigasApp.screenm.current}")

    def what_is_now(self):
        if self.current_lesson_index() >= 0:
            print(self.current_lesson_index())
            return "lesson"  # Notiek stunda
        elif self.current_break_index() >= 0:
            return "break"  # Ir starpbīdis
        elif self.day == 5 or self.day == 6:
            return "weekend"  # Ir brīvdiena
        else:
            return "free"  # Laiks ir ārpus stundu saraksta

    def current_break_index(self):
        if self.day < 5:
            for i in range(0, len(saraksts_11_DIT[self.day])):
                if stundu_laiki[i][1][0] == self.hrs == stundu_laiki[i+1][0][0]:
                    if stundu_laiki[i][1][1] <= self.min <= stundu_laiki[i+1][0][1]:
                        return i
                elif stundu_laiki[i][1][0] <= self.hrs <= (stundu_laiki[i+1][0][0]):
                    if stundu_laiki[i][1][0] == self.hrs and stundu_laiki[i][0][1] <= self.min:
                        return i
                    if stundu_laiki[i+1][0][0] == self.hrs and self.min <= stundu_laiki[i+1][0][1]:
                        return i
        return -1

    def update(self, dt):
        self.update_current_lesson()
        self.update_next_lesson()
        self.change_screen()

    def update_current_lesson(self):
        if self.what_is_now() == "lesson":
            self.current_lesson_txt = f"Tagad ir {self.lesson_name_from_index(self.current_lesson_index())}"
            self.current_lesson_ends_in_txt = f"{str(self.min_until_lesson_end(self.current_lesson_index()))}"

    def update_next_lesson(self):
        if self.day < 5:
            if len(saraksts_11_DIT[self.day]) == self.current_lesson_index():
                self.next_lesson = "nav"
            else:
                self.next_lesson = f"Nākamā stunda: {self.lesson_name_from_index(self.current_lesson_index()+1)}"
                self.next_lesson_kab = f"{saraksts_11_DIT[self.day][1][1]}. kab"

    def lesson_name_from_index(self, lesson_index):
        lesson = saraksts_11_DIT[self.day][lesson_index][0]
        return lesson

    def min_until_lesson_end(self, lesson_index):
        if lesson_index == -1:
            return -1
        else:
            if stundu_laiki[lesson_index][1][0] == self.hrs:
                lesson_end_time = stundu_laiki[lesson_index][1][1]
            else:
                lesson_end_time = (stundu_laiki[lesson_index][1][1] + 60)

            min_until_lesson_end = lesson_end_time - self.min
            print(min_until_lesson_end)
            return min_until_lesson_end

    def min_until_break_end(self, break_index):
        if self.current_break_index() == -1:
            return -1
        else:
            if stundu_laiki[break_index][1][0] == self.hrs:
                break_end_time = stundu_laiki[break_index+1][0][1]
                if break_end_time == 0:
                    break_end_time += 60
            else:
                break_end_time = (stundu_laiki[break_index+1][0][1] + 60)

            min_until_break_end = break_end_time - self.min
            print(break_end_time)
            return min_until_break_end


class Break(Screen):
    mins = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        self.min_until_break_end()

    def min_until_break_end(self):
        self.mins = str((MainWidget.min_until_break_end(MainWidget(), MainWidget.current_break_index(MainWidget()))))
        return self.mins


class Weekend(Screen):
    pass


class Free(Screen):
    next_lesson_starts_in_int = StringProperty()
    next_lesson_label_txt = StringProperty

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        self.next_lesson_starts_in()
        self.next_lesson_label()

    def next_lesson_label(self):
        if self.remaining_hrs() < 8:
            print(self.remaining_hrs())
            self.next_lesson_label_txt = "Stundas sāksies pēc:"
        else:
            self.next_lesson_label_txt = "Stundas ir beigušās,\n bet nākamās sāksies pēc"

        return self.next_lesson_label_txt

    def next_lesson_starts_in(self):
        if MainWidget.day < 5:
            if saraksts_11_DIT[MainWidget.day][0][0] == "Nav":
                starts = [8, 15]
            else:
                starts = [9, 0]

            if starts[0] >= MainWidget.hrs:
                remaining_hrs = starts[0] - MainWidget.hrs
            else:
                remaining_hrs = starts[0]+24 - MainWidget.hrs

            if starts[1] >= MainWidget.min:
                remaining_mins = starts[1] - MainWidget.min
            else:
                remaining_mins = starts[1]+60 - MainWidget.min
                remaining_hrs -= 1

            if remaining_hrs == 0:
                self.next_lesson_starts_in_int = f"{remaining_mins}min"
            elif remaining_mins < 10:
                self.next_lesson_starts_in_int = f"{remaining_hrs}h un 0{remaining_mins}min"
            else:
                self.next_lesson_starts_in_int = f"{remaining_hrs}h un {remaining_mins}min"
        return self.next_lesson_starts_in_int

    def remaining_hrs(self):
        remaining_hrs = 0
        if MainWidget.day < 5:
            if saraksts_11_DIT[MainWidget.day][0][0] == "Nav":
                starts = [8, 15]
            else:
                starts = [9, 0]

            if starts[0] >= MainWidget.hrs:
                remaining_hrs = starts[0] - MainWidget.hrs
            else:
                remaining_hrs = starts[0]+24 - MainWidget.hrs

            if starts[1] >= MainWidget.min:
                pass
            else:
                remaining_hrs -= 1
        return remaining_hrs


# class Manager(ScreenManager):
#     screen_one = ObjectProperty(None)
#     screen_two = ObjectProperty(None)
#     screen_three = ObjectProperty(None)
beigas_app = BeigasApp()


if __name__ == "__main__":
    beigas_app.run()
