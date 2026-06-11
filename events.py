import pygame
from enum import IntEnum
from typing import Callable

from data_types.vector import Vector2D


class InputKeys(IntEnum):
    W = pygame.K_w
    S = pygame.K_s
    A = pygame.K_a
    D = pygame.K_d

    SPACE = pygame.K_SPACE
    LSHIFT = pygame.K_LSHIFT
    TAB = pygame.K_TAB
    C = pygame.K_c


class MouseButton(IntEnum):
    # indices into pygame.mouse.get_pressed()
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class EventManager:

    def __init__(self):
        # Instance-owned so two managers can never tread on each other's
        # bindings (these were class attributes before).
        self.input_events: dict[InputKeys, Callable[[], None]] = {}
        self.mouse_hold_events: dict[int, Callable[[Vector2D], None]] = {}
        self.should_exit: bool = False
        self.mouse_pos: Vector2D = Vector2D(0, 0)

    def add_input_event(self, input_key: InputKeys, func: Callable[[], None]):
        """
        Adds an event to be called upon when the assosiated input key is pressed
        Use lambdas or partials to pass functions with parameters
        """

        self.input_events[input_key] = func

    def add_mouse_hold_event(self, button: MouseButton, func: Callable[[Vector2D], None]):
        """
        Fires every frame the given mouse button is held down, handing the
        callback the current cursor position. This is what gives hold-to-fire;
        the actual rate is still gated by the shooter's own cooldown.
        """
        self.mouse_hold_events[button] = func

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.should_exit = True

            if event.type == pygame.KEYDOWN:
                pressed_key = event.key
                if pressed_key in self.input_events.keys():
                    self.input_events[pressed_key]()

        # Mouse is polled rather than event-driven: aim wants the live cursor
        # position every frame and firing wants to repeat while the button is
        # held, neither of which the KEYDOWN-style queue gives cleanly.
        mx, my = pygame.mouse.get_pos()
        self.mouse_pos = Vector2D(mx, my)

        pressed = pygame.mouse.get_pressed()
        for button, func in self.mouse_hold_events.items():
            if button < len(pressed) and pressed[button]:
                func(self.mouse_pos)
