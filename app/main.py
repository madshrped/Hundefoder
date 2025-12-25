from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import ScrollView
from kivy.uix.codeinput import TextInput
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from kivy.core.text import Text
from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.factory import Factory
from kivy.clock import Clock

from datetime import datetime
import client


def get_today():
    now = datetime.now()
    return event(now.year, now.month, now.day, now.hour, now.minute)


class RoundedTextInput(TextInput):
    pass


class CustomLabel(Label):
    pass


class Empty_object(CustomLabel):
    pass


# class PopupContent(BoxLayout):
#     pass

# class CustomPopup(Popup):
#     pass


class BoxPick_pop(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.num_boxes = 0
        self.title = "Kasse?"
        self.content = BoxLayout(
            padding=self.width * 0.09,
            orientation="vertical",
            spacing=self.height * 0.09,
        )
        self.no_contact = client.no_contact
        self.size_hint = (0.75, 0.2)
        self.auto_dismiss = False
        self.std_timeout = 1

        self.ex_text = Pop_msg(text="Hvilken kasse skal der åbnes for?")
        self.content.add_widget(self.ex_text)
        self.input = RoundedTextInput(
            bg_color=(0.9, 0.9, 1, 1),
            border_buff=0.05,
            border_color=(0.7, 0.7, 0.8, 1),
            input_filter="int",
            multiline=False,
            size_hint=(0.7, 1),
            input_type="number",
        )
        self.content.add_widget(self.input)
        self.send = RoundedButton(
            text="[b]Send[/b]",
            default_color=(68 / 255, 145 / 255, 68 / 255, 1),
            border_color=(1, 1, 1, 1),
            border_buff=0.01,
            size_hint=(0.7, 1),
        )
        self.content.add_widget(self.send)
        self.send.bind(on_release=self.capture)

    def capture(self, _):
        try:
            int(self.input.text)
        except ValueError:
            show_popup(
                "Fejl",
                f"{self.input.text} er ikke et tal. Kasserne er nummereret, og skal inputtet skal derfor være tal mellem 1 og {self.num_boxes}",
            )

        if self.input.text == "":
            err = f"""Ingen dispensor valgt"""
            self.ex_text.text = err

        elif not (0 < int(self.input.text) <= self.num_boxes):
            err = f"""Dispenser {self.input.text} findes ikke"""
            self.ex_text.text = err

        else:
            self.dismiss()
            bridge.send_message(f"i{int(self.input.text)-1}")
            message = reciver.anticipate(self.std_timeout)
            if message == self.no_contact:
                show_popup("Fejl", self.no_contact)
            else:
                show_popup("Aktivering", message)


class RoundedButton(Button):
    button_color = ObjectProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

    def on_press(self):
        self.button_color = [
            self.button_color[i] * self.press_shade[i] for i in range(4)
        ]

    def on_release(self):
        self.button_color = self.default_color

    def update(self):
        pass


class EventHolder(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)

    def update(self):
        self.label_font_size = self.height / 8

    def delete_me(self, q_number):
        app = App.get_running_app()
        main_window = app.root.get_screen("main")
        main_window.delete_event(q_number)


class InputContainers(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Scroller(InputContainers):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.length = 0
        self.bind(children=self._update_height)

    def _update_height(self, *args):
        total_height = sum([child.height for child in self.children])
        self.height = (
            total_height + self.padding[1] * 2 + self.spacing * len(self.children)
        )

    def add_element(self, element=None):
        if element is None:
            element = EventHolder()
        self.add_widget(element)
        self._update_height()
        self.length += 1

    def pop_element(self, index):
        self.remove_widget(self.children[index])
        self._update_height()
        self.length -= 1

    def clear_elements(self):
        self.clear_widgets()


class Pop_msg(Label):
    pass


def show_popup(
    _title: str, _text: str = None, sizehint: tuple = (0.75, 0.2), content=None
):
    _content = Pop_msg(text=_text) if not content else content
    new = Popup(title=_title, content=_content, size_hint=sizehint)
    new.open()


class event:
    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        dispenser: int = 0,
        package: str = "",
    ):
        self.hour_hand = hour
        self.minut_hand = minute
        self.day = day
        self.month = month
        self.year = year

        self.act = [self.year, self.month, self.day, self.hour_hand, self.minut_hand]

        self.package = package
        self.dispenser = dispenser

    def __str__(self):
        return f"""Indhold: {self.package}\nDato: {self.day}/{self.month}/{self.year}\nTid: {self.hour_hand}:{self.minut_hand if len(str(self.minut_hand)) == 2 else f'0{self.minut_hand}'}\nDispenser: {self.dispenser}"""


class TestObject(BoxLayout):
    pass


class MainWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.hour_hand = ObjectProperty(None)
        self.minut_hand = ObjectProperty(None)
        self.day = ObjectProperty(None)
        self.dispenser = ObjectProperty(None)
        self.month = ObjectProperty(None)
        self.year = ObjectProperty(None)
        self.dispensers = 0

        self.package = ObjectProperty(None)

        self.inputs = [
            self.year,
            self.month,
            self.day,
            self.hour_hand,
            self.minut_hand,
            self.package,
        ]

        self.events = []
        self.scroller = ObjectProperty(None)

        self.no_contact = client.no_contact
        self.std_timeout = 1

        Clock.schedule_interval(self.app_update, 1)

    def wipe_text(self):
        self.inputs = [self.hour_hand, self.minut_hand, self.package, self.dispenser]
        for i in self.inputs:
            i.text = ""

    def check_event_relevant(self, current):
        test1 = [get_today(), current]
        test2 = self.sort_events(test1)
        if not [i.act for i in test1] == [i.act for i in test2]:
            return True
        return False

    def sort_events(self, events: list):
        def switch(fir, sec, n=0):
            if fir.act == sec.act:
                return False
            if fir.act[n] > sec.act[n]:
                return True
            if fir.act[n] == sec.act[n]:
                if not n == 5:
                    return switch(fir, sec, n + 1)
                else:
                    False
            return False

        def is_sorted(ev):
            for i in range(len(ev) - 1):
                if switch(ev[i], ev[i + 1]):
                    return False
            return True

        # _events = list(filter(lambda a: a != [], events.copy()))
        _events = events.copy()
        while not is_sorted(_events):
            for i in range(len(_events) - 1):
                if switch(_events[i], _events[i + 1]):
                    _events[i], _events[i + 1] = _events[i + 1], _events[i]

        # for i in range(len(events)-len(_events)):
        #     _events.append([])

        return _events

    def dateCheck(self, date: list):
        try:
            for i in range(len(date)):
                int(date[i])
        except ValueError:
            err = f"""Det valgt tidpunkt:
            {date[2]}/{date[1]}/{date[0]} kl: {date[-2]}:{date[-1]}
            skal udelukkende bestå af tal"""
            show_popup("Indtastnings Fejl", err)
            return False

        for i in range(len(date)):
            date[i] = int(date[i])

        try:
            datetime(
                year=date[0], month=date[1], day=date[2], hour=date[3], minute=date[4]
            )

        except ValueError:
            err = f"""Det valgt tidpunkt:
            {date[2]}/{date[1]}/{date[0]}
            er ikke en rigtig dato"""
            show_popup("Indtastnings Fejl", err)
            return False

        if not (0 <= date[-2] < 24) or not (0 <= date[-1] < 60):
            err = f"""Det valgt tidpunkt:
            kl: {date[-2]}:{date[-1]}
            er ikke et rigtigt tidspunkt på dagen"""
            show_popup("Indtastnings Fejl", err)
            return False

        test1 = [get_today(), event(date[0], date[1], date[2], date[3], date[4])]
        test2 = self.sort_events(test1)
        if not [i.act for i in test1] == [i.act for i in test2]:
            err = f"""Det valgt tidpunkt:
            {date[2]}/{date[1]}/{date[0]} kl: {date[-2]}:{date[-1]}
            ligger i fortiden..."""
            show_popup("Indtastnings Fejl", err)
            return False
        return True

    def dispenserCheck(self):
        if self.dispenser.text == "":
            err = f"""Ingen dispensor valgt"""
            show_popup("Indtastnings Fejl", err)
            return False

        elif not (0 < int(self.dispenser.text) <= self.dispensers):
            err = f"""Dispenser {self.dispenser.text} findes ikke"""
            show_popup("Indtastnings Fejl", err)
            return False

        return True

    def app_update(self, dt):
        for i in range(len(self.events)):
            if self.check_event_relevant(self.events[i]):
                content = (
                    f"[b]Inhold[/b]: {self.events[i].package}"
                    if self.events[i].package != ""
                    else ""
                )
                show_popup(
                    "Aktivering",
                    f"Aktiverer...\nÅbner for dispenser {self.events[i].dispenser}\n{content}",
                )
        self.events = [e for e in self.events if not self.check_event_relevant(e)]
        self.events = self.sort_events(self.events)
        self.update_EventHolders()

    def update_EventHolders(self):
        self.scroller.clear_elements()
        self.events = self.sort_events(self.events)
        if self.events == []:
            self.scroller.add_element(Empty_object())
        else:
            for i in self.events:
                holder = EventHolder()
                holder.label_text = f"""[b]Indhold[/b]: {i.package}\n[b]Dato[/b]: {i.day}/{i.month}/{i.year}\n[b]Tid[/b]: {i.hour_hand}:{i.minut_hand if len(str(i.minut_hand)) == 2 else f'0{i.minut_hand}'}\n[b]Dispenser[/b]: {i.dispenser}"""
                holder.q_number = self.events.index(i)
                self.scroller.add_element(holder)

            for child in self.scroller.children:
                child.update()

    def update_esp(self):
        events_message = "r"
        for event in self.events:
            events_message += f"|{event.package} ,{event.year},{event.month},{event.day},{event.hour_hand},{event.minut_hand},{event.dispenser}|"

        print(events_message)
        bridge.send_message(events_message)
        status = reciver.anticipate(self.std_timeout)
        show_popup("Status", status)
        return status

    def instant_release_esp(self):
        q_pop = BoxPick_pop()
        q_pop.num_boxes = self.dispensers
        q_pop.open()

    def reed_esp(self):
        bridge.send_message("g")

        message = reciver.anticipate(self.std_timeout)
        if message == self.no_contact:
            show_popup("Ingen kontakt", self.no_contact)
            return
        print(message)

        self.dispensers = int(message[-1])
        print(f"Dispensers: {self.dispensers}")
        new_events = message.split("|")[:-1]
        for i in new_events:
            new_events.remove("")
        print(new_events)

        for i in range(len(new_events)):
            new_events[i] = [new_events[i]]
        print(new_events)
        self.events = []

        for index in new_events:
            _event = index[0].split(",")
            print(_event)

            self.events.append(
                event(
                    year=int(_event[1]),
                    month=int(_event[2]),
                    day=int(_event[3]),
                    hour=int(_event[4]),
                    minute=int(_event[5]),
                    dispenser=int(_event[6]),
                    package=_event[0],
                )
            )

        print("events: ")
        for i in self.events:
            print(i)

    def add_event(self):
        new_event = event(
            self.year.text,
            self.month.text,
            self.day.text,
            self.hour_hand.text,
            self.minut_hand.text,
            self.dispenser.text,
            self.package.text,
        )
        prev_events = self.events.copy()
        print(prev_events)
        if not self.dateCheck(new_event.act):
            return
        if not self.dispenserCheck():
            return
        self.events.append(new_event)

        self.events = self.sort_events(self.events)

        update = self.update_esp()

        if update == self.no_contact:
            self.events = prev_events

        for i in self.events:
            print(i)

        self.update_EventHolders()
        # self.wipe_text()

    def delete_event(self, event):
        prev_events = self.events.copy()
        self.events.pop(event)
        self.events = self.sort_events(self.events)
        if self.update_esp() == self.no_contact:
            self.events = prev_events
        self.scroller.pop_element(0)
        self.update_EventHolders()


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


sketch = Builder.load_file("sketch.kv")


class sketchApp(App):
    def build(self):
        return sketch

    def on_start(self):
        main_window = self.root.get_screen("main")
        today = get_today()
        main_window.ids.hourHand.text = str(today.hour_hand)
        main_window.ids.minutHand.text = str(today.minut_hand)
        main_window.ids.day.text = str(today.day)
        main_window.ids.month.text = str(today.month)
        main_window.ids.year.text = str(today.year)
        main_window.reed_esp()
        main_window.update_EventHolders()


scale = 45
if __name__ == "__main__":
    bridge = client.bridge()
    reciver = bridge.reciver(bridge)
    Window.size = (9 * scale, 20 * scale)
    sketchApp().run()
