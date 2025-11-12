from foundational import Character, MultipleStatusEffects
from status_effects import *
from random_select import get_n_random

LINE_SEPARATOR: Final[str] = f"\n{ANSI_MAGENTA}{100 * '-'}{ANSI_NORMAL}"

# ----------------------------------------------

def get_user_choice(character: Character, num_choices: int = 3) -> StatusEffect | None:

    def is_valid(choice: str) -> bool:
        if choice == "concede":
            return True
        try:
            choice_num: int = int(choice)
            return 1 <= choice_num <= num_choices
        except ValueError:
            return False

    choices: list[StatusEffect | None] = get_n_random(character, num_choices)
    print(f"\n{character.name}, your choices are:\n")

    for index, choice in enumerate(choices):
        print(f"{ANSI_BLUE}{index + 1}{ANSI_NORMAL}: ", end = "")
        if choice is None:
            print(f"No status effect {ANSI_BLUE}:({ANSI_NORMAL}")
        else:
            print(choice)

    entered: str = input("\nEnter your choice now " \
                         f"(or {ANSI_RED}concede{ANSI_NORMAL}): {ANSI_MAGENTA}")
    print(ANSI_NORMAL, end = "")
    while not is_valid(entered):
        entered = input(f"Not accepted. Try again: {ANSI_MAGENTA}")
        print(ANSI_NORMAL, end = "")

    if entered == "concede":
        print(f"\n{character.name} has conceded!")
        exit()
    entered_choice: int = int(entered)

    return choices[entered_choice - 1]

# ----------------------------------------------

def play() -> None:

    player_1: Character = Character(f"Player {ANSI_YELLOW}1{ANSI_NORMAL}", 10, 100)
    player_2: Character = Character(f"Player {ANSI_YELLOW}2{ANSI_NORMAL}", 10, 100)
    turn: int = 1

    print(f"\n{ANSI_CYAN}Before the fight starts:{ANSI_NORMAL}")
    for player in [player_1, player_2]:
        print(player)
    print(LINE_SEPARATOR)

    while player_1.alive and player_2.alive:

        print(f"\nTurn {ANSI_BLUE}{turn}{ANSI_NORMAL}:")
        turn += 1

        print(f"\n{ANSI_CYAN}Status effects carried over:{ANSI_NORMAL}")
        if len(player_1.effects) == 0 and len(player_2.effects) == 0:
            print("None")
        for player in [player_1, player_2]:
            for effect in player.effects:
                print(f"{player.name}: {effect}")

        player_1_choice: StatusEffect | None = None
        player_2_choice: StatusEffect | None = None
        if turn % 2 == 0:
            player_1_choice = get_user_choice(player_1)
            player_2_choice = get_user_choice(player_2)
        else:
            player_2_choice = get_user_choice(player_2)
            player_1_choice = get_user_choice(player_1)

        status_effects: list[StatusEffect] = []
        if player_1_choice is not None: status_effects.append(player_1_choice)
        if player_2_choice is not None: status_effects.append(player_2_choice)

        with player_1.get_multiple_status_effects() & \
             player_2.get_multiple_status_effects() & \
             MultipleStatusEffects(status_effects):
            
            print(f"\n{ANSI_CYAN}Active status effects this turn:{ANSI_NORMAL}")
            if len(player_1.effects) == 0 and len(player_2.effects) == 0:
                print("None")
            for player in [player_1, player_2]:
                for effect in player.effects:
                    print(f"{player.name}: {effect}")

            print(f"\n{ANSI_CYAN}Before combat:{ANSI_NORMAL}")
            for player in [player_1, player_2]:
                print(player)

            player_1.attack(player_2)
            player_2.attack(player_1)

            print(f"\n{ANSI_CYAN}After combat:{ANSI_NORMAL}")
            for player in [player_1, player_2]:
                print(player)

            print(LINE_SEPARATOR)

        for player in [player_1, player_2]:
            player.activate_inactive_effects()

    final_turns: str = f"{ANSI_BLUE}{turn - 1}{ANSI_NORMAL} {"turns" if turn - 1 >= 2 else "turn"}"
    if player_1.alive and not player_2.alive:
        print(f"\n{player_1.name} won after {final_turns}!")
    elif player_2.alive and not player_1.alive:
        print(f"\n{player_2.name} won after {final_turns}!")
    else:
        print(f"\n{player_1.name} and {player_2.name} destroyed each other after {final_turns}!")

# ----------------------------------------------

if __name__ == "__main__":
    play()