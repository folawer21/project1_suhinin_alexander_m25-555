from . import constants, utils


def show_inventory(game_state):
    """Отображает содержимое инвентаря игрока"""
    inventory = game_state['player_inventory']
    
    if not inventory:
        print("\nВаш инвентарь пуст.")
    else:
        print(f"\nВаш инвентарь ({len(inventory)} предметов):")
        for i, item in enumerate(inventory, 1):
            print(f"  {i}. {item}")


def get_input(prompt="> "):
    try:
        user_input = input(prompt)
        # Принудительно кодируем и декодируем для исправления проблем с кодировкой
        user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"
    except Exception as e:
        print(f"\nОшибка ввода: {e}. Пожалуйста, попробуйте еще раз.")
        return get_input(prompt)
    

def move_player(game_state, direction):
    """Перемещает игрока в указанном направлении"""
    current_room = game_state['current_room']
    room_data = constants.ROOMS.get(current_room, {})
    exits = room_data.get('exits', {})
    
    if direction in exits:
        target_room = exits[direction]
        
        # Проверка на переход в treasure_room
        if target_room == 'treasure_room':
            if 'rusty_key' in game_state['player_inventory']:
                msg = "🔑 Вы используете найденный ключ, чтобы открыть путь."
                print(msg)
                game_state['current_room'] = target_room
                game_state['steps_taken'] += 1
                utils.describe_current_room(game_state)
                return True
            else:
                print("🔒 Дверь заперта. Нужен ключ, чтобы пройти дальше.")
                return False
        
        # Обычное перемещение для других комнат
        game_state['current_room'] = target_room
        game_state['steps_taken'] += 1
        print(f"\nВы переместились {direction}.")
        utils.describe_current_room(game_state)
        return True
    else:
        print("Нельзя пойти в этом направлении.")
        return False
    

def take_item(game_state, item_name):
    """Позволяет игроку подобрать предмет из комнаты"""
    current_room = game_state['current_room']
    room_data = constants.ROOMS.get(current_room, {})
    items = room_data.get('items', [])
    
    if item_name in items:
        game_state['player_inventory'].append(item_name)
        items.remove(item_name)
        print(f"Вы подняли: {item_name}")
        return True
    else:
        print("Такого предмета здесь нет.")
        return False
    

def use_item(game_state, item_name):
    """Позволяет игроку использовать предмет из инвентаря"""
    inventory = game_state['player_inventory']
    
    if item_name not in inventory:
        print("У вас нет такого предмета.")
        return False
    
    if item_name == 'torch':
        msg = "🔥 Вы зажгли факел. Стало светлее."
        print(msg)
    
    elif item_name == 'sword':
        msg = "⚔️ Вы почувствовали уверенность, держа меч в руках."
        print(msg)
    
    elif item_name == 'bronze_box':
        if 'small_key' not in inventory:
            msg = "🎁 Вы открыли бронзовую шкатулку. Нашли ключ!"
            print(msg)
            game_state['player_inventory'].append('small_key')
        else:
            print("📦 Шкатулка уже пуста.")
    
    elif item_name == 'ancient_book':
        msg = "📖 Вы читаете древнюю книгу о магии лабиринта."
        print(msg)
    
    elif item_name == 'healing_potion':
        print("🧪 Вы выпили зелье лечения. Вы чувствуете прилив сил!")

    else:
        print(f"Вы не знаете, как использовать {item_name}.")
        return False
    
    return True