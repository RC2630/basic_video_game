from types import TracebackType
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any
from copy import deepcopy
from ansi_codes import *

type TypeET = type[BaseException] | None
type TypeEV = BaseException | None
type TypeETb = TracebackType | None

# -------------------------------------

@dataclass
class Character:

    name: str
    damage: int
    health: int
    shield: int = 0
    effects: list[StatusEffect] = field(default_factory = list)

    def attack(self, other: Character) -> None:
        if not (other.has_active_effect("Invincible") or self.has_active_effect("Stun")):
            other.health -= max(self.damage - other.shield, 0)
            for effect in self.effects:
                if not effect.active:
                    continue
                if (give_effect_ref := effect.give_next_attack_target()) is not None:
                    give_effect: StatusEffect = deepcopy(give_effect_ref)
                    give_effect.character = other
                    give_effect.add_to_character(active = False)

    @property
    def alive(self) -> bool:
        return self.health > 0
    
    def __str__(self) -> str:
        return f"{self.name}: {ANSI_GREEN}{self.damage}{ANSI_NORMAL} damage, " \
               f"{ANSI_RED}{self.health}{ANSI_NORMAL} health " \
               f"({ANSI_BLUE}{self.shield}{ANSI_NORMAL} shield)"

    def get_effect_names(self) -> list[str]:
        return [type(effect).__name__ for effect in self.effects]
    
    def find_effect(self, effect_name: str) -> StatusEffect:
        return self.effects[self.get_effect_names().index(effect_name)]
    
    def has_effect(self, effect_name: str) -> bool:
        return effect_name in self.get_effect_names()
    
    def has_active_effect(self, effect_name: str) -> bool:
        if not self.has_effect(effect_name):
            return False
        effect: StatusEffect = self.find_effect(effect_name)
        return effect.active
    
    def remove_effect(self, effect_name: str) -> None:
        del self.effects[self.get_effect_names().index(effect_name)]

    def get_multiple_status_effects(self) -> MultipleStatusEffects:
        return MultipleStatusEffects(self.effects)
    
    def activate_inactive_effects(self) -> None:
        active_effects: list[StatusEffect] = \
            [effect for effect in self.effects if effect.active]
        inactive_effects: list[StatusEffect] = \
            [effect for effect in self.effects if not effect.active]
        self.effects = active_effects.copy()
        for effect in inactive_effects:
            assert self.name == effect.character.name
            effect.add_to_character(active = True) # removes original if present

    def update_stats_after_each_turn(self) -> None:
        self.damage += 1 # makes gameplay more high-stakes as the game drags on

# -------------------------------------

class StatusEffect(ABC):

    def __init__(self, character: Character, turns: int = 1) -> None:
        self.character: Character = character
        self.turns: int = turns
        self.active: bool = True

    def __and__(self, other: StatusEffect | MultipleStatusEffects) -> MultipleStatusEffects:
        return MultipleStatusEffects.from_orig_and_new(self, other)
    
    @property
    def name(self) -> str:
        return type(self).__name__
    
    def __repr__(self) -> str:
        return f"{self.name}({self.character.name}, {self.turns})"
    
    def __eq__(self, other: Any) -> bool:
        assert isinstance(other, StatusEffect)
        return self.name == other.name and self.character.name == other.character.name
    
    def add_to_character(self, active: bool = True) -> None:
        self.active = active
        if self in self.character.effects:
            stored_effect: StatusEffect = self.character.effects[self.character.effects.index(self)]
            if stored_effect.active == self.active:
                self.character.effects.remove(self)
        self.character.effects.append(self)

    def remove_from_character_if_expired(self) -> None:
        self.turns -= 1
        if self.turns == 0:
            self.character.effects.remove(self)

    @abstractmethod
    def __enter__(self) -> None:
        ...

    @abstractmethod
    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

    def give_next_attack_target(self) -> StatusEffect | None:
        return None

# -------------------------------------

class MultipleStatusEffects:

    def __init__(self, effects: list[StatusEffect]) -> None:
        self.effects: list[StatusEffect] = effects

    def __and__(self, other: StatusEffect | MultipleStatusEffects) -> MultipleStatusEffects:
        return MultipleStatusEffects.from_orig_and_new(self, other)
    
    @staticmethod
    def from_orig_and_new(
        orig_effects: StatusEffect | MultipleStatusEffects,
        new_effects: StatusEffect | MultipleStatusEffects
    ) -> MultipleStatusEffects:
        orig_effects_list: list[StatusEffect] = \
            [orig_effects] if isinstance(orig_effects, StatusEffect) else orig_effects.effects
        new_effects_list: list[StatusEffect] = \
            [new_effects] if isinstance(new_effects, StatusEffect) else new_effects.effects
        all_effects_list: list[StatusEffect] = orig_effects_list.copy()
        for effect in new_effects_list:
            try:
                all_effects_list.remove(effect)
            except ValueError:
                pass
            all_effects_list.append(effect)
        return MultipleStatusEffects(all_effects_list)

    def __enter__(self) -> None:
        for effect in self.effects:
            effect.__enter__()

    def __exit__(self, exc_type: TypeET, exc_val: TypeEV, exc_tb: TypeETb) -> bool | None:
        returns: list[bool] = []
        for effect in reversed(self.effects):
            returns.append(bool(effect.__exit__(exc_type, exc_val, exc_tb)))
        return all(returns) # propagate exception if any status effect wants to propagate