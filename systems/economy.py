"""The economy — keeps track of the player's gold.

Gold is earned by surviving a wave and spent on towers. Keeping all the
gold rules in one small class means the rest of the game just asks this
object "can I afford it?" instead of juggling the number itself.
"""

import settings


class Economy:
    """Holds the player's gold and the rules for spending it."""

    def __init__(self):
        self.gold = settings.STARTING_GOLD

    def earn(self, amount):
        """Add gold (for example, after surviving a wave)."""
        self.gold += amount

    def can_afford(self, cost):
        """True if there is enough gold to pay `cost`."""
        return self.gold >= cost

    def spend(self, cost):
        """Pay `cost` if possible. Returns True if the purchase happened."""
        if self.can_afford(cost):
            self.gold -= cost
            return True
        return False
