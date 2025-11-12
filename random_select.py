from random import randint
from status_effects import *

NUM_DUMMIES: Final[int] = round(len(ALL_STATUS_EFFECTS) / 2)

def get_one_random(character: Character) -> StatusEffect | None:
    random_index: int = randint(0, len(ALL_STATUS_EFFECTS) + NUM_DUMMIES - 1)
    if random_index >= len(ALL_STATUS_EFFECTS):
        return None
    effect_type: type[StatusEffect] = ALL_STATUS_EFFECTS[random_index]
    if effect_type in [Invincible, DoubleDamage, StunBlade]:
        return effect_type(character)
    elif effect_type is DamageReduction:
        reduce_amount: int = randint(5, 15)
        return DamageReduction(character, reduce_amount)
    elif effect_type is Regenerate:
        regen_amount: int = randint(3, 7)
        regen_turns: int = randint(2, 4)
        return Regenerate(character, regen_turns, regen_amount)
    elif effect_type is PoisonBlade:
        poison_amount: int = randint(2, 4)
        poison_turns: int = randint(2, 4)
        return PoisonBlade(character, poison_turns, poison_amount)
    else:
        raise RuntimeError("should not reach here")
    
def get_n_random(character: Character, n: int) -> list[StatusEffect | None]:
    return [get_one_random(character) for i in range(n)]