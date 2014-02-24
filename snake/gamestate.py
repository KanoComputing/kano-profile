import kanoprofile as kp

app_name = 'make-snake'
state = dict()


def load_state():
    global state

    try:
        state = kp.load_app_state(app_name)
        init_states = kp.get_gamestate_variables(app_name)

        # loop throught all states and initialize them with zero
        for s in init_states:
            if s not in state:
                state[s] = 0
    except Exception:
        pass


def save_state():
    global state

    try:
        kp.save_app_state(app_name, state)
    except Exception:
        pass
