# Все классы компонентов кладутся сюда
import abc
import random
from collections import deque
from .event_loop import EventLoop
# Компонент Считыватель:
# Действие «Принять символ»
# Событие «Есть символ»
# Событие «Строка закончилась»
# Атрибут «Принятый символ»

# Компонент Сигнал:
# Действие «Импульс А»
# Действие «Импульс Б»
# Действие «Импульс В»

# Компонент Счётчик:
# Действие «Установить»
# Действие «Увеличить»
# Действие «Уменьшить»
# Действие «Очистить»
# Атрибут «Значение»




class Component(abc.ABC):
    def __init__(self, name: str):
        self.name = name

    def get_sm_options(self, options: dict):
        ...
        # raise NotImplementedError("This method should be overridden in subclasses")

class Reader(Component):
    # signals: char_accepted
    # signals: line_finished
    def __init__(self, name: str):
        super().__init__(name)
        self.message = ''
        self.current_char = ''
        self.index = 0

    def get_sm_options(self, options: dict):
        self.message = options['message']
        # self.current_char = self.message[0]

    def read(self):
        if self.index < len(self.message):
            self.current_char = self.message[self.index]
            self.index += 1
            EventLoop.add_event(f'{self.name}.char_accepted')
            return True
        else:
            EventLoop.add_event(f'{self.name}.line_finished')
            return False


class Impulse(Component):
    def impulseA(self):
        # print('impulseA')
        EventLoop.add_event('impulseA', True)

    def impulseB(self):
        # print('impulseB')
        EventLoop.add_event('impulseB', True)

    def impulseC(self):
        # print('impulseC')
        EventLoop.add_event('impulseC', True)

class Counter(Component):
    def __init__(self, name: str):
        super().__init__(name)
        self.value = 0

    def set(self, value: int):
        self.value = value

    def add(self):
        self.value += 1

    def sub(self):
        self.value -= 1

    def clear(self):
        self.value = 0

# Компонент Свое событие
# Событие Вызвано
# Действие Вызвать

# Компонент Компас
# Атрибут Ориентация (С, Ю, З, В)
# Атрибут Координата X
# Атрибут Координата Y

# Компонент Цветы
# Действие Высадить, параметр Тип [роза, мята, василек]

# Компонент Движение
# Действие Вперёд
# Действие Назад
# Действие Повернуть влево
# Действие Повернуть вправо

# Компонент Сенсор
# Действие Осмотреть стены
# Действия Осмотреть растение
# Событие Растение осмотрено
# Событие Стена спереди
# Событие Стена сзади
# Событие Стена слева
# Событие Стена справа
# Атрибут Стена спереди = 1/0
# Атрибут Стена сзади = 1/0
# Атрибут Стена слева = 1/0
# Атрибут Стена справа = 1/0
# Атрибут Высаженные цветы = 0/1/2/3 (нет/роза/мята/василек)

class GardenerCrashException(Exception):
    ...

