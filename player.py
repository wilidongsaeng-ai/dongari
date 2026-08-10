"""플레이어 이동 및 상호작용."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from config import INTERACT_RANGE, PLAYER_RADIUS, PLAYER_SPEED, TILE_SIZE
from door import Door
from map_generator import GameMap

Vec2 = Tuple[float, float]


@dataclass
class Player:
    x: float
    y: float
    speed: float = PLAYER_SPEED

    @property
    def pos(self) -> Vec2:
        return self.x, self.y

    def tile_coord(self) -> Tuple[int, int]:
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def update(self, dt: float, move_dir: Vec2, game_map: GameMap) -> None:
        dx, dy = move_dir
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        self._move_axis(dx * self.speed * dt, 0, game_map)
        self._move_axis(0, dy * self.speed * dt, game_map)

        tx, ty = self.tile_coord()
        room = game_map.room_at(tx, ty)
        if room is not None:
            room.mark_visited()

    def _move_axis(self, dx: float, dy: float, game_map: GameMap) -> None:
        if dx == 0 and dy == 0:
            return

        new_x = self.x + dx
        new_y = self.y + dy

        if not self._collides(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y

    def _collides(self, x: float, y: float, game_map: GameMap) -> bool:
        points = [
            (x - PLAYER_RADIUS, y - PLAYER_RADIUS),
            (x + PLAYER_RADIUS, y - PLAYER_RADIUS),
            (x - PLAYER_RADIUS, y + PLAYER_RADIUS),
            (x + PLAYER_RADIUS, y + PLAYER_RADIUS),
        ]
        for px, py in points:
            tx = int(px // TILE_SIZE)
            ty = int(py // TILE_SIZE)
            if not game_map.is_walkable(tx, ty):
                door = game_map.door_lookup.get((tx, ty))
                if door is None or door.blocks_movement():
                    return True
        return False

    def find_nearby_door(self, game_map: GameMap) -> Optional[Door]:
        best_door: Optional[Door] = None
        best_dist = INTERACT_RANGE

        for door in game_map.doors:
            door_x = door.tile_x * TILE_SIZE + TILE_SIZE / 2
            door_y = door.tile_y * TILE_SIZE + TILE_SIZE / 2
            dist = math.hypot(self.x - door_x, self.y - door_y)
            if dist <= best_dist:
                best_dist = dist
                best_door = door

        return best_door
