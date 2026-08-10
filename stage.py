"""스테이지 설정 로더."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class StageConfig:
    stage: int
    enemy_speed: float
    room_count: int
    required_items: int
    quiz_count: int
    map_width: int
    map_height: int
    theme: str = "school"


def load_stages(data_dir: Path | None = None) -> List[StageConfig]:
    data_dir = data_dir or Path(__file__).parent / "data"
    path = data_dir / "stages.json"
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)

    return [StageConfig(**entry) for entry in raw["stages"]]


def get_stage_config(stage_number: int, stages: List[StageConfig] | None = None) -> StageConfig:
    stages = stages or load_stages()
    for cfg in stages:
        if cfg.stage == stage_number:
            return cfg
    raise ValueError(f"스테이지 {stage_number} 설정을 찾을 수 없습니다.")
