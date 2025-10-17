#!/usr/bin/env python3
from labyrinth_game import constants, player_actions, utils
    
def main():
    print("Добро пожаловать в Лабиринт сокровищ!")

    game_state = {
        'player_inventory': [], 
        'current_room': 'entrance',
        'game_over': False,
        'steps_taken': 0
    }

    utils.describe_current_room(game_state)

    while not game_state['game_over']:
        command = player_actions.get_input("\nЧто вы хотите сделать? ").strip().lower()
        if command == "quit":
            print("Спасибо за игру! До свидания!")
            break
        utils.process_command(game_state, command)
    if game_state['game_over']:
        print(f"\nИгра завершена! Вы сделали {game_state['steps_taken']} шагов.")
        print("Надеемся, вам понравилось приключение!")



if __name__ == "__main__":
    main()