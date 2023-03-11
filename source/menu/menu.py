from menu_states import (
    MainMenu,
    BrowseMenu,
    RebootMenu,
    SeekMenu,
    SleepTimerMenu,
    AlarmMenu,
    ShutdownMenu
)


class MenuStateMachine:
    def __init__(self):
        self.current_state = None
        self.main_menu()

    def main_menu(self):
        self.current_state = MainMenu()
        self.current_state.run()

    def go_back(self):
        self.current_state = self.current_state.previous()
        self.current_state.run()


class Menu:
    def __init__(self) -> None:
        self.state = MenuStateMachine()

        # NAV_ARRAY_NAME, NAV_ARRAY_URI, NAV_ARRAY_TYPE, NAV_ARRAY_SERVICE = [], [], [], []

        # NAV_DICT = {"MARKER": 0, "LISTMAX": int(OBJ['listmax']['value']), "LISTSTART": 0, "LISTRESULT": 0}


    def show_menu(self, menu):
        if VOLUMIO_DICT['MODE'] == 'player':
            VOLUMIO_DICT['MODE'] = 'menu'
            emit_action = ['setSleep', {'enabled': 'true', 'time': strftime("%H:%M", gmtime(OBJ['sleeptimer']['value']*60))}]
            NAV_ARRAY_NAME = [OBJ_TRANS['DISPLAY']['MUSICSELECTION'], OBJ_TRANS['DISPLAY']['SEEK'], OBJ_TRANS['DISPLAY']['PREVNEXT'], 'Sleeptimer ' + str(OBJ['sleeptimer']['value']) + 'M', OBJ_TRANS['DISPLAY']['SHUTDOWN'], OBJ_TRANS['DISPLAY']['REBOOT']]
            NAV_ARRAY_URI = ['', 'seek', 'prevnext', emit_action, 'shutdown', 'reboot']
            NAV_ARRAY_TYPE = ['', 'seek', 'prevnext', 'emit', 'emit', 'emit']
            NAV_DICT['LISTRESULT'] = 6
            display_stuff(IMAGE_DICT['BG_DEFAULT'], NAV_ARRAY_NAME, NAV_DICT['MARKER'], NAV_DICT['LISTSTART'])