class Gardener:

    def __init__(self, N: int, M: int, with_walls: bool = False):
        self.N = N
        self.M = M
        self.field = [[0 for _ in range(N)] for _ in range(M)]
        if with_walls:
            self.generate_walls()
        self.SOUTH = 0
        self.NORTH = 1
        self.WEST = 2
        self.EAST = 3

        self.ROSE = 1
        self.MINT = 2
        self.VASILEK = 3
        self.EMPTY = 0

        self.orientation = self.SOUTH
        self.x = 0
        self.y = 0

        # Атрибуты наличия стен
        self.wall_left_value = 0
        self.wall_right_value = 0
        self.wall_straight_value = 0
        self.wall_back_value = 0

    def generate_walls(self, wall_fraction: float = 0.2, max_attempts: int = 1000):
        N, M = self.N, self.M
        total_cells = N * M
        num_walls = int(total_cells * wall_fraction)
        attempts = 0
        walls_placed = 0
        # Список всех координат кроме стартовой (0,0)
        coords = [(i, j) for i in range(M) for j in range(N) if not (i == 0 and j == 0)]
        random.shuffle(coords)
        def is_connected(field):
            # BFS из (0,0), считаем количество достижимых клеток
            visited = [[False for _ in range(N)] for _ in range(M)]
            q = deque()
            q.append((0, 0))
            visited[0][0] = True
            reachable = 1
            while q:
                x, y = q.popleft()
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= ny < M and 0 <= nx < N and not visited[ny][nx] and field[ny][nx] != -1:
                        visited[ny][nx] = True
                        q.append((nx, ny))
                        reachable += 1
            # Количество пустых клеток
            empty_cells = sum(field[i][j] != -1 for i in range(M) for j in range(N))
            return reachable == empty_cells
        for x, y in coords:
            if walls_placed >= num_walls or attempts >= max_attempts:
                break
            if self.field[y][x] == 0:
                self.field[y][x] = -1
                if is_connected(self.field):
                    walls_placed += 1
                else:
                    self.field[y][x] = 0
            attempts += 1
        # print(f"Walls placed: {walls_placed}")


    def update_walls(self):
        # Обновляет значения wall_left_value, wall_right_value, wall_straight_value, wall_back_value
        dir_left = {
            self.NORTH: self.WEST,
            self.WEST: self.SOUTH,
            self.SOUTH: self.EAST,
            self.EAST: self.NORTH
        }[self.orientation]
        dir_right = {
            self.NORTH: self.EAST,
            self.EAST: self.SOUTH,
            self.SOUTH: self.WEST,
            self.WEST: self.NORTH
        }[self.orientation]
        dir_back = {
            self.NORTH: self.SOUTH,
            self.SOUTH: self.NORTH,
            self.EAST: self.WEST,
            self.WEST: self.EAST
        }[self.orientation]
        self.wall_left_value = 1 if self._wall_in_direction(dir_left) else 0
        self.wall_right_value = 1 if self._wall_in_direction(dir_right) else 0
        self.wall_straight_value = 1 if self._wall_in_direction(self.orientation) else 0
        self.wall_back_value = 1 if self._wall_in_direction(dir_back) else 0

    def wall_left(self):
        return self.wall_left_value == 1

    def wall_right(self):
        return self.wall_right_value == 1

    def wall_straight(self):
        return self.wall_straight_value == 1

    def wall_back(self):
        return self.wall_back_value == 1

    def get_current_flower(self):
        return self.field[self.y][self.x]

    def _wall_in_direction(self, direction):
        dx, dy = 0, 0
        if direction == self.NORTH:
            dx, dy = 0, -1
        elif direction == self.SOUTH:
            dx, dy = 0, 1
        elif direction == self.WEST:
            dx, dy = -1, 0
        elif direction == self.EAST:
            dx, dy = 1, 0
        nx, ny = self.x + dx, self.y + dy
        if 0 <= ny < self.M and 0 <= nx < self.N:
            return self.field[ny][nx] == -1
        else:
            return True

