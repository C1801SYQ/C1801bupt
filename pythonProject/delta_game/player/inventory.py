# player/inventory.py

class Inventory:
    def __init__(self):
        self.items = []
        self.gold = 0
        self.total_weight = 0
        self.is_open = False  # ⭐ 新增：记录背包是否打开

    def toggle(self):
        """切换背包打开/关闭状态"""
        self.is_open = not self.is_open

    def add_item(self, item_obj):
        self.items.append(item_obj)
        if hasattr(item_obj, 'amount'):
            self.gold += item_obj.amount
        if hasattr(item_obj, 'weight'):
            self.total_weight += item_obj.weight

    def get_speed_multiplier(self):
        """⭐ 修复报错：计算负重减速"""
        threshold = 10.0
        if self.total_weight > threshold:
            penalty = (self.total_weight - threshold) * 0.05
            return max(0.4, 1.0 - penalty)
        return 1.0

    def get_item_counts(self):
        """⭐ 新增：统计背包物品，用于 UI 显示清单"""
        counts = {}
        for item in self.items:
            name = getattr(item, 'name', '未知物品')
            color = getattr(item, 'color', (255, 255, 255))
            if name not in counts:
                counts[name] = {"count": 0, "color": color}
            counts[name]["count"] += 1
        return counts

    def use_item(self, item_name, player):
        for i, item in enumerate(self.items):
            if getattr(item, 'name', '') == item_name:
                if hasattr(item, 'weight'):
                    self.total_weight -= item.weight
                item.use(player)
                self.items.pop(i)
                return True
        return False