def print_options(action_phrase: str, actions: dict, choice_phrase: str) -> None:
    '''
    formats any list of choices
    '''

    l_action = list(actions)


    print(f"{action_phrase} \n")

    [print(f"\t[{l_action.index(x)}] {x}") for x in actions.keys()]

    print(f"\n{choice_phrase}")
    choice = input()

    if choice.isdigit():
        choice = int(choice)
        if choice < len(list(l_action)) and choice > -1:
            return l_action, choice

def print_callable(action_phrase: str, actions: dict, choice_phrase: str) -> None:
    l_action, choice = print_options(action_phrase, actions, choice_phrase)

    actions[l_action[choice]]()

def print_constants(action_phrase: str, actions: dict, choice_phrase: str) -> int:
    '''
    Returns the constant chosen
    '''
    l_action, choice = print_options(action_phrase, actions, choice_phrase)

    return actions[l_action[choice]]