class Sensor(Component):
    def __init__(self, name: str):
        super().__init__(name)
        self.gardener: Gardener | None = None
        self.flower = -1
        self.wall_right = -1
        self.wall_left = -1
        self.wall_straight = -1
        self.wall_back = -1

    @property
    def rose(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        return self.gardener.ROSE

    @property
    def mint(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        return self.gardener.MINT

    @property
    def vasilek(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        return self.gardener.VASILEK

    @property
    def empty(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        return self.gardener.EMPTY
    
    @property
    def wall_back(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.wall_back_value

    @property
    def wall_straight(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.wall_straight_value

    @property
    def wall_right(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.wall_right

    @property
    def north(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.NORTH

    
    def get_sm_options(self, options: dict):
        gardener = options.get('gardener')

        if gardener is None:
            raise ValueError('Gardener is None!')

        self.gardener = gardener
        self.flower = gardener.get_current_flower()
    
    def search_walls(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        self.gardener.update_walls()
        if self.gardener.wall_right():
            EventLoop.add_event(f'{self.name}.wall_right')
        elif self.gardener.wall_back():
            EventLoop.add_event(f'{self.name}.wall_back')
        elif self.gardener.wall_left():
            EventLoop.add_event(f'{self.name}.wall_left')
        elif self.gardener.wall_straight():
            EventLoop.add_event(f'{self.name}.wall_straight')
        self.wall_back = self.gardener.wall_back_value
        self.wall_left = self.gardener.wall_left_value
        self.wall_right = self.gardener.wall_right_value
        self.wall_straight = self.gardener.wall_straight_value

    def search_flowers(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        self.flower = self.gardener.get_current_flower()
        EventLoop.add_event(f'{self.name}.isDataRecieved')

    

class UserSignal(Component):
    def call(self):
        EventLoop.add_event(f'{self.name}.call', True)


class Flower(Component):
    def __init__(self, name: str):
        super().__init__(name)
        self.gardener: Gardener | None = None

    def get_sm_options(self, options: dict):
        gardener = options.get('gardener')

        if gardener is None:
            raise ValueError('Gardener is None!')

        self.gardener = gardener
    
    def plant(self, flower: int):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        self.gardener.field[self.gardener.y][self.gardener.x] = flower

# Компонент Движение
# Действие Вперёд
# Действие Назад
# Действие Повернуть влево
# Действие Повернуть вправо

class Mover(Component):
    def __init__(self, name: str):
        super().__init__(name)
        self.gardener: Gardener | None = None
    
    def get_sm_options(self, options: dict):
        gardener = options.get('gardener') 

        if gardener is None:
            raise ValueError('Gardener is None!')

        self.gardener = gardener
    
    def move_forward(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        dx, dy = 0, 0
        if self.gardener.orientation == self.gardener.NORTH:
            dx, dy = 0, -1
        elif self.gardener.orientation == self.gardener.SOUTH:
            dx, dy = 0, 1
        elif self.gardener.orientation == self.gardener.WEST:
            dx, dy = -1, 0
        elif self.gardener.orientation == self.gardener.EAST:
            dx, dy = 1, 0
        nx, ny = self.gardener.x + dx, self.gardener.y + dy
        if 0 <= nx < self.gardener.N and 0 <= ny < self.gardener.M:
            if self.gardener.field[ny][nx] != -1:
                self.gardener.x = nx
                self.gardener.y = ny
            else:
                raise GardenerCrashException('Crash: hit a wall!')
        else:
            raise GardenerCrashException('Crash: out of bounds!')
    def move_backward(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        dx, dy = 0, 0
        if self.gardener.orientation == self.gardener.NORTH:
            dx, dy = 0, 1
        elif self.gardener.orientation == self.gardener.SOUTH:
            dx, dy = 0, -1
        elif self.gardener.orientation == self.gardener.WEST:
            dx, dy = 1, 0
        elif self.gardener.orientation == self.gardener.EAST:
            dx, dy = -1, 0
        nx, ny = self.gardener.x + dx, self.gardener.y + dy
        if 0 <= nx < self.gardener.N and 0 <= ny < self.gardener.M:
            if self.gardener.field[ny][nx] != -1:
                self.gardener.x = nx
                self.gardener.y = ny
            else:
                raise GardenerCrashException('Crash: hit a wall!')
        else:
            raise GardenerCrashException('Crash: out of bounds!')

    def turn_left(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        # Поворот против часовой стрелки
        self.gardener.orientation = {
            self.gardener.NORTH: self.gardener.WEST,
            self.gardener.WEST: self.gardener.SOUTH,
            self.gardener.SOUTH: self.gardener.EAST,
            self.gardener.EAST: self.gardener.NORTH
        }[self.gardener.orientation]

    def turn_right(self):
        if self.gardener is None:
            raise ValueError('Gardener is None!')
        # Поворот по часовой стрелке
        self.gardener.orientation = {
            self.gardener.NORTH: self.gardener.EAST,
            self.gardener.EAST: self.gardener.SOUTH,
            self.gardener.SOUTH: self.gardener.WEST,
            self.gardener.WEST: self.gardener.NORTH
        }[self.gardener.orientation]

class Compass(Component):
    def __init__(self, name: str):
        super().__init__(name)
        self.gardener: Gardener | None = None

    def get_sm_options(self, options: dict):
        gardener = options.get('gardener')

        if gardener is None:
            raise ValueError('Gardener is required for Compass work!')

        self.gardener = gardener

    @property
    def x(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.x

    @property
    def y(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.y

    @property
    def south(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.SOUTH

    @property
    def north(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.NORTH

    @property
    def west(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.WEST

    @property
    def east(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.EAST

    @property
    def orientation(self):
        if self.gardener is None:
            raise ValueError('Gardener is required for Compass work!')
        return self.gardener.orientation
    
class LED:
    def on(self):
        print('on')

    def off(self):
        print('off')

    def get_sm_options(self, options: dict):
        ...

class Timer:
    def start(self, time: int):
        print('timer started for', time)
