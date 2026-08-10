"""게임 상태 및 메인 루프."""

from __future__ import annotations

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from map_generator import GameMap, generate_map
from player import Player
from stage import StageConfig, get_stage_config, load_stages
from ui import UIRenderer


class Game:
    def __init__(self, start_stage: int = 1) -> None:
        pygame.init()
        pygame.display.set_caption("방 탈출 추격 게임")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.ui = UIRenderer()
        self.stages = load_stages()
        self.stage_number = start_stage
        self.running = True
        self.load_stage(self.stage_number)

    def load_stage(self, stage_number: int) -> None:
        self.stage_cfg = get_stage_config(stage_number, self.stages)
        seed = stage_number * 10007
        self.game_map: GameMap = generate_map(
            map_width=self.stage_cfg.map_width,
            map_height=self.stage_cfg.map_height,
            room_count=self.stage_cfg.room_count,
            seed=seed,
        )
        sx, sy = self.game_map.spawn_tile
        self.player = Player(
            x=sx * TILE_SIZE + TILE_SIZE / 2,
            y=sy * TILE_SIZE + TILE_SIZE / 2,
        )

    def run(self) -> None:
        while self.running:
            dt_ms = self.clock.tick(60)
            dt = dt_ms / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_e:
                    self._toggle_nearby_door()

    def _toggle_nearby_door(self) -> None:
        door = self.player.find_nearby_door(self.game_map)
        if door is not None:
            door.toggle()

    def _get_move_input(self) -> tuple[float, float]:
        keys = pygame.key.get_pressed()
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        return dx, dy

    def _update(self, dt: float) -> None:
        move_dir = self._get_move_input()
        self.player.update(dt, move_dir, self.game_map)

    def _camera(self) -> tuple[float, float]:
        cam_x = self.player.x - SCREEN_WIDTH / 2
        cam_y = self.player.y - SCREEN_HEIGHT / 2
        max_x = self.game_map.width * TILE_SIZE - SCREEN_WIDTH
        max_y = self.game_map.height * TILE_SIZE - SCREEN_HEIGHT
        cam_x = max(0, min(cam_x, max(0, max_x)))
        cam_y = max(0, min(cam_y, max(0, max_y)))
        return cam_x, cam_y

    def _draw(self) -> None:
        cam_x, cam_y = self._camera()
        self.ui.draw_world(self.screen, self.game_map, self.player, cam_x, cam_y)

        door = self.player.find_nearby_door(self.game_map)
        hint = ""
        if door is not None:
            state = "열림" if door.is_open else "닫힘"
            action = "닫기" if door.is_open else "열기"
            hint = f"[E] 문 {action} (현재: {state})"

        self.ui.draw_hud(self.screen, self.stage_cfg, hint)
