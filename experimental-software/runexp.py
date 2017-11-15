#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Last mod: Jun/20/2016


import time
import codecs
import random
from psychopy import core, visual, event


INSTRUCTION1 = (
  u'Herzlich Willkommen zum Experiment!\n\n'
  u'In jedem Durchgang werden Ihnen gleichzeitig zwei Städtenamen '
  u'präsentiert. Ihre Aufgabe ist es, unter den beiden Städten diejenige mit '
  u'der höheren Einwohnerzahl auszuwählen. Benutzen Sie die Tasten < und - '
  u'um Ihre Wahl zu treffen.\n\n'
  u'Wenn Sie glauben, die linke Stadt hat mehr Einwohner, drücken Sie <.\n\n'
  u'Wenn Sie glauben, die rechte Stadt hat mehr Einwohner, drücken Sie -.\n\n'
  u'Weiter mit beliebiger Taste ...'
)

INSTRUCTION2 = (
  u'Bitte versuchen Sie - so oft wie möglich - die Stadt zu wählen, von der '
  u'Sie schon einmal gehört haben. Dies ist eine gute Strategie, da bekannte '
  u'Städte üblicherweise auch mehr Einwohner haben.\n\n'
  u'Also wählen Sie Städte, die Sie kennen, unabhängig davon, was Sie über '
  u'sie wissen.\n\n'
  u'Weiter mit beliebiger Taste ...'
)

INSTRUCTION3 = (
  u'Vielen Dank.\n\n'
  u'Nun wollen wir Sie noch fragen, ob Sie von den eben dargebotenen Städten '
  u'vor dem Experiment schon einmal gehört haben oder ob Sie Ihnen unbekannt '
  u'waren.\n\n'
  u'Weiter mit beliebiger Taste ...'
)


def trial(city_left, city_right):
    """
    City-size paired comparison task
    """
    leftTS.text  = city_left
    rightTS.text = city_right

    questionTS.draw()
    fixpoint.draw()
    leftTS.draw()
    rightTS.draw()
    win.flip()

    timer.reset()
    response = None
    while response not in [city_left, city_right]:
        pressed_key = event.waitKeys(timeStamped=timer)
        if pressed_key[0][0] in ['q', 'escape']:
            core.quit()
        if pressed_key[0][0] == 'less':
            response = city_left
        if pressed_key[0][0] == 'minus':
            response = city_right

    questionTS.draw()
    fixpoint.draw()
    win.flip()
    core.wait(0.4)

    ## Save data
    datfile.write('%s;%s;%s;%1.4f\n' %
                  (city_left, city_right, response, pressed_key[0][1]))


def pause(text):
    pauseTS = visual.TextStim(win, text, height=th)
    pauseTS.draw()
    win.flip()
    core.wait(1)
    pauseTS.draw()
    visual.TextStim(win, 'Weiter mit beliebiger Taste ...', pos=(0, -200),
                    height=th, wrapWidth=ww).draw()
    win.flip()
    event.waitKeys()


def instruction(text):
    visual.TextStim(win, text, height=th, wrapWidth=ww).draw()
    win.flip()
    core.wait(1)
    if event.waitKeys()[0] in ['q', 'escape']:
        core.quit()
    win.flip()
    core.wait(1)


def askKnowledge(cityname, citycountry, distractors):
    """
    Knowledge questions
    """
    questionTS.text = 'Kennen Sie die Stadt %s?' % cityname
    questionTS.draw()
    visual.TextStim(win,
                    u'[1] Ja, ich kenne den Namen.\n' +
                    u'[2] Nein, ich habe vorher noch nie davon gehört.',
                    height=th, wrapWidth=ww).draw()
    win.flip()

    is_known = None
    while is_known not in ['y', 'n']:
        pressed_key = event.waitKeys()
        if pressed_key[0] in ['q', 'escape']:
            core.quit()
        if pressed_key[0] == '1':
            is_known = 'y'
        if pressed_key[0] == '2':
            is_known = 'n'

    """
    Which country?
    """
    questionTS.text = u'In welchem Land (schätzen Sie) liegt %s?' % cityname
    questionTS.draw()

    distractorA, distractorB, distractorC = distractors
    respcat = [citycountry, distractorA, distractorB, distractorC]
    random.shuffle(respcat)

    visual.TextStim(win, text='[1] %s\n[2] %s \n[3] %s\n[4] %s' %
                    tuple(respcat), height=th).draw()
    win.flip()

    response_country = None
    while response_country not in respcat:
        pressed_key = event.waitKeys()
        if pressed_key[0] in ['q', 'escape']:
            core.quit()
        if pressed_key[0] == '1':
            response_country = respcat[0]
        if pressed_key[0] == '2':
            response_country = respcat[1]
        if pressed_key[0] == '3':
            response_country = respcat[2]
        if pressed_key[0] == '4':
            response_country = respcat[3]

    """
    Population?
    """
    questionTS.text = u'Wieviele Einwohner (schätzen Sie) hat %s?' % cityname
    input_text = ""
    responseTS = visual.TextStim(win, '> %s' % input_text, height=th,
                                 wrapWidth=ww)
    taskTS  = visual.TextStim(win,
      u'Geben Sie eine beliebige Zahl ein.\n'
      u'Korrektur mit der Löschen-Taste.\nBestätigen mit der Eingabe-Taste.',
      pos=(0, -200), height=.7*th, color=(.2, .2, 1), wrapWidth=ww)
    questionTS.setAutoDraw(True)
    responseTS.setAutoDraw(True)
    taskTS.setAutoDraw(True)
    win.flip()

    response = None
    while response != 'finish':
        pressed_key = event.waitKeys()
        if pressed_key[0] in ['q', 'escape']:
            core.quit()
        if pressed_key[0] in [str(i) for i in range(10)]:
            input_text += pressed_key[0]
        if pressed_key[0] in ['backspace'] and input_text != "":
            input_text = input_text[:-1]  # delete last character
        responseTS.text = '> %s' % input_text
        win.flip()
        if pressed_key[0] == 'return' and input_text != "":
            response = 'finish'
            questionTS.setAutoDraw(False)
            responseTS.setAutoDraw(False)
            taskTS.setAutoDraw(False)

    return (cityname, is_known,
            response_country,
            citycountry,
            distractorA,
            distractorB,
            distractorC,
            input_text)


"""
Main routine starts here
"""
## Collect subject info
expinfo = dict( id = raw_input('Subject ID: '),
               age = raw_input('Subject age: '),
               sex = raw_input('Subject gender (f/m): '),
           session = raw_input('Session file: '),
           student = raw_input('Student? (y/n): '),
          semester = raw_input('Semester (number/NA): '),
            tstamp = time.strftime("%Y%m%d_%H%M", time.localtime()))

win = visual.Window(fullscr=True, allowGUI=False, color='black', units='pix')
timer = core.Clock()  # keep track of time during each trial

## Create stimuli
th         = 38    # text height
ww         = 1000  # wrap width
questionTS = visual.TextStim(win, u'Welche Stadt hat mehr Einwohner?',
                             pos=(0, 200), height=th, wrapWidth=ww)
fixpoint   = visual.Circle(win, radius=3, lineColor=1, fillColor=1)
leftTS     = visual.TextStim(win, pos=(-200, 0), height=th)
rightTS    = visual.TextStim(win, pos=( 200, 0), height=th)


## Paired comparisons
instruction(INSTRUCTION1)  # INSTRUCTION2 called by session file if necessary

with codecs.open('../raw-data/subj' + expinfo['id'] + '-' + expinfo['tstamp'] +
                 '-pc.txt', 'w', encoding='utf-8') as datfile:
    datfile.write('# ' + str(expinfo) + '\n')
    datfile.write('city_left;city_right;response;rt\n')
    with open('session/' + expinfo['session'],
              'r') as sesfile:
        exec(sesfile)


## Knowledge questions
instruction(INSTRUCTION3)

with codecs.open('../raw-data/subj' + expinfo['id'] + '-' + expinfo['tstamp'] +
                 '-know.txt', 'w', encoding='utf-8') as datfile:
    datfile.write('# ' + str(expinfo) + '\n')
    datfile.write('Name;Know;resp_country;Country;DistA;DistB;DistC;Size\n')
    for city_country in zip(cities, countries):
        name, country = city_country
        distractors = list(set(countries))  # unique countries
        distractors.remove(country)
        datfile.write('%s;%s;%s;%s;%s;%s;%s;%s\n' %
                      askKnowledge(name, country,
                                   random.sample(distractors, 3)))


visual.TextStim(win, u'Vielen Dank für Ihre Teilnahme.', height=th,
                wrapWidth=ww).draw()
win.flip()
core.wait(1)
event.waitKeys()
