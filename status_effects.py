from foundational import StatusEffect, Character
from typing import override, Final
from types import TracebackType
from ansi_codes import *

type TypeET = type[BaseException] | None
type TypeEV = BaseException | None
type TypeETb = TracebackType | None

# -------------------------------------

class Invincible(StatusEffect):

    @override
    def __enter__(self) -> None:
        self.add_to_character()

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None
    
    @override
    def __str__(self) -> str:
        return "Invincible"

# -------------------------------------

class DoubleDamage(StatusEffect):

    @override
    def __enter__(self) -> None:
        self.add_to_character()
        self.character.damage *= 2

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        self.character.damage //= 2
        return None
    
    @override
    def __str__(self) -> str:
        return "Double Damage"

# -------------------------------------

class DamageReduction(StatusEffect):

    @override
    def __init__(self, character: Character, reduce_amount: int) -> None:
        super().__init__(character)
        self.reduce_amount: int = reduce_amount

    @override
    def __enter__(self) -> None:
        self.add_to_character()
        self.character.shield += self.reduce_amount

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        self.character.shield -= self.reduce_amount
        return None
    
    @override
    def __str__(self) -> str:
        return f"Damage Reduction by {ANSI_BLUE}{self.reduce_amount}{ANSI_NORMAL}"

# -------------------------------------

class Regenerate(StatusEffect):

    @override
    def __init__(self, character: Character, turns: int, amount_per_turn: int) -> None:
        super().__init__(character, turns)
        self.amount_per_turn: int = amount_per_turn

    @override
    def __enter__(self) -> None:
        self.add_to_character()
        self.character.health += self.amount_per_turn
    
    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None
    
    @override
    def __str__(self) -> str:
        turns: str = "turns" if self.turns >= 2 else "turn"
        return f"Regenerate {ANSI_BLUE}{self.amount_per_turn}{ANSI_NORMAL} health per turn " \
               f"for {ANSI_BLUE}{self.turns}{ANSI_NORMAL} {turns}"

# -------------------------------------

class Stun(StatusEffect):

    @override
    def __enter__(self) -> None:
        self.add_to_character()

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None
    
    @override
    def __str__(self) -> str:
        return "Stun"

# -------------------------------------

class StunBlade(StatusEffect):

    @override
    def __enter__(self) -> None:
        self.add_to_character()

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None
    
    @override
    def give_next_attack_target(self) -> StatusEffect | None:
        return Stun(self.character)

    @override
    def __str__(self) -> str:
        return "Stun Blade (next attack gives the target the Stun effect)"

# -------------------------------------

class Poison(StatusEffect):

    @override
    def __init__(self, character: Character, turns: int, amount_per_turn: int) -> None:
        super().__init__(character, turns)
        self.amount_per_turn: int = amount_per_turn

    @override
    def __enter__(self) -> None:
        self.add_to_character()
        self.character.health -= self.amount_per_turn
    
    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None
    
    @override
    def __str__(self) -> str:
        turns: str = "turns" if self.turns >= 2 else "turn"
        return f"Poison (lose {ANSI_BLUE}{self.amount_per_turn}{ANSI_NORMAL} health per turn " \
               f"for {ANSI_BLUE}{self.turns}{ANSI_NORMAL} {turns})"

# -------------------------------------

class PoisonBlade(StatusEffect):

    @override
    def __init__(self, character: Character, poison_turns: int, poison_per_turn: int) -> None:
        super().__init__(character)
        self.poison_turns: int = poison_turns
        self.poison_per_turn: int = poison_per_turn

    @override
    def __enter__(self) -> None:
        self.add_to_character()

    @override
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        self.remove_from_character_if_expired()
        return None

    @override
    def give_next_attack_target(self) -> StatusEffect | None:
        return Poison(self.character, self.poison_turns, self.poison_per_turn)

    @override
    def __str__(self) -> str:
        turns: str = "turns" if self.poison_turns >= 2 else "turn"
        return "Poison Blade (next attack gives the target the Poison effect for " \
               f"{ANSI_BLUE}{self.poison_per_turn}{ANSI_NORMAL} per turn for " \
               f"{ANSI_BLUE}{self.poison_turns}{ANSI_NORMAL} {turns})"

# -------------------------------------

ALL_STATUS_EFFECTS: Final[list[type[StatusEffect]]] = [
    Invincible, DoubleDamage, DamageReduction, Regenerate, StunBlade, PoisonBlade
]