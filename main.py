import pygame
import sys
from app import TypingApp


def main():
    pygame.init()
    app = TypingApp()
    app.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
