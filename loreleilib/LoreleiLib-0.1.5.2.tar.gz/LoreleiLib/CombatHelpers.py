from LoreleiLib.Statistics import AttributeSet


def CalculatePhysicalDamage(damage, attackerStats, defenderStats):
    # type: (AttributeSet, AttributeSet) -> int
    return ((attackerStats.attack + 20) / (defenderStats.defense + 20) * damage)


def CalculateMagicalDamage(damage, attackerStats, defenderStats):
    # type: (AttributeSet, AttributeSet) -> int
    return ((attackerStats.magicAttack + 20) / (defenderStats.magicDefense + 20) * damage)


def CalculateExperienceGain(targetLevel, playerLevel):
    # type: (int, int) -> int
    return 50


def CalculateNextLevelExperience(level):
    # type: (int) -> int
    return level * 250 + 250


def CalculateThreatGain(damage, entityStats):
    # type: (int, AttributeSet) -> int
    modifier = 100.0 + entityStats.t
    modifier /= 100.0
    return int(modifier * damage)