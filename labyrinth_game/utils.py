import math

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
    """Показывает список доступных команд"""
    print("\nДоступные команды:")
    for command, description in constants.COMMANDS.items():
        print(f"  {command:<16} - {description}")


def process_command(game_state, command):
    """Обрабатывает команды пользователя"""
    parts = command.split(' ', 1)
    main_command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""
    
    directions = ['north', 'south', 'east', 'west', 'up', 'down']
    if main_command in directions:
        main_command = 'go'
        argument = parts[0]
    
    match main_command:
        case 'осмотреться' | 'look':
            describe_current_room(game_state)
        
        case 'инвентарь' | 'inventory' | 'inv':
            player_actions.show_inventory(game_state)
        
        case 'идти' | 'go':
            if argument:
                old_room = game_state['current_room']
                success = player_actions.move_player(game_state, argument)
                if success and game_state['current_room'] != old_room:
                    random_event(game_state)
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


def pseudo_random(seed, modulo):
    """Генерирует псевдослучайное число на основе синуса"""
    sin_value = math.sin(seed * 12.9898)
    multiplied = sin_value * 43758.5453
    
    fractional = multiplied - math.floor(multiplied)
    
    result = int(fractional * modulo)
    return result


def trigger_trap(game_state):
    """Активирует ловушку с негативными последствиями для игрока"""
    print("\n💀 Ловушка активирована! Пол стал дрожать...")
    
    inventory = game_state['player_inventory']
    
    if inventory:
        item_index = pseudo_random(game_state['steps_taken'], len(inventory))
        lost_item = inventory.pop(item_index)
        print(f"💥 В суматохе вы потеряли: {lost_item}!")
        
        if inventory:
            print(f"📦 В вашем инвентаре осталось: {len(inventory)} предметов")
        else:
            print("📦 Ваш инвентарь теперь пуст!")
    else:
        print("💥 Вы получили удар от ловушки!")
        damage_chance = pseudo_random(game_state['steps_taken'], 10)
        
        if damage_chance < 3:
            print("❌ Критическое попадание! Игра окончена.")
            game_state['game_over'] = True
        else:
            print("✅ Вам повезло! Вы уцелели, но будьте осторожнее.")


def random_event(game_state):
    """Случайные события во время перемещения игрока"""
    event_chance = pseudo_random(game_state['steps_taken'], 10)
    
    if event_chance == 0:
        event_type = pseudo_random(game_state['steps_taken'] + 1, 3)
        
        current_room = game_state['current_room']
        room_data = constants.ROOMS.get(current_room, {})
        inventory = game_state['player_inventory']
        
        if event_type == 0:
            print("\n✨ Вы заметили что-то блестящее на полу...")
            print("💰 Вы нашли монетку!")
            if 'items' not in room_data:
                room_data['items'] = []
            room_data['items'].append('coin')
            
        elif event_type == 1:
            print("\n👂 Вы слышите странный шорох в темноте...")
            if 'sword' in inventory:
                print("⚔️ Вы достаете меч, и существо убегает!")
            else:
                print("😨 Вам стало не по себе...")
                
        elif event_type == 2:
            print("\n⚠️ Вы чувствуете, что наступили на подозрительную плиту...")
            if current_room == 'trap_room' and 'torch' not in inventory:
                print("🔦 Без факела вы не заметили ловушку вовремя!")
                trigger_trap(game_state)
            else:
                print("✅ К счастью, ловушка оказалась неактивной.")


def solve_puzzle(game_state):
    """Функция решения загадок с альтернативными ответами"""
    current_room = game_state['current_room']
    room_data = constants.ROOMS.get(current_room, {})
    puzzle = room_data.get('puzzle')
    
    if not puzzle:
        print("Загадок здесь нет.")
        return False
    
    question, correct_answer = puzzle
    
    print(f"\n{question}")
    user_answer = player_actions.get_input("Ваш ответ: ").strip().lower()
    
    is_correct = False
    if correct_answer in constants.PUZZLE_ALTERNATIVES:
        alternatives = constants.PUZZLE_ALTERNATIVES[correct_answer]
        is_correct = user_answer in alternatives
    else:
        is_correct = user_answer == correct_answer.lower()
    
    if is_correct:
        print("🎉 Верно! Загадка решена.")
        room_data['puzzle'] = None
        
        if current_room == 'hall':
            print("🎁 Пьедестал открывается! Вы получаете 'silver_key'!")
            game_state['player_inventory'].append('silver_key')
        elif current_room == 'trap_room':
            print("🎁 Ловушка отключена! Теперь вы можете безопасно пройти.")
        elif current_room == 'library':
            print("🎁 Свиток превращается в 'magic_scroll'!")
            game_state['player_inventory'].append('magic_scroll')
        elif current_room == 'garden':
            print("🎁 Из фонтана появляется 'crystal_shard'!")
            game_state['player_inventory'].append('crystal_shard')
        elif current_room == 'observatory':
            print("🎁 Телескоп активируется! Вы находите 'star_key'!")
            game_state['player_inventory'].append('star_key')
        elif current_room == 'forge':
            print("🎁 Вы создали 'master_key'!")
            game_state['player_inventory'].append('master_key')
        elif current_room == 'maze_center':
            print("🎁 Алтарь светится! Вы получаете 'ancient_artifact'!")
            game_state['player_inventory'].append('ancient_artifact')
        else:
            print("🎉 Вы чувствуете прогресс в исследовании лабиринта.")
        
        return True
    else:
        print("❌ Неверно.")
        if current_room == 'trap_room':
            print("💀 Неправильный ответ активирует ловушку!")
            trigger_trap(game_state)
        else:
            print("Попробуйте снова.")
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
    
    if 'rusty_key' in game_state['player_inventory']:
        print("🔑 Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        items.remove('treasure_chest')
        print("🎊 В сундуке сокровище! Вы победили!")
        game_state['game_over'] = True
        return True
    
    print("🔒 Сундук заперт. У вас нет подходящего ключа.")
    choice_input = "Попробовать ввести код? (да/нет): "
    choice = player_actions.get_input(choice_input).strip().lower()
    
    if choice in ['да', 'yes', 'y']:
        puzzle = room_data.get('puzzle')
        if puzzle:
            question, correct_answer = puzzle
            print(f"\n{question}")
            user_code = player_actions.get_input("Введите код: ").strip()
            
            is_correct = False
            if correct_answer in constants.PUZZLE_ALTERNATIVES:
                alternatives = constants.PUZZLE_ALTERNATIVES[correct_answer]
                is_correct = user_code in alternatives
            else:
                is_correct = user_code.lower() == correct_answer.lower()
            
            if is_correct:
                print("🎉 Код принят! Сундук открывается!")
                items.remove('treasure_chest')
                print("🎊 В сундуке сокровище! Вы победили!")
                game_state['game_over'] = True
                return True
            else:
                print("❌ Неверный код. Сундук остается запертым.")
                return False
        else:
            print("❌ Нет возможности ввести код. Нужен ключ.")
            return False
    else:
        print("Вы отступаете от сундука.")
        return False