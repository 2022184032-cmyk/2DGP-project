# play_mode.py
from pico2d import *
import game_framework
import game_world
from samurai_Archer import Samurai
from arrow import Arrow

def handle_events():
    events = get_events()
    for event in events:
        game_world.handle_collisions()  # handle_collision -> handle_collisions로 수정
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            game_world.samurai.handle_event(event)

def init():
    game_world.clear()
    game_world.samurai = Samurai()
    game_world.add_object(game_world.samurai, 1)

def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    pass

def pause():
    pass

def resume():
    pass