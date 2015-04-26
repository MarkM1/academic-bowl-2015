# -------------------------------------------------------------------------------
# File:     game.py
# Author:   Mark Macerato
# Date:     April 29, 2015
# Desc:     This script is the main game program for the Academic Bowl.  It reads
#           the values of buttons conntected to the RPi's GPIO pins, and can
#           light up LEDs in response to specific button presses.
# -------------------------------------------------------------------------------
# Import GPIO module
import RPi.GPIO as GPIO

"""
    The following class, Team, represents a team participating in the competition.
    Teams have a state - they can be alive or dead, e.g., their buttons could be
    responsive or not.  For example, a team that answers incorrectly should be
    set dead while the other teams buzz in. Teams also have an LED on their
    table, and on the operator panel. Finally, they have a pin that their button
    is attatched to.
"""
class Team:
    def __init___(self, button, led_table, led_op name):
        self.button = button
        self.led_table = table
        self.led_op = led_op
        self.alive = False
        self.name = name

# Define a variable to hold the state of the game.  The author has opted to use
# a string for this representation, although many other possibilities exist.
state = ""

# Define the states of the game
# STANDBY is the state the exists while the operator is reading the question
STANDBY = "STANDBY"

# QUESTION is the state that exists while the teams are preparing their
# responses
QUESTION = "QUESTION"

# ANSWER is the state that exists after a team has buzzed in
ANSWER = "ANSWER"

# Create the teams
judge = Team(4, 23, 24, "JUDGE")
huberts = Team(25, 8, 7, "HUBERTS")
flower = Team(4, 17, 27, "FLOWER")
ryan = Team(22, 10, 9, "RYAN")

# Define operator pins
op = 2
yes = 3
no = 11 

# Collect them
teams = [judge, huberts, flower, ryan]

# Setup all GPIO pins
GPIO.setmode(GPIO.BCM)
for team in teams:
    GPIO.setup(team.button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(team.button, GPIO.RISING, bouncetime = 100) # ms
    GPIO.setup(team.led_op, GPIO.OUT)
    GPIO.setup(team.led_table, GPIO.OUT)

# Setup the operator pins
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(yes, GPIO.RISING, bouncetime = 100) # ms
GPIO.add_event_detect(no, GPIO.RISING, bouncetime = 100) # ms

"""
The following function is the task to be executed periodically in the standby
state.  It requires no parameters, and simply waits for a go-ahead from the
operator
"""
def standby():
    for team in teams:
        # All teams are in the next question
        team.alive = True
        GPIO.output(team.led_op, False)
        GPIO.output(team.led_table, False)
    GPIO.wait_for_edge(op, GPIO.RISING)
    # Clean up team event detection
    for team in teams:
        GPIO.event_detected(team.button)
    GPIO.remove_event_detect(op)
    state = QUESTION

"""
The following function handles the question mode.
"""
def question(quesiton_init):
    if question_init:
        GPIO.add_event_detect(op, GPIO.RISING)
        # If all teams are out, go to standby
        team_left = False
        for team in teams:
            team_left = team_left or team.alive
        if not team_left:
            state = STANDBY
            return None
    team_buzzed = None
    for team in teams:
        if team.alive:
            # Light up living teams
            GPIO.output(team.led_table, True)
            if GPIO.event_detected(team.button):
                team_buzzed = team
                state = ANSWER
                break
    # Operator ends the question
    if GPIO.event_detected(op):
        state = STANDBY
    # Keep clearing yes and no buttons
    GPIO.event_detected(yes)
    GPIO.event_detected(no)
    return team_buzzed
"""
The following function handles the answer mode
"""
def answer(team_buzzed):
    # Turn off all teams that failed to answer
    for team in teams:
        if team is not team_buzzed:
            GPIO.output(team.led_table, False)
    # Light up the team on the operator board
    GPIO.output(team_buzzed.led_op, True)
    # Wait for them to answer
    if GPIO.event_detected(yes):
        state = STANDBY
    elif GPIO.event_detected(no):
        state = QUESTION
        team_buzzed.alive = False
    

# The main game loop runs indefinately, until interrupted by a Ctrl+C
state = STANDBY

question_init = True
team_buzzed = None

while True:
    try:
        if state == STANDBY:
            standby()
            question_init = True
        elif state == QUESTION:
            team_buzzed = question()
            question_init = False
        elif state == ANSWER:
            answer(team_buzzed, answer_init)
            question_init = True
    except KeyboardInterrupt:
        sys.exit()
