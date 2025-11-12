# samurai_Archer.py
from pico2d import load_image, load_font, draw_rectangle, SDL_KEYDOWN, SDLK_a, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, \
    SDLK_UP, SDLK_DOWN, SDLK_LSHIFT
from arrow import Arrow
import game_world
import game_framework
from state_machine import StateMachine
import time  # time 모듈 추가
from event_to_string import event_to_string  # event_to_string 함수 임포트

# 상수 정의
PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)
WALK_SPEED_PPS = RUN_SPEED_PPS * 0.5

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


# 이벤트 정의
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def lshift_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LSHIFT


def lshift_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LSHIFT


def event_stop(e):
    return e[0] == 'STOP'


def event_run(e):
    return e[0] == 'RUN'


# 상태 클래스
class Idle:
    def __init__(self, samurai):
        self.samurai = samurai

    def enter(self, e):
        if event_stop(e):
            self.samurai.face_dir = e[1]
        self.samurai.frame = 0

    def exit(self, e):
        if a_down(e):
            self.samurai.state_machine.handle_state_event(('ATTACK', None))

    def do(self):
        self.samurai.frame = (self.samurai.frame + 8 * ACTION_PER_TIME * game_framework.frame_time) % 8

    def draw(self):
        if self.samurai.face_dir == 1:
            self.samurai.walk_image.clip_draw(int(self.samurai.frame) * 128, 0, 128, 128, self.samurai.x, self.samurai.y)
        else:
            self.samurai.walk_image.clip_composite_draw(int(self.samurai.frame) * 128, 0, 128, 128, 0, 'h',
                                                        self.samurai.x, self.samurai.y, 128, 128)


