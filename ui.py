"""HUD 및 화면 렌더링."""

from __future__ import annotations

import pygame

from config import (
    COLOR_BG,
    COLOR_CORRIDOR,
    COLOR_DOOR_CLOSED,
    COLOR_DOOR_OPEN,
    COLOR_PLAYER,
    COLOR_ROOM,
    COLOR_UI_DIM,
    COLOR_UI_TEXT,
    COLOR_WALL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_CORRIDOR,
    TILE_ROOM,
    TILE_SIZE,
    TILE_WALL,
)
from map_generator import GameMap
from player import Player
from stage import StageConfig


class UIRenderer:
    def __init__(self) -> None:
        pygame.font.init()
        self.font = pygame.font.SysFont("applesdgothicneo", 20)
        self.font_large = pygame.font.SysFont("applesdgothicneo", 28, bold=True)

    def draw_world(
        self,
        surface: pygame.Surface,
        game_map: GameMap,
        player: Player,
        camera_x: float,
        camera_y: float,
    ) -> None:
        surface.fill(COLOR_BG)

        start_tx = max(0, int(camera_x // TILE_SIZE) - 1)
        start_ty = max(0, int(camera_y // TILE_SIZE) - 1)
        end_tx = min(game_map.width, start_tx + SCREEN_WIDTH // TILE_SIZE + 3)
        end_ty = min(game_map.height, start_ty + SCREEN_HEIGHT // TILE_SIZE + 3)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = game_map.tile_at(tx, ty)
                rect = pygame.Rect(
                    tx * TILE_SIZE - camera_x,
                    ty * TILE_SIZE - camera_y,
                    TILE_SIZE,
                    TILE_SIZE,
                )

                if tile == TILE_WALL:
                    color = COLOR_WALL
                elif tile == TILE_CORRIDOR:
                    color = COLOR_CORRIDOR
                elif tile == TILE_ROOM:
                    color = COLOR_ROOM
                else:
                    color = COLOR_WALL

                pygame.draw.rect(surface, color, rect)

        for door in game_map.doors:
            rect = pygame.Rect(
                door.tile_x * TILE_SIZE - camera_x,
                door.tile_y * TILE_SIZE - camera_y,
                TILE_SIZE,
                TILE_SIZE,
            )
            door_color = COLOR_DOOR_OPEN if door.is_open else COLOR_DOOR_CLOSED
            pygame.draw.rect(surface, door_color, rect)
            pygame.draw.rect(surface, COLOR_UI_TEXT, rect, 2)

        px = int(player.x - camera_x)
        py = int(player.y - camera_y)
        pygame.draw.circle(surface, COLOR_PLAYER, (px, py), 10)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 10, 2)

    def draw_hud(
        self,
        surface: pygame.Surface,
        stage_cfg: StageConfig,
        nearby_door_hint: str,
    ) -> None:
        panel = pygame.Rect(12, 12, 360, 130)
        pygame.draw.rect(surface, (30, 30, 40), panel, border_radius=8)
        pygame.draw.rect(surface, COLOR_UI_DIM, panel, 1, border_radius=8)

        lines = [
            self.font_large.render(f"STAGE {stage_cfg.stage}", True, COLOR_UI_TEXT),
            self.font.render(f"방: {stage_cfg.room_count}개", True, COLOR_UI_DIM),
            self.font.render("WASD: 이동  |  E: 문 열기/닫기", True, COLOR_UI_DIM),
        ]
        if nearby_door_hint:
            lines.append(self.font.render(nearby_door_hint, True, (255, 220, 120)))

        y = 20
        for line in lines:
            surface.blit(line, (24, y))
            y += line.get_height() + 6

        help_text = self.font.render("복도를 따라 방으로 이동하세요 (방끼리 직접 연결 없음)", True, COLOR_UI_DIM)
        surface.blit(help_text, (12, SCREEN_HEIGHT - 36))
