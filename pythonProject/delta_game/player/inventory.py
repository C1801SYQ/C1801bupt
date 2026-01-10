class Inventory:
    def __init__(self):
        self.gold = 0
        self.items = {}

    def add_gold(self, amount):
        self.gold += amount

    def add_item(self, item):
        name = item.name
        if name not in self.items:
            self.items[name] = [item, 0]
        self.items[name][1] += 1

    def use_item(self, name, player):
        if name not in self.items:
            return False

        item, count = self.items[name]
        if count <= 0:
            return False

        item.use(player)
        self.items[name][1] -= 1
        return True
