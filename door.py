"""문 상태 및 상호작용."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Door:
    """방과 복도를 잇는 문. 방마다 복도 쪽으로 하나만 존재."""

    tile_x: int
    tile_y: int
    room_id: int
    is_open: bool = False

    def toggle(self) -> None:
        self.is_open = not self.is_open

    def blocks_movement(self) -> bool:
        return not self.is_open
