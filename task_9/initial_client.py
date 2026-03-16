from client_cleaner_api import ClientCleanerApi

cleaner_api = ClientCleanerApi()

cleaner_api.activate_cleaner((
    'move 100',
    'turn -90',
    'set soap',
    'start',
    'move 50',
    'stop'
    ))

print (cleaner_api.get_x(), 
    cleaner_api.get_y(), 
    cleaner_api.get_angle(), 
    cleaner_api.get_state())