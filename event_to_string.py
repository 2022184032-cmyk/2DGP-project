# event_to_string.py
def event_to_string(state_event):
    """이벤트의 모든 상세 정보를 문자열로 반환 (모든 키 자동 처리)"""
    from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP, SDL_MOUSEWHEEL
    import pico2d

    event_names = {
        SDL_KEYDOWN: 'KEYDOWN',
        SDL_KEYUP: 'KEYUP',
        SDL_MOUSEMOTION: 'MOUSEMOTION',
        SDL_MOUSEBUTTONDOWN: 'MOUSEBUTTONDOWN',
        SDL_MOUSEBUTTONUP: 'MOUSEBUTTONUP',
        SDL_MOUSEWHEEL: 'MOUSEWHEEL'
    }

    state_event_type = state_event[0]
    event = state_event[1]
    if state_event_type != 'INPUT':
        return f"{state_event}"

    key_names = {}
    for name in dir(pico2d):
        if name.startswith('SDLK_'):
            key_code = getattr(pico2d, name)
            key_name = name.replace('SDLK_', '')
            key_names[key_code] = key_name

    event_type = event_names.get(event.type, f'Unknown({event.type})')
    key_attr = getattr(event, 'key', None)
    if key_attr is not None:
        key_name = key_names.get(key_attr, f'key({key_attr})')
    else:
        key_name = ''

    info = f'{event_type}:{key_name}'
    return f"('{state_event_type}', {info})"