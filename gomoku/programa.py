# encoding: utf-8
from gomoku_lib.display import Display
from gomoku_lib.state import State
from gomoku_lib.events import Mouse
from gomoku_lib.exceptions import StopPropagation, Quit
from gomoku_lib.minimax import minimax

__all__ = ["Display", "State"]
inf = float('inf')

def process_mouse_click(display, state, ev):
    if not ev.match(Mouse.LEFT_CLICKED):
        return state
    y, x = display.locate(ev.y, ev.x)
    state = state.mark(y, x)
    return display.trigger(display.MARK_EVENT, state, y=y, x=x)


def finish(display, state, *args, **kwargs):
    raise Quit()
    return state


def check_won(display, state, y, x):
    finished = state.finished()
    won = state.won(y, x)
    if finished and won:
        # Detect the player who won...
        winner = state.max_sequence(y, x).player
        feeling = "_o_"
        if winner in display.computer_player:
            feeling = "\o/"
        state = state.display("The player {} won {}".format(winner, feeling))
        display.off(display.MOUSE_EVENT)
        display.once(display.MOUSE_EVENT, finish)
        raise StopPropagation(state)
    elif finished and not won:
        state = state.display("No winners :(")
        display.off(display.MOUSE_EVENT)
        display.once(display.MOUSE_EVENT, finish)
    return state


def run_ai(display, state, *args, **kwargs):
    _, s = minimax(state, 2, -inf, inf, True)
    return display.trigger(display.MARK_EVENT, s, s.last_move.y, s.last_move.x)


def should_ai_run(display, state, y, x):
    if state.player in display.computer_player:
        # Update the screen so the user sees the click instantly..
        display.draw(state)
        display.trigger_delay(display.IA_MOVE)
    return state


def undo(display, state, ev, *args, **kwargs):
    """
    Desfaz o status ate a ultima jogada do jogador..
    """
    if ev.upper() == "U" and state.player not in display.computer_player:
        p = state.parent
        while state.last_move == p.last_move or p.player != state.player:
            p = p.parent
        return p
    return state

def clear_message(display, state, ev, *args, **kwargs):
    if not ev.match(Mouse.LEFT_CLICKED) or not state.message:
        return state
    return state.display(None)

if __name__ == "__main__":
    state = State.get_initial_state()
    display = Display()
    display.on(display.MOUSE_EVENT, process_mouse_click)
    display.on(display.MARK_EVENT, should_ai_run)
    display.on(display.MARK_EVENT, check_won)
    display.on(display.KEY_EVENT, undo)
    display.on(display.IA_MOVE, run_ai)
    display.on(display.MOUSE_EVENT, clear_message)
    display.loop(state)
