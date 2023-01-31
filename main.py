from kivy.animation import Animation
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import ssl

from kivy.uix.togglebutton import ToggleButton

# ssl._create_default_https_context = ssl._create_unverified_context

Config.set('graphics', 'width', '250')
Config.set('graphics', 'height', '500')

from kivy.app import App
from kivy.properties import NumericProperty, Clock, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, FadeTransition
from kivy.lang import Builder

from bs4 import BeautifulSoup
import requests
from kivy.uix.textinput import TextInput

from saraksts import get_table, get_stundu_laiki, dictOfStrings, default_saraksts
from datetime import datetime, timedelta
import datetime as dtt


import pickle


class FastTransition(FadeTransition):
    duration = 0.1


class Global:
    tt = 2
    break_index = -1
    what_is = 'a'
    day = dtt.datetime.now().weekday()
    lesson_index = -1
    klase = '11-DIT'
    current_time = datetime.now().time()
    next_lesson = ''
    next_lesson_kab = ''
    lesson_count = 9
    min_until_break_end = 0

    # GLOBAL variables go here ^^^
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Global, cls).__new__(cls)
        return cls._instance


try:
    with open('data.pickle', 'rb') as file:
        data = pickle.load(file)
except EOFError:
    data = {}
    data['done_setup'] = False
    data['saraksts_11_DIT'] = default_saraksts
    Global.what_is = 'start'
    data['stundu_laiki'] = get_stundu_laiki()
    data['klase'] = Global.klase


    data['done_setup'] = True
    with open('data.pickle', 'wb') as file:
        pickle.dump(data, file)

with open('data.pickle', 'rb') as file:
    data = pickle.load(file)
    saraksts_11_DIT = data['saraksts_11_DIT']
    stundu_laiki = data['stundu_laiki']
    print(saraksts_11_DIT[2])


class BeigasApp(App):
    screenm = ScreenManager(transition=FastTransition())

    me = None

    def home(self, me):
        me.background_color = (0, 1, 0, 1)
        self.me = me
        Clock.schedule_once(self.fade_back)

    def fade_back(self, dt):
        anim = Animation(background_color=(0.5, .5, .5, 1), duration=1)
        anim.start(self.me)

    @staticmethod
    def load_files():
        Builder.load_file("gui/beigas.kv")
        Builder.load_file("gui/set.kv")
        Builder.load_file("gui/free.kv")
        Builder.load_file("gui/stundu_saraksts.kv")
        Builder.load_file("gui/setup.kv")
        Builder.load_file("gui/break.kv")
        Builder.load_file("gui/konsultacijas.kv")
        Builder.load_file("gui/tools.kv")
        Builder.load_file("gui/beigas.kv")
        Builder.load_file("gui/laiki.kv")

    load_files()

    def build(self):
        self.screenm.add_widget(MainWidget(name="lesson"))
        self.screenm.add_widget(Set(name="set"))
        self.screenm.add_widget(Break(name="break"))
        self.screenm.add_widget(Free(name="free"))
        self.screenm.add_widget(Tools(name="tools"))
        self.screenm.add_widget(Kons(name="kons"))
        self.screenm.add_widget(Table(name="table"))
        self.screenm.add_widget(Setup(name="setup"))
        self.screenm.add_widget(Laiki(name="laiki"))
        self.screenm.add_widget(Start(name="start"))
        return self.screenm


