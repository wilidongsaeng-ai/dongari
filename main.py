"""게임 진입점."""

from game import Game


def main() -> None:
    game = Game(start_stage=1)
    game.run()


if __name__ == "__main__":
    main()
