# 방 탈출 추격 게임

복도를 따라 흩어진 방을 탐색하고, 아이템을 모아 탈출구를 찾아 탈출하는 추격형 방 탈출 게임입니다.

## 현재 구현 상태 (1단계)

- [x] 플레이어 이동 (WASD, dt 기반)
- [x] 복도 + 방 맵 (방끼리 직접 연결 없음)
- [x] 문 열기/닫기 (E)
- [x] 1~50 스테이지 데이터 (`data/stages.json`)
- [ ] 아이템 획득 (2단계)
- [ ] 탈출구 (3단계)
- [ ] 추격 개체 (4단계)
- [ ] 퀴즈/보조 아이템 (5~6단계)

## 실행 방법

```bash
cd ~/Projects/room-escape-chase
pip install -r requirements.txt
python main.py
```

## 조작

| 키 | 동작 |
|---|---|
| WASD | 이동 |
| E | 문 열기/닫기 |
| ESC | 종료 |

## 맵 구조

방들은 서로 직접 연결되지 않습니다. 집 구조도처럼 **넓은 복도 네트워크**를 따라 방이 띄엄띄엄 배치되며, 각 방은 복도와 연결된 **문 1개**만 가집니다.

## 프로젝트 구조

```
project/
├── main.py           # 진입점
├── game.py           # 게임 루프
├── player.py         # 플레이어
├── room.py / door.py # 방·문
├── map_generator.py  # 복도형 맵 생성
├── stage.py          # 스테이지 설정
├── ui.py             # HUD
└── data/             # JSON 데이터
```