class MainWidget(Screen):        # Main class -------------------------------------------------------------------------
    current_lesson_txt = StringProperty("Sobrideja stunda")
    current_lesson_ends_in_txt = StringProperty()

    next_lesson = StringProperty('')
    next_lesson_kab = StringProperty()
    next_lesson_starts_in = StringProperty()
    break_ends_in = NumericProperty()

    date = dtt.datetime.now()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)
        Clock.schedule_once(self.update, 0.001)
        Clock.schedule_once(self.update, 0.001)
        Global.klase = data['klase']

    def current_lesson_index(self):
        #if Global.day < 5:
        for lesson_index, lesson in enumerate(stundu_laiki):
            print(lesson)
            start_time = dtt.time(int(lesson[0][0]), int(lesson[0][1]))
            end_time = dtt.time(int(lesson[1][0]), int(lesson[1][1]))

            if start_time <= Global.current_time <= end_time:
                print(lesson_index)
                return lesson_index
        return -1
        #else:
            #return -1

    def change_screen(self):
        if BeigasApp.screenm.current not in ("set", "tools", "kons", 'table', 'setup', 'setup', 'laiki', 'start'):
            BeigasApp.screenm.transition = NoTransition()
            BeigasApp.screenm.current = Global.what_is
            BeigasApp.screenm.transition = FastTransition()
            print(f'--------------{Global.what_is}')
        print(f"Current screen: {BeigasApp.screenm.current}")

    def what_is_now(self):
        print(f"Stundas index: {Global.lesson_index}")
        print(f"Break index: {Global.break_index}")
        print(f"what_is_now(): {Global.what_is}")
        print(f"Global() Day: {Global.day}")

        if 0 <= Global.lesson_index < Global.lesson_count-1:
            Global.what_is = 'lesson'
        elif Global.break_index >= 0:
            Global.what_is = 'break'
        else:
            Global.what_is = 'free'

    def current_break_index(self):
        if Global.day < 5:
            for i in range(len(stundu_laiki)):
                start_time = dtt.time(stundu_laiki[i][1][0], stundu_laiki[i][1][1])
                try:
                    end_time = dtt.time(stundu_laiki[i+1][0][0], stundu_laiki[i+1][0][1])
                except IndexError:
                    return -1

                if start_time <= Global.current_time <= end_time:
                    Global.break_index = i
                    return i
        else:
            return -1

    def update(self, dt):
        Global.current_time = datetime.now().time()

        if Global.what_is not in ('start', 'setup'):
            Global.lesson_index = self.current_lesson_index()
            Global.break_index = self.current_break_index()
            self.update_next_lesson()
            self.what_is_now()
            self.change_screen()
            Global.day = self.date.weekday()

            if Global.what_is == "lesson":
                self.update_current_lesson()
                self.update_table_block()

        self.change_screen()
        Global.tt += 1

        print(f'what_is() from update {Global.what_is}')
        print(f'Global day from update {Global.day}')
        print(f'Global klase  {Global.klase}')
        print('----------------------------------------------------------------------------------------------')

    def update_table_block(self):
        block = self.ids['table_block']
        block.clear_widgets()
        day_list = saraksts_11_DIT[Global.day]
        i = len(day_list) - 1
        while i >= 0:
            if day_list[i][0] == "":
                del day_list[i]
            else:
                break
            i -= 1
        Global.lesson_count = len(day_list)
        for i, item in enumerate(day_list):
            b = Label(text=item[0], color=[1, 1, 1, 0.8])
            if i == Global.lesson_index:
                b.color = [1, 0, 0, 1]
                b.bold = True
            elif i-1 == Global.lesson_index:
                b.bold = True
            block.add_widget(b)

    def update_current_lesson(self):
        if Global.what_is == "lesson":
            lesson = saraksts_11_DIT[Global.day][Global.lesson_index][0]
            second = (60 - Global.current_time.second) - 1
            if second < 10:
                second = f'0{second}'

            if lesson == '':
                end = self.min_until_bb_end(Global.lesson_index)
                if end < 10:
                    self.current_lesson_txt = f"Drīz beigsies ir bīvstunda"
                    self.current_lesson_ends_in_txt = f"{self.min_until_bb_end(Global.lesson_index)}:{second}"
                else:
                    self.current_lesson_txt = f"Tagad ir bīvstunda"
                    self.current_lesson_ends_in_txt = f"{self.min_until_bb_end(Global.lesson_index)+1}"

            end = self.min_until_lesson_end(Global.lesson_index)
            if end < 10:
                self.current_lesson_txt = f"Drīz beigsies {lesson}"
                self.current_lesson_ends_in_txt = f"{end}:{second}"
            else:
                self.current_lesson_txt = f"Tagad: {lesson}"
                self.current_lesson_ends_in_txt = f"{end+1}"

    def update_next_lesson(self):
        if Global.what_is != 'free':
            for item in saraksts_11_DIT[Global.day]:
                if item[0] != '':
                    self.next_lesson = item[0]
                    self.next_lesson_kab = item[1]
                    Global.next_lesson = item[0]
                    Global.next_lesson_kab = item[1]
                    break
        else:
            if Global.day < 4:
                for item in saraksts_11_DIT[Global.day + 1]:
                    print(item)
                    if item[0] != '':
                        self.next_lesson = item[0]
                        self.next_lesson_kab = item[1]
                        Global.next_lesson = item[0]
                        Global.next_lesson_kab = item[1]
                        break
            else:
                for i, item in enumerate(saraksts_11_DIT[0]):
                    if item[0] != '':
                        self.next_lesson = item[0]
                        self.next_lesson_kab = item[1]
                        Global.next_lesson = item[0]
                        Global.next_lesson_kab = item[1]
                        break

    def min_until_lesson_end(self, lesson_index):
        end_time = datetime.strptime(f"{stundu_laiki[lesson_index][1][0]}:{stundu_laiki[lesson_index][1][1]}", "%H:%M").time()
        end_time = datetime.combine(datetime.today(), end_time)
        time_difference = end_time - datetime.now()
        return ((time_difference.seconds % 3600) // 60)

    def min_until_bb_end(self, lesson_index):
        end_time = datetime.strptime(f"{stundu_laiki[lesson_index+1][0][0]}:{stundu_laiki[lesson_index+1][0][1]}", "%H:%M").time()
        end_time = datetime.combine(datetime.today(), end_time)
        time_difference = end_time - datetime.now()
        return ((time_difference.seconds % 3600) // 60)







class Break(Screen):  # BREAK SCREEN WIDGET --------------------------------------------
    mins = StringProperty()
    min_until_break_end_txt = StringProperty('R')
    next_lesson = StringProperty('a')
    next_lesson_kab = StringProperty('b')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('innitialized')
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        print(Global.what_is)
        print(f'Loop from Break update(): {Global.tt}')
        if Global.what_is in ('break', 'lesson'):
            self.min_until_break_end()
            self.next_lesson = Global.next_lesson
            self.next_lesson_kab = Global.next_lesson_kab
            self.update_table_block()
        print('Break_update---------------------')

    def min_until_break_end(self):
        #if not len(stundu_laiki[Global.break_index]) <= Global.break_index + 1:
            end_time = datetime.strptime(f"{stundu_laiki[Global.break_index+1][0][0]}:{stundu_laiki[Global.break_index+1][0][1]}",
                                         "%H:%M").time()
            end_time = datetime.combine(datetime.today(), end_time)
            print(f'end time 2 -- - -- - {end_time}')
            time_difference = end_time - datetime.now()
            print(end_time)
            result = str(((time_difference.seconds % 3600) // 60) + 1)
            print(result)
            self.min_until_break_end_txt = result
            Global.min_until_break_end = result
            return result
        #return -1

    def update_table_block(self):
        block = self.ids['table_block_break']
        block.clear_widgets()
        if Global.day < 5:
            day_list = saraksts_11_DIT[Global.day]
        else:
            day_list = saraksts_11_DIT[0]
        i = len(day_list) - 1
        while i >= 0:
            if day_list[i][0] == "":
                del day_list[i]
            else:
                break
            i -= 1
        for i, item in enumerate(day_list):
            b = Label(text=item[0], color=[1, 1, 1, 0.8])
            if i == Global.break_index:

                b.bold = True
            elif i-1 == Global.break_index:
                b.bold = True
                b.color = [1, 0, 0, 1]
            block.add_widget(b)


class Free(Screen):
    next_lesson_starts_in_int = StringProperty('a')
    next_lesson_label = StringProperty('Nākamā stunda sāksies pēc:')
    next_lesson = StringProperty('')
    next_lesson_kab = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        if Global.what_is == "free":
            self.next_lesson_starts_in()
            self.next_lesson = Global.next_lesson
            print(f'{Global.next_lesson}<-----------------------------------------')
            self.next_lesson_kab = Global.next_lesson_kab


    def next_lesson_starts_in(self):
        current_time = datetime.now().time()

        end_time = datetime.strptime(f"{stundu_laiki[0][0][0]}:{stundu_laiki[0][0][1]}", "%H:%M").time()

        if end_time < current_time:
            end_time = datetime.combine(datetime.today(), end_time) + timedelta(days=1)
            self.next_lesson_label = 'Stundas ir beigušās,\ntaču nākamās sāksies pēc:'

        else:
            end_time = datetime.combine(datetime.today(), end_time)
            self.next_lesson_label = 'Nākamā stundas sāksies pēc:'

        time_difference = end_time - datetime.now()

        h = time_difference.seconds // 3600
        m = (time_difference.seconds % 3600) // 60
        if Global.day > 3:
            day = 6 - Global.day
        else:
            day = 0
        if day != 0:
            self.next_lesson_starts_in_int = f"{day}d {h}h {m + 1}min"
        elif h != 0:
            self.next_lesson_starts_in_int = f"{h}h {m + 1}min"
        elif m > 9:
            self.next_lesson_starts_in_int = f"{m + 1}min"
        else:
            sec = (60 - Global.current_time.second) -1
            if sec > 9:
                self.next_lesson_starts_in_int = f"{m}:{sec}"
            else:
                self.next_lesson_starts_in_int = f"{m}:0{sec}"


class Kons(Screen):
    my_text = StringProperty("Nospied Enter lai meklētu")
    text_input_str = ''

    def home(self):
        BeigasApp.screenm.current = Global.what_is


    def on_focus(self, instance):
        if instance.focus and instance.text == "vārds/uzvards/priekšmets":
            instance.text = ""

    def on_text_validate(self, text):
        self.text_input_str = text.text
        print(text.text)

        vards = text.text

        for word, replacement in dictOfStrings.items():
            vards = vards.replace(word, replacement)
        url = "https://www.r64vsk.lv/5-12-klase/konsultacijas"

        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        kons = soup.find("tbody")

        konstxt = kons.text
        kons_array = konstxt.splitlines()

        vards = vards.casefold()
        for i in kons_array:
            if i.casefold().startswith(vards) or i.casefold().endswith(vards):
                vards = i

        try:
            index = kons_array.index(vards)
            self.my_text = f"\t{vards}\n\tLaiks: {kons_array[index + 2]}\n\tVieta: {kons_array[index + 4]}"
        except ValueError:
            self.my_text = "    neaks netika atrasts\n    pārbaudi pareizrakstību"






class Tools(Screen):
    def home(self):
        BeigasApp.screenm.current = Global.what_is
    def back(self):
        BeigasApp.screenm.current = Global.what_is






class Table(Screen):
    my_text = StringProperty()
    day_index = 0

    def on_enter(self, *args) -> None:
        a = ToggleButton(state="down")
        self.uncover(a, Global.day)

    # def on_clear(self, instance, value):
    #     print('gfhjklhjkghjsfdgkhjklfgdhjkldgshjksdfgl')
    #     if not value:
    #         instance.text = ""

    def on_leave(self, *args):
        table = self.ids['table']
        table_kab = self.ids['table_kab']
        table_index = self.ids['table_index']
        table.clear_widgets()
        table_kab.clear_widgets()
        table_index.clear_widgets()
    def home(self):
        BeigasApp.screenm.current = Global.what_is

    # def on_plus(self, instance):
    #     saraksts_11_DIT[0].append(['',''])
    #     a = ToggleButton(state="down")
    #     self.uncover(a, Global.day)
    #     self.uncover(a, 0)


    def uncover(self, me, day_index):
        self.day_index = day_index
        table = self.ids['table']
        table_kab = self.ids['table_kab']
        table_index = self.ids['table_index']
        table.clear_widgets()
        table_kab.clear_widgets()
        table_index.clear_widgets()

        for i in range(len(saraksts_11_DIT[day_index])):
            lesson_name = str(saraksts_11_DIT[day_index][i][0])
            b = TextInput(text=lesson_name,
                          background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0))

            self.ids[f'lesson{day_index}{i}'] = b
            # b.bind(on_focus=self.on_clear)
            table.add_widget(b)
            c = TextInput(text=str(saraksts_11_DIT[day_index][i][1]),
                          background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0))

            self.ids[f'kab{day_index}{i}'] = c
            # c.bind(on_touch_down=self.on_clear)
            table_kab.add_widget(c)

            lesson_index = Label(text=str(i+1))
            table_index.add_widget(lesson_index)
        # add_lesson = Button(text='+')
        # add_lesson.bind(on_press=self.on_plus)
        # table.add_widget(add_lesson)

    def save(self, me):
        inputs = []
        inputs2 = []
        for i in range(len(saraksts_11_DIT[self.day_index])):
            b = self.ids[f'lesson{self.day_index}{i}']
            inputs.append(b.text)
        for i in range(len(inputs)):
            saraksts_11_DIT[self.day_index][i][0] = inputs[i]

        for i in range(len(saraksts_11_DIT[self.day_index])):
            b = self.ids[f'kab{self.day_index}{i}']
            inputs2.append(b.text)
        for i in range(len(inputs)):
            saraksts_11_DIT[self.day_index][i][1] = inputs2[i]
        print(saraksts_11_DIT[self.day_index])

        me.background_color = (0, 1, 0, 1)
        Clock.schedule_once(self.fade_back)

        with open('data.pickle', 'wb') as file:
            data['saraksts_11_DIT'] = saraksts_11_DIT
            pickle.dump(data, file)

    def fade_back(self, dt):
        me = self.ids['table_save']
        anim = Animation(background_color=(0.5, .5, .5, 1), duration=1)
        anim.start(me)






class Setup(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init)

    def home(self):
        BeigasApp.screenm.current = Global.what_is

    def init(self, dt):
        root = self.ids['classes']
        allgrades = [['5A', '5B', '5C', '5D', '5E'],
                     ['6A', '6B', '6C', '6D', '6E'],
                     ['7A', '7B', '7C', '7D'],
                     ['8A', '8B', '8C', '8D'],
                     ['9A', '9B', '9C', '9D'],
                     ['10Inz', '10VUD'],
                     ['11DA', '11DIT', '11UZ', '11VISP'],
                     ['12DAS', '12DIT', '12UZ', '12VM'],
                     ]

        # Iterate through the grades to create boxlayouts and buttons
        for grades in allgrades:
            box = BoxLayout()
            for grade in grades:
                button = Button(text=grade, size_hint=(0.19, 0.8), background_color='gray')
                button.bind(on_press=self.on_button_press)
                box.add_widget(button)
            # Add the boxlayout to the root layout
            root.add_widget(box)

    def exit_setup(self):
        Global.what_is = 'free'
        BeigasApp.screenm.current = Global.what_is

    def on_button_press(self, me):
        Global.klase = me.text
        id = f'rs-class-table-{me.text}'
        with open('data.pickle', 'wb') as file:
            data['saraksts_11_DIT'] = get_table(id)
            data['klase'] = me.text
            pickle.dump(data, file)
        update_table()

        self.exit_setup()


def update_table():
    with open('data.pickle', 'rb') as file:
        data = pickle.load(file)
        global saraksts_11_DIT
        saraksts_11_DIT = data['saraksts_11_DIT']


class Start(Screen):
    pass



class Set(Screen):
    klase = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        self.klase = Global.klase



    def home(self):
        BeigasApp.screenm.current = Global.what_is


class Laiki(Screen):
    def on_enter(self, *args) -> None:
        self.uncover()
        self.header = self.ids['laiki_header']
        self.header.text = 'Stundu laiki'

    def home(self) -> None:
        BeigasApp.screenm.current = Global.what_is

    def highlight_text(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: instance.select_all(), 0)

    def uncover(self):
        lesson_count_number = self.ids['lesson_count_number']
        start_time_h = self.ids['start_time_h']
        end_time_h = self.ids['end_time_h']
        start_time_m = self.ids['start_time_m']
        end_time_m = self.ids['end_time_m']
        laiki_middle = self.ids['laiki_middle']

        lesson_count_number.clear_widgets()
        start_time_h.clear_widgets()
        end_time_h.clear_widgets()
        start_time_m.clear_widgets()
        end_time_m.clear_widgets()
        laiki_middle.clear_widgets()

        for i in range(len(stundu_laiki)-2):
            count = Label(text=str(i+1))
            dash = Label(text=str('-'))
            sh = TextInput(text=str(stundu_laiki[i][0][0]),
                           background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0), multiline=False)

            sm = TextInput(text=str(stundu_laiki[i][0][1]),
                           background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0), multiline=False)

            eh = TextInput(text=str(stundu_laiki[i][1][0]), multiline=False,
                           background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0))

            em = TextInput(text=str(stundu_laiki[i][1][1]), multiline=False,
                           background_color=(1, 1, 1, 0.3), padding=(10, 10, 0, 0))

            self.ids[f'start_time_h{i}'] = sh
            sh.bind(on_text_validate=self.save, on_focus=self.highlight_text)
            start_time_h.add_widget(sh)

            self.ids[f'start_time_m{i}'] = sm
            sm.bind(on_text_validate=self.save)
            start_time_m.add_widget(sm)

            self.ids[f'end_time_h{i}'] = eh
            eh.bind(on_text_validate=self.save)
            end_time_h.add_widget(eh)

            self.ids[f'end_time_m{i}'] = em
            em.bind(on_text_validate=self.save)
            end_time_m.add_widget(em)

            laiki_middle.add_widget(dash)
            lesson_count_number.add_widget(count)

        plus = Button(text='+')
        plus.bind(on_press=self.on_plus_press)
        lesson_count_number.add_widget(plus)

        minus = Button(text='-')
        minus.bind(on_press=self.on_minus_press)
        laiki_middle.add_widget(minus)

    def on_plus_press(self, me):
        stundu_laiki.append(stundu_laiki[-1])
        print(stundu_laiki)
        self.uncover()

    def on_minus_press(self, me):
        stundu_laiki.pop(-1)
        print(stundu_laiki)
        self.uncover()



    def save(self, me):
        print(stundu_laiki)
        start_time_h = []
        start_time_m = []
        end_time_h = []
        end_time_m = []

        for i in range(len(stundu_laiki)-2):
            sh = self.ids[f'start_time_h{i}']
            start_time_h.append(sh.text)
            sm = self.ids[f'start_time_m{i}']
            start_time_m.append(sm.text)

            eh = self.ids[f'end_time_h{i}']
            end_time_h.append(eh.text)

            em = self.ids[f'end_time_m{i}']
            end_time_m.append(em.text)

        for i in range(len(stundu_laiki)-2):
            sh = self.ids[f'start_time_h{i}']
            try:
                start_time_h[i] = int(start_time_h[i])
                if 0 <= start_time_h[i] <= 23:
                    stundu_laiki[i][0][0] = start_time_h[i]
                    sh.background_color = (1, 1, 1, 0.3)
                    if i+1 == len(stundu_laiki):
                        BeigasApp.screenm.current = 'set'
                        self.header.text = 'Saglabāts !'

                else:
                    sh.background_color = (0.8, 0, 0, 0.5)
                    self.header.text = 'Laikam ir jābūt no 0:00 - 23:59'
                    break
            except ValueError:
                sh.background_color = (0.8, 0, 0, 0.5)
                self.header.text = 'Ievadītajam laikam ir jābūt skaitlim'
                break

            with open('data.pickle', 'wb') as file:
                data['stundu_laiki'] = stundu_laiki
                pickle.dump(data, file)

            stundu_laiki[i][0][1] = int(start_time_m[i])
            stundu_laiki[i][1][0] = int(end_time_h[i])
            stundu_laiki[i][1][1] = int(end_time_m[i])

        print(stundu_laiki)


beigas_app = BeigasApp()

if __name__ == "__main__":
    beigas_app.run()
