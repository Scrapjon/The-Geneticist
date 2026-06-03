import pygame
from enum import IntEnum
from typing import Callable

class InputKeys(IntEnum):
    W = pygame.K_w
    S = pygame.K_s
    A = pygame.K_a
    D = pygame.K_d

    SPACE = pygame.K_SPACE
    LSHIFT = pygame.K_LSHIFT

class EventManager:
    
    input_events: dict[InputKeys, Callable[[], None]] = {}
    should_exit: bool = False

    
    def add_input_event(self, input_key: InputKeys, func: Callable[[], None]):
        """ 
        Adds an event to be called upon when the assosiated input key is pressed
        Use lambdas or partials to pass functions with parameters
        """

        self.input_events[input_key] = func

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.should_exit = True

            if event.type == pygame.KEYDOWN:
                pressed_key = event.key
                if pressed_key in self.input_events.keys():
                    self.input_events[pressed_key]()