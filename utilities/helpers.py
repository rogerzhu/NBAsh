from bs4 import element
import os
import fake_useragent


# helper functions
def get_header():
    location = os.getcwd() + '/agent.json'
    ua = fake_useragent.UserAgent(path=location)
    return ua.random


def GetElementsByClass(item, tag, class_name):
    if item.find_all(tag, {'class': class_name}) is not None:
        return item.find_all(tag, {'class': class_name})


def GetOneElementByClass(item, tag, class_name, default_value=''):
    if item.find(tag, {'class': class_name}) is not None:
        return item.find(tag,  {'class': class_name})
    else:
        return default_value


def GetTextOfItem(item, default_value=''):
    if item is not None and isinstance(item, element.Tag):
        return item.get_text()
    else:
        return default_value


def ClearScreen(screen):
    for i in range(0, screen.height + 1):
        screen.move(0, i)
        screen.draw(screen.width, i, char=' ')
