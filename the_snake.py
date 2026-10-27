"""Игра "Змейка"."""

from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
KEY_DIRECTIONS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20
# Начальная позиция
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс объектов игры."""

    def __init__(
            self,
            body_color=None,
            position=START_POSITION,
    ):
        """Задать цвет и начальную позицию объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Задать способ отрисовки для дочерних классов."""
        raise NotImplementedError

    def _draw_cell(self, position, color=None):
        """Нарисовать клетку объекта в позиции position."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Объект яблока."""

    def __init__(
            self,
            body_color=APPLE_COLOR,
            position=START_POSITION,
            occupied_positions=None,
    ):
        """Задать цвет и случайную начальную позицию яблока."""
        super().__init__(body_color=body_color, position=position)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Выбрать позицию вне занятых клеток."""
        free_cells = BOARD_CELLS.difference(occupied_positions or ())
        self.position = choice(tuple(free_cells)) if free_cells else None

    def draw(self):
        """Нарисовать яблоко на игровом поле."""
        if self.position is not None:
            self._draw_cell(self.position)


class Snake(GameObject):
    """Объект змейки."""

    def __init__(
            self,
            body_color=SNAKE_COLOR,
            position=START_POSITION,
    ):
        """Создать змейку длиной в одну клетку, движущуюся вправо."""
        super().__init__(body_color=body_color, position=position)
        self.reset(direction=RIGHT)

    def update_direction(self):
        """Изменить направление движения змейки."""
        self.direction = self.next_direction or self.direction
        self.next_direction = None

    def move(self):
        """Передвинуть змейку на следующую клетку."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(0, (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        self.last = None

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def grow(self):
        """Увеличить длину змейки на сегмент."""
        self.length += 1
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def draw(self):
        """Стереть сегмент хвоста и нарисовать голову змейки."""
        head = self.get_head_position()
        # При замыкании пути голова может занять прежнюю клетку хвоста
        if self.last is not None and self.last != head:
            self._draw_cell(self.last, BOARD_BACKGROUND_COLOR)

        self._draw_cell(head)

    def check_collision(self):
        """Вернуть признак столкновения головы с телом змейки."""
        return self.get_head_position() in self.positions[1:]

    def get_head_position(self):
        """Вернуть координаты головы."""
        return self.positions[0]

    def reset(self, direction=None):
        """Сбросить змейку до одного сегмента в начальной позиции."""
        self.length = 1
        self.positions = [self.position]
        self.direction = direction or choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать пользовательский ввод."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            raise SystemExit

        direction = KEY_DIRECTIONS.get(event.key)
        if direction is None:
            continue

        opposite = tuple(-value for value in game_object.direction)
        # Нельзя двигаться в обратную сторону
        if direction != opposite:
            game_object.next_direction = direction


def main():
    """Запустить игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    apple_moved = True

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.check_collision() or apple.position is None:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple_moved = True

        elif snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)
            apple_moved = True

        snake.draw()

        if apple_moved:
            apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