class Run:
    def __init__(self, samurai):
        self.samurai = samurai

    def enter(self, e):
        if self.samurai.xdir != 0:
            self.samurai.face_dir = self.samurai.xdir
        self.samurai.frame = 0

    def exit(self, e):
        if a_down(e):
            self.samurai.state_machine.handle_state_event(('ATTACK', None))

    def do(self):
        self.samurai.frame = (self.samurai.frame + 8 * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.samurai.x += self.samurai.xdir * self.samurai.speed * game_framework.frame_time
        self.samurai.y += self.samurai.ydir * self.samurai.speed * game_framework.frame_time

    def draw(self):
        if self.samurai.face_dir == 1:
            self.samurai.run_image.clip_draw(int(self.samurai.frame) * 128, 0, 128, 128, self.samurai.x, self.samurai.y)
        else:
            self.samurai.run_image.clip_composite_draw(int(self.samurai.frame) * 128, 0, 128, 128, 0, 'h',
                                                       self.samurai.x, self.samurai.y, 128, 128)


class Walk:
    def __init__(self, samurai):
        self.samurai = samurai

    def enter(self, e):
        if self.samurai.xdir != 0:
            self.samurai.face_dir = self.samurai.xdir
        self.samurai.frame = 0

    def exit(self, e):
        if a_down(e):
            self.samurai.state_machine.handle_state_event(('ATTACK', None))

    def do(self):
        self.samurai.frame = (self.samurai.frame + 8 * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.samurai.x += self.samurai.xdir * self.samurai.speed * game_framework.frame_time
        self.samurai.y += self.samurai.ydir * self.samurai.speed * game_framework.frame_time

    def draw(self):
        if self.samurai.face_dir == 1:
            self.samurai.walk_image.clip_draw(int(self.samurai.frame) * 128, 0, 128, 128, self.samurai.x, self.samurai.y)
        else:
            self.samurai.walk_image.clip_composite_draw(int(self.samurai.frame) * 128, 0, 128, 128, 0, 'h',
                                                        self.samurai.x, self.samurai.y, 128, 128)


class Attack:
    def __init__(self, samurai):
        self.samurai = samurai

    def enter(self, e):
        self.samurai.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.samurai.frame = (self.samurai.frame + 14 * ACTION_PER_TIME * game_framework.frame_time) % 14
        if int(self.samurai.frame) == 6:  # 7번째 프레임(0-based index 6)에서 화살 발사
            self.samurai.shoot_arrow()
        if int(self.samurai.frame) == 13:  # 14번째 프레임에서 Idle로 복귀
            self.samurai.state_machine.handle_state_event(('STOP', self.samurai.face_dir))

    def draw(self):
        if self.samurai.face_dir == 1:
            self.samurai.shot_image.clip_draw(int(self.samurai.frame) * 128, 0, 128, 128, self.samurai.x, self.samurai.y)
        else:
            self.samurai.shot_image.clip_composite_draw(int(self.samurai.frame) * 128, 0, 128, 128, 0, 'h',
                                                        self.samurai.x, self.samurai.y, 128, 128)


class StateMachine:
    def __init__(self, start_state, state_transitions):
        self.cur_state = start_state
        self.state_transitions = state_transitions
        self.cur_state.enter(('START', None))
        self.last_input_time = time.time()  # 마지막 입력 시간 초기화
        self.samurai = start_state.samurai  # Samurai 객체 참조

    def update(self):
        self.cur_state.do()
        current_time = time.time()
        if current_time - self.last_input_time >= 5.0 and self.cur_state != self.samurai.IDLE:  # 5초 경과 시 Idle로 전환
            self.cur_state.exit(('STOP', self.samurai.face_dir))
            self.next_state = self.samurai.IDLE
            self.next_state.enter(('STOP', self.samurai.face_dir))
            print(
                f'{self.cur_state.__class__.__name__} ---- (5s Idle Timeout) ----> {self.next_state.__class__.__name__}')
            self.cur_state = self.next_state

    def handle_state_event(self, event):
        for check_event in self.state_transitions[self.cur_state].keys():
            if check_event(event):
                self.cur_state.exit(event)
                self.next_state = self.state_transitions[self.cur_state][check_event]
                self.next_state.enter(event)
                print(
                    f'{self.cur_state.__class__.__name__} ---- {event_to_string(event)} ----> {self.next_state.__class__.__name__}')
                self.cur_state = self.next_state
                self.last_input_time = time.time()  # 입력 발생 시 시간 갱신
                return

        print(f'처리되지 않은 이벤트 {event_to_string(event)} 가 있습니다.')

    def draw(self):
        self.cur_state.draw()


class Samurai:
    idle_image = None
    run_image = None
    walk_image = None
    attack_image = None
    shot_image = None

    def __init__(self):
        if Samurai.idle_image == None:
            Samurai.idle_image = load_image('samurai_Archer/Walk.png')  # Idle은 Walk 이미지로 대체
        if Samurai.run_image == None:
            Samurai.run_image = load_image('samurai_Archer/Run.png')
        if Samurai.walk_image == None:
            Samurai.walk_image = load_image('samurai_Archer/Walk.png')
        if Samurai.attack_image == None:
            Samurai.attack_image = load_image('samurai_Archer/Attack_1.png')
        if Samurai.shot_image == None:
            Samurai.shot_image = load_image('samurai_Archer/shot.png')  # 경로 수정, 14프레임
        self.x, self.y = 400, 300
        self.frame = 0
        self.xdir, self.ydir = 0, 0
        self.face_dir = 1
        self.speed = WALK_SPEED_PPS

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {event_run: self.WALK, a_down: self.ATTACK},
            self.WALK: {lshift_down: self.RUN, event_stop: self.IDLE, event_run: self.WALK, a_down: self.ATTACK},
            self.RUN: {lshift_up: self.WALK, event_stop: self.IDLE, a_down: self.ATTACK},
            self.ATTACK: {}
        })

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN):
            cur_xdir, cur_ydir = self.xdir, self.ydir
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_LEFT:
                    self.xdir -= 1
                elif event.key == SDLK_RIGHT:
                    self.xdir += 1
                elif event.key == SDLK_UP:
                    self.ydir += 1
                elif event.key == SDLK_DOWN:
                    self.ydir -= 1
            elif event.type == SDL_KEYUP:
                if event.key == SDLK_LEFT:
                    self.xdir += 1
                elif event.key == SDLK_RIGHT:
                    self.xdir -= 1
                elif event.key == SDLK_UP:
                    self.ydir -= 1
                elif event.key == SDLK_DOWN:
                    self.ydir += 1

            if cur_xdir != self.xdir or cur_ydir != self.ydir:
                if self.xdir == 0 and self.ydir == 0:
                    self.state_machine.handle_state_event(('STOP', self.face_dir))
                else:
                    if self.speed == RUN_SPEED_PPS:
                        self.state_machine.handle_state_event(('RUN', None))
                    else:
                        self.state_machine.handle_state_event(('RUN', None))
        else:
            self.state_machine.handle_state_event(('INPUT', event))  # 모든 이벤트로 시간 갱신
        self.state_machine.last_input_time = time.time()  # 이벤트 발생 시 시간 갱신

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 30, self.y - 40, self.x + 30, self.y + 40  # 충돌 박스 (60x80), 필요 시 조정 가능

    def shoot_arrow(self):
        arrow = Arrow(self.x + self.face_dir * 50, self.y, self.face_dir)
        game_world.add_object(arrow, 1)
        game_world.add_collision_pair('samurai_Archer:arrow', None, arrow)

    def handle_collision(self, group, other):
        pass