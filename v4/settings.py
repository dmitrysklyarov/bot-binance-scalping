#global settings
isContinue = True
waitCounter = 0

def increaseWaitCounter():
    global waitCounter
    waitCounter = waitCounter + 1

def resetWaitCounter():
    global waitCounter
    waitCounter = 0