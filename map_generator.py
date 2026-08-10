"""복도 중심 맵 생성기.

방들은 서로 직접 연결되지 않고, 넓은 복도 네트워크를 따라 띄엄띄엄 배치된다.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from config import TILE_CORRIDOR, TILE_ROOM, TILE_WALL
from door import Door
from room import Room

TileCoord = Tuple[int, int]
Direction = Tuple[int, int]

DIRS: List[Direction] = [(1, 0), (-1, 0), (0, 1), (0, -1)]


@dataclass
class GameMap:
    width: int
    height: int
    tiles: List[List[int]]
    rooms: List[Room]
    doors: List[Door]
    spawn_tile: TileCoord
    door_lookup: Dict[TileCoord, Door]

    def tile_at(self, tx: int, ty: int) -> int:
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return TILE_WALL
        return self.tiles[ty][tx]

    def is_walkable(self, tx: int, ty: int) -> bool:
        tile = self.tile_at(tx, ty)
        if tile in (TILE_CORRIDOR, TILE_ROOM):
            return True
        door = self.door_lookup.get((tx, ty))
        if door is not None:
            return door.is_open
        return False

    def room_at(self, tx: int, ty: int) -> Optional[Room]:
        for room in self.rooms:
            if room.contains_tile(tx, ty):
                return room
        return None


def _carve_rect(
    grid: List[List[int]],
    x: int,
    y: int,
    w: int,
    h: int,
    tile: int,
) -> None:
    height = len(grid)
    width = len(grid[0])
    for ty in range(y, y + h):
        for tx in range(x, x + w):
            if 0 <= tx < width and 0 <= ty < height:
                grid[ty][tx] = tile


def _carve_corridor_network(
    grid: List[List[int]],
    width: int,
    height: int,
    branch_count: int,
    rng: random.Random,
) -> Set[TileCoord]:
    """중앙에서 가지치는 복도 네트워크를 만든다."""
    corridor_cells: Set[TileCoord] = set()
    start_x, start_y = width // 2, height // 2

    _carve_rect(grid, start_x - 1, start_y - 1, 3, 3, TILE_CORRIDOR)
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            corridor_cells.add((start_x + dx, start_y + dy))

    frontier = [(start_x, start_y)]
    created_branches = 0
    max_steps = branch_count * 3

    while frontier and created_branches < max_steps:
        cx, cy = rng.choice(frontier)
        direction = rng.choice(DIRS)
        length = rng.randint(8, 18)

        px, py = cx, cy
        path: List[TileCoord] = []
        for _ in range(length):
            px += direction[0]
            py += direction[1]
            if px < 3 or py < 3 or px >= width - 3 or py >= height - 3:
                break
            path.append((px, py))

        if len(path) < 4:
            continue

        corridor_w = 3
        if direction[0] != 0:
            for tx, ty in path:
                _carve_rect(grid, tx, ty - 1, corridor_w, corridor_w, TILE_CORRIDOR)
                for dx in range(corridor_w):
                    for dy in range(corridor_w):
                        corridor_cells.add((tx + dx, ty - 1 + dy))
        else:
            for tx, ty in path:
                _carve_rect(grid, tx - 1, ty, corridor_w, corridor_w, TILE_CORRIDOR)
                for dx in range(corridor_w):
                    for dy in range(corridor_w):
                        corridor_cells.add((tx - 1 + dx, ty + dy))

        created_branches += 1
        frontier.append(path[-1])

        if rng.random() < 0.45:
            side_dir = (direction[1], direction[0])
            if rng.random() < 0.5:
                side_dir = (-side_dir[0], -side_dir[1])
            sx, sy = path[len(path) // 2]
            side_path = []
            spx, spy = sx, sy
            for _ in range(rng.randint(4, 8)):
                spx += side_dir[0]
                spy += side_dir[1]
                if spx < 3 or spy < 3 or spx >= width - 3 or spy >= height - 3:
                    break
                side_path.append((spx, spy))
            if len(side_path) >= 3:
                if side_dir[0] != 0:
                    for tx, ty in side_path:
                        _carve_rect(grid, tx, ty - 1, corridor_w, corridor_w, TILE_CORRIDOR)
                        for dx in range(corridor_w):
                            for dy in range(corridor_w):
                                corridor_cells.add((tx + dx, ty - 1 + dy))
                else:
                    for tx, ty in side_path:
                        _carve_rect(grid, tx - 1, ty, corridor_w, corridor_w, TILE_CORRIDOR)
                        for dx in range(corridor_w):
                            for dy in range(corridor_w):
                                corridor_cells.add((tx - 1 + dx, ty + dy))

    return corridor_cells


def _find_room_slots(
    grid: List[List[int]],
    corridor_cells: Set[TileCoord],
) -> List[Tuple[int, int, Direction]]:
    """복도 옆 벽면에 방을 붙일 수 있는 후보 위치."""
    slots: List[Tuple[int, int, Direction]] = []
    width = len(grid[0])
    height = len(grid)

    for tx, ty in corridor_cells:
        for dx, dy in DIRS:
            nx, ny = tx + dx, ty + dy
            if nx < 1 or ny < 1 or nx >= width - 1 or ny >= height - 1:
                continue
            if grid[ny][nx] != TILE_WALL:
                continue
            # 복도 바깥쪽 벽이면 방 후보
            if (tx, ty) in corridor_cells and grid[ny][nx] == TILE_WALL:
                slots.append((nx, ny, (dx, dy)))

    return slots


def _can_place_room(
    grid: List[List[int]],
    origin_x: int,
    origin_y: int,
    room_w: int,
    room_h: int,
    door_x: int,
    door_y: int,
) -> bool:
    height = len(grid)
    width = len(grid[0])

    if origin_x < 1 or origin_y < 1:
        return False
    if origin_x + room_w >= width - 1 or origin_y + room_h >= height - 1:
        return False

    for ty in range(origin_y, origin_y + room_h):
        for tx in range(origin_x, origin_x + room_w):
            cell = grid[ty][tx]
            if (tx, ty) == (door_x, door_y):
                continue
            if cell != TILE_WALL:
                return False
    return True


def _place_rooms(
    grid: List[List[int]],
    corridor_cells: Set[TileCoord],
    room_count: int,
    rng: random.Random,
) -> Tuple[List[Room], List[Door]]:
    slots = _find_room_slots(grid, corridor_cells)
    rng.shuffle(slots)

    rooms: List[Room] = []
    doors: List[Door] = []
    used_areas: Set[TileCoord] = set()

    for slot_x, slot_y, outward in slots:
        if len(rooms) >= room_count:
            break

        room_w = rng.randint(5, 8)
        room_h = rng.randint(5, 8)

        if outward[0] == 1:
            origin_x, origin_y = slot_x, slot_y - room_h // 2
            door_x, door_y = slot_x - 1, slot_y
        elif outward[0] == -1:
            origin_x, origin_y = slot_x - room_w + 1, slot_y - room_h // 2
            door_x, door_y = slot_x, slot_y
        elif outward[1] == 1:
            origin_x, origin_y = slot_x - room_w // 2, slot_y
            door_x, door_y = slot_x, slot_y - 1
        else:
            origin_x, origin_y = slot_x - room_w // 2, slot_y - room_h + 1
            door_x, door_y = slot_x, slot_y

        if not _can_place_room(grid, origin_x, origin_y, room_w, room_h, door_x, door_y):
            continue

        room_tiles: Set[TileCoord] = set()
        valid = True
        for ty in range(origin_y, origin_y + room_h):
            for tx in range(origin_x, origin_x + room_w):
                if (tx, ty) == (door_x, door_y):
                    continue
                if grid[ty][tx] != TILE_WALL:
                    valid = False
                    break
                room_tiles.add((tx, ty))
            if not valid:
                break

        if not valid:
            continue

        if room_tiles & used_areas:
            continue

        for tx, ty in room_tiles:
            grid[ty][tx] = TILE_ROOM

        door = Door(tile_x=door_x, tile_y=door_y, room_id=len(rooms))
        doors.append(door)

        center_x = origin_x + room_w // 2
        center_y = origin_y + room_h // 2
        room = Room(
            id=len(rooms),
            tiles=room_tiles,
            door=door,
            center=(center_x, center_y),
        )
        rooms.append(room)
        used_areas.update(room_tiles)
        used_areas.add((door_x, door_y))

    return rooms, doors


def _pick_spawn(corridor_cells: Set[TileCoord], rng: random.Random) -> TileCoord:
    return rng.choice(sorted(corridor_cells))


def _validate_connectivity(game_map: GameMap) -> bool:
    """모든 방이 복도를 통해 도달 가능한지 검사."""
    if not game_map.rooms:
        return len(game_map.door_lookup) == 0

    start = game_map.spawn_tile
    visited: Set[TileCoord] = {start}
    stack = [start]

    while stack:
        cx, cy = stack.pop()
        for dx, dy in DIRS:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in visited:
                continue
            if game_map.is_walkable(nx, ny):
                visited.add((nx, ny))
                stack.append((nx, ny))
            elif (nx, ny) in game_map.door_lookup:
                door = game_map.door_lookup[(nx, ny)]
                if door.is_open:
                    visited.add((nx, ny))
                    stack.append((nx, ny))

    for room in game_map.rooms:
        door_coord = (room.door.tile_x, room.door.tile_y)
        # 문이 닫혀 있어도 도달 가능성은 문 옆 복도 타일 기준으로 확인
        reachable = False
        for dx, dy in DIRS:
            adj = (door_coord[0] + dx, door_coord[1] + dy)
            if adj in visited:
                reachable = True
                break
        if not reachable:
            return False
    return True


def generate_map(
    map_width: int,
    map_height: int,
    room_count: int,
    seed: Optional[int] = None,
    max_attempts: int = 40,
) -> GameMap:
    """복도 + 방 맵을 생성한다. 실패 시 재시도."""
    rng = random.Random(seed)

    for attempt in range(max_attempts):
        grid = [[TILE_WALL for _ in range(map_width)] for _ in range(map_height)]
        branch_count = max(6, room_count + 2)
        corridor_cells = _carve_corridor_network(grid, map_width, map_height, branch_count, rng)
        rooms, doors = _place_rooms(grid, corridor_cells, room_count, rng)

        min_rooms = max(3, int(room_count * 0.75))
        if len(rooms) < min_rooms:
            rng.seed((seed or 0) + attempt + 1)
            continue

        door_lookup = {(d.tile_x, d.tile_y): d for d in doors}
        spawn = _pick_spawn(corridor_cells, rng)

        game_map = GameMap(
            width=map_width,
            height=map_height,
            tiles=grid,
            rooms=rooms,
            doors=doors,
            spawn_tile=spawn,
            door_lookup=door_lookup,
        )

        if _validate_connectivity(game_map):
            return game_map

        rng.seed((seed or 0) + attempt + 1)

    raise RuntimeError("유효한 맵을 생성하지 못했습니다.")
