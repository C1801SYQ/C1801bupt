import pygame
import random
from settings import TILE_SIZE


class TileMap:
    def __init__(self, rows=60, cols=60, padding=10):
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self.tile_size = TILE_SIZE

        # 1. 初始化全为墙 "1"
        self.raw_data = [["1" for _ in range(cols)] for _ in range(rows)]
        self.rooms = []
        self.corridors = []  # ⭐ 新增：用于存储连廊矩形，供小地图显示
        # 2. 生成结构化地图
        self._generate_structured_map()

        # 3. 转换为字符串数组并应用填充
        raw_strings = ["".join(row) for row in self.raw_data]
        self.map_data = self._pad_map(raw_strings, self.padding)

        self.exit_rect = None
        self.walls = []
        self.player_spawn = (0, 0)
        self.wall_colors = {}

        self._load_map()

    def _pad_map(self, data, p):
        """在地图四周填充 p 层墙壁"""
        width = len(data[0])
        horiz_wall = "1" * (width + 2 * p)
        padded = [horiz_wall] * p
        side_wall = "1" * p
        for row in data:
            padded.append(side_wall + row + side_wall)
        padded.extend([horiz_wall] * p)
        return padded

    def _generate_structured_map(self):
        # 1. 房间做大：将尺寸从 (5,8) 提升到 (10, 15)
        for _ in range(random.randint(5, 7)):
            w = random.randint(10, 15)  # 更宽的大厅
            h = random.randint(10, 15)  # 更高的房间
            # 缩短连廊的关键：限制房间生成的分布范围，不要太分散
            x = random.randint(2, self.cols - w - 2)
            y = random.randint(2, self.rows - h - 2)

            for i in range(y, y + h):
                for j in range(x, x + w):
                    self.raw_data[i][j] = "0"
            self.rooms.append((x, y, w, h))

        # 2. 连接房间并记录连廊位置
        for i in range(len(self.rooms) - 1):
            x1, y1, w1, h1 = self.rooms[i]
            x2, y2, w2, h2 = self.rooms[i + 1]
            cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
            cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2

            # 横向连廊：记录矩形 (x, y, w, h)
            hx, hy = min(cx1, cx2), cy1
            hw, hh = max(cx1, cx2) - min(cx1, cx2) + 1, 1
            self.corridors.append((hx, hy, hw, hh))
            for x in range(hx, hx + hw): self.raw_data[hy][x] = "0"

            # 纵向连廊
            vx, vy = cx2, min(cy1, cy2)
            vw, vh = 1, max(cy1, cy2) - min(cy1, cy2) + 1
            self.corridors.append((vx, vy, vw, vh))
            for y in range(vy, vy + vh): self.raw_data[y][vx] = "0"

        # ⭐ 强制校准撤离点：设在最后一个房间中心
        if self.rooms:
            ex, ey, ew, eh = self.rooms[-1]
            # 挖出 2x2 的撤离区
            self.raw_data[ey + eh // 2][ex + ew // 2] = "E"
            self.raw_data[ey + eh // 2 + 1][ex + ew // 2] = "E"
            self.raw_data[ey + eh // 2][ex + ew // 2 + 1] = "E"
            self.raw_data[ey + eh // 2 + 1][ex + ew // 2 + 1] = "E"

    def _load_map(self):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                if tile == "1":
                    rect = pygame.Rect(world_x, world_y, self.tile_size, self.tile_size)
                    self.walls.append(rect)
                    c = random.randint(50, 70)
                    self.wall_colors[id(rect)] = (c, c, c)
                elif tile == "P":
                    self.player_spawn = (world_x, world_y)
                elif tile == "E" and self.exit_rect is None:
                    # 初始化撤离点矩形
                    self.exit_rect = pygame.Rect(world_x, world_y, self.tile_size * 2, self.tile_size * 2)

    def get_random_empty_pos(self):
        """寻找空地供金币随机生成"""
        while True:
            r, c = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.raw_data[r][c] == "0":
                return (c + self.padding) * self.tile_size, (r + self.padding) * self.tile_size

    def draw(self, screen, camera):
        # 绘制背景和墙体
        bg_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(screen, (25, 25, 30), camera.apply_rect(bg_rect))
        for wall in self.walls:
            rect = camera.apply_rect(wall)
            if rect.bottom > 0 and rect.top < 600:
                pygame.draw.rect(screen, self.wall_colors.get(id(wall), (60, 60, 60)), rect)

    @property
    def width(self):
        return len(self.map_data[0]) * self.tile_size

    @property
    def height(self):
        return len(self.map_data) * self.tile_size