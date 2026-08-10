"""방 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Tuple

from door import Door

TileCoord = Tuple[int, int]


@dataclass
class Room:
    """복도와만 연결된 독립 방."""

    id: int
    tiles: Set[TileCoord]
    door: Door
    center: TileCoord
    is_escape_room: bool = False
    visited: bool = False
    items: list = field(default_factory=list)
    has_quiz: bool = False

    def contains_tile(self, tx: int, ty: int) -> bool:
        return (tx, ty) in self.tiles

    def mark_visited(self) -> None:
        self.visited = True
