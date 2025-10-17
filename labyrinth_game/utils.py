from . import constants, player_actions

def describe_current_room(game_state):
    """Выводит описание текущей комнаты"""
    current_room = game_state['current_room']
    room_data = constants.ROOMS.get(current_room, {})
    
    print(f"\n== {current_room.upper()} ==")
    
    print(room_data.get('description', 'Неизвестная комната'))
    
    items = room_data.get('items', [])
    if items:
        print("\nЗаметные предметы:", ", ".join(items))
    
    exits = room_data.get('exits', {})
    if exits:
        print("\nВыходы:", ", ".join(exits.keys()))
    
    if room_data.get('puzzle'):
        print("\nКажется, здесь есть загадка (используйте команду solve).")

def show_help():
    print("\nДоступные команды:")
    print("  go <direction>  - перейти в направлении (north/south/east/west)")
    print("  look            - осмотреть текущую комнату")
    print("  take <item>     - поднять предмет")
    print("  use <item>      - использовать предмет из инвентаря")
    print("  inventory       - показать инвентарь")
    print("  solve           - попытаться решить загадку в комнате")
    print("  quit            - выйти из игры")
    print("  help            - показать это сообщение") 

def process_command(game_state, command):
    """Обрабатывает команды пользователя"""
    parts = command.split(' ', 1)
    main_command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""
    
    match main_command:
        case 'осмотреться' | 'look':
            describe_current_room(game_state)
        
        case 'инвентарь' | 'inventory' | 'inv':
            player_actions.show_inventory(game_state)
        
        case 'идти' | 'go':
            if argument:
                player_actions.move_player(game_state, argument)
            else:
                print("Укажите направление. Например: 'идти north'")
        
        case 'взять' | 'take':
            if argument:
                player_actions.take_item(game_state, argument)
            else:
                print("Укажите предмет. Например: 'взять torch'")
        
        case 'использовать' | 'use':
            if argument:
                player_actions.use_item(game_state, argument)
            else:
                print("Укажите предмет. Например: 'использовать torch'")
        
        case 'решить' | 'solve':
            current_room = game_state['current_room']
            if current_room == 'treasure_room':
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        
        case 'открыть' | 'open':
            if game_state['current_room'] == 'treasure_room':
               attempt_open_treasure(game_state)
            else:
                print("Нечего открывать здесь.")
        
        case 'помощь' | 'help':
            show_help()
        
        case 'выход' | 'exit' | 'quit':
            print("Спасибо за игру! До свидания!")
            game_state['game_over'] = True
        
        case _:
            print("Неизвестная команда. Введите 'помощь' для списка команд.")

def solve_puzzle(game_state):
    """Функция решения загадок"""
    current_room = game_state['current_room']
    room_data = constants.ROOMS.get(current_room, {})
    puzzle = room_data.get('puzzle')
    
    if not puzzle:
        print("Загадок здесь нет.")
        return False
    
    question, correct_answer = puzzle
    
    print(f"\n{question}")
    user_answer = player_actions.get_input("Ваш ответ: ").strip()
    
    if user_answer.lower() == correct_answer.lower():
        print("Верно! Загадка решена.")
        
        room_data['puzzle'] = None
        
        if current_room == 'hall':
            print("Пьедестал открывается! Вы получаете 'silver_key'!")
            game_state['player_inventory'].append('silver_key')
        elif current_room == 'trap_room':
            print("Ловушка отключена! Теперь вы можете безопасно пройти.")
        elif current_room == 'library':
            print("Свиток превращается в 'magic_scroll'!")
            game_state['player_inventory'].append('magic_scroll')
        elif current_room == 'treasure_room':
            print("Вы получаете доступ к сундуку!")
        else:
            print("Вы чувствуете, что достигли прогресса в исследовании лабиринта.")
        
        return True
    else:
        print("Неверно. Попробуйте снова.")
        return False
    
def attempt_open_treasure(game_state):
    """Функция открытия сундука с сокровищами"""
    current_room = game_state['current_room']
    
    if current_room != 'treasure_room':
        print("Здесь нет сундука с сокровищами.")
        return False
    
    room_data = constants.ROOMS.get(current_room, {})
    items = room_data.get('items', [])
    
    if 'treasure_chest' not in items:
        print("Сундук с сокровищами уже открыт!")
        return True
    
    # Проверка наличия ключа
    if 'treasure_key' in game_state['player_inventory']:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        items.remove('treasure_chest')
        print("В сундуке сокровище! Вы победили!")
        game_state['game_over'] = True
        return True
    
    # Если ключа нет, предлагаем ввести код
    print("Сундук заперт. У вас нет подходящего ключа.")
    choice = player_actions.get_input("Попробовать ввести код? (да/нет): ").strip().lower()
    
    if choice in ['да', 'yes', 'y']:
        puzzle = room_data.get('puzzle')
        if puzzle:
            question, correct_answer = puzzle
            print(f"\n{question}")
            user_code = player_actions.get_input("Введите код: ").strip()
            
            if user_code.lower() == correct_answer.lower():
                print("Код принят! Сундук открывается!")
                items.remove('treasure_chest')
                print("В сундуке сокровище! Вы победили!")
                game_state['game_over'] = True
                return True
            else:
                print("Неверный код. Сундук остается запертым.")
                return False
        else:
            print("Нет возможности ввести код. Нужен ключ.")
            return False
    else:
        print("Вы отступаете от сундука.")
        return False