import time
from psychopy import core, visual, event
import random

INSTRUCTION = "Lorem ipsum"

def trial(cityA, cityB):
    """
    Executes presentation and recording of one Trial.
    """
    text_left.text = cityA
    text_right.text = cityB

    fixpoint.draw()
    text_left.draw()
    text_right.draw()
    win.flip()

    timer.reset()
    response = None
    while response not in [cityA, cityB]:
        pressed_key = event.getKeys(timeStamped=timer)
        if pressed_key and pressed_key[0][0] in ['q', 'escape']:
            core.quit()
        if pressed_key and pressed_key[0][0] == 'less':
            response = cityA
        if pressed_key and pressed_key[0][0] == 'minus':
            response = cityB

    ## Save data
    datfile.write('%s;%s;%s;%7.4f\n' %
                  (cityA, cityB, response, pressed_key[0][1]))

def pause(message):
    visual.TextStim(win,message, height=th).draw()
    win.flip()
    core.wait(10)
    if event.waitKeys()[0] in ['q', 'escape']:
        core.quit()

    win.flip()

def askProminence(cityname, citycountry, distractors):
    """
    Bekanntheit
    """
    visual.TextStim(win, pos=(0,200), text='Kennen Sie %s?\n < Ja\n - Nein' % (cityname),
                                    height=th).draw()

    win.flip()

    is_known = None
    while is_known not in ['y', 'n']:
        pressed_key = event.getKeys(timeStamped=timer)
        if pressed_key and pressed_key[0][0] in ['q', 'escape']:
            core.quit()
        if pressed_key and pressed_key[0][0] == 'less':
            is_known = 'y'
        if pressed_key and pressed_key[0][0] == 'minus':
            is_known = 'n'


    """
    Land
    """
    visual.TextStim(win, pos=(0,200), text='In welchem Land liegt %s?' % (cityname),
                                            height=th).draw()

    distractorA, distractorB, distractorC = distractors
    lst = list((citycountry, distractorA, distractorB, distractorC))
    random.shuffle(lst)

    first, second, third, fourth = lst

    visual.TextStim(win,
                    pos=(0,-100),
                    text='[1] %s\n[2] %s \n[3] %s\n[4] %s\n[5] Keine Ahnung' %
                    (first, second, third, fourth),
                    height=th).draw()

    win.flip()


    response_country = None
    while response_country not in lst + ['KA']:
        pressed_key = event.getKeys(timeStamped=timer)
        if pressed_key and pressed_key[0][0] in ['q', 'escape']:
            core.quit()
        if pressed_key and pressed_key[0][0] == '1':
            response_country = first
        if pressed_key and pressed_key[0][0] == '2':
            response_country = second
        if pressed_key and pressed_key[0][0] == '3':
            response_country = third
        if pressed_key and pressed_key[0][0] == '4':
            response_country = fourth
        if pressed_key and pressed_key[0][0] == '5':
            response_country = 'KA'

    """
    Size
    """
    input_text = ""

    response_text = visual.TextStim(win,
                                    pos=(0,200),
                                    text='Wieviele Einwohner hat %s?\n\n\n%s'
                                    % (cityname, input_text)
                                    , height=th)

    response_text.setAutoDraw(True)
    win.flip()

    response = None
    while response != 'finish':
        pressed_key = event.getKeys(timeStamped=timer)
        if pressed_key and pressed_key[0][0] in ['q', 'escape']:
            core.quit()
        if pressed_key and pressed_key[0][0] in ['1', '2', '3', '4','5','6','7','8','9','0']:
            input_text = input_text + pressed_key[0][0]
        if pressed_key and pressed_key[0][0] in ['backspace'] and input_text != "":
            input_text = input_text[:-1] #letzten character entfernen
        response_text.text= 'Wieviele Einwohner hat %s?\n\n\n%s' % (cityname, input_text)
        win.flip()
        if pressed_key and pressed_key[0][0] == 'return' and input_text != "":
            response = 'finish'
            response_text.setAutoDraw(False)

    return (cityname, is_known,
            response_country,
            citycountry,
            distractorA,
            distractorB,
            distractorC,
            input_text)



def getCountries(file_path):
    with open(file_path, 'r') as cities:
        cities.readline()
        cities.readline()
        cities.readline()
        cities.readline()
        countries = list()
        for line in cities:
            number, position, name, size, country, continent = line.strip('\n').split(';')
            countries.append(country)
        countries = set(countries)
        return countries


"""
Beginn Ablauf
"""
## Collect subject info
expinfo = dict( id = raw_input('Subject ID: '),
               age = raw_input('Subject age: '),
               sex = raw_input('Subject gender (f/m): '),
           session = raw_input('Session file: '),
            tstamp = time.strftime("%Y%m%d_%H%M", time.localtime()))

win = visual.Window(fullscr=True, allowGUI=False, units='pix')
timer = core.Clock()  # keep track of time during each trial

## Create stimuli
fixpoint   = visual.Circle(win, radius=3, lineColor=1, fillColor=1)
th         = 38  # text height
text_left  = visual.TextStim(win, pos=(-300,0), height=th)
text_right = visual.TextStim(win, pos=(300,0), height=th)

## Instructions
visual.TextStim(win,INSTRUCTION, height=th).draw()
win.flip()
if event.waitKeys()[0] in ['q', 'escape']:
    core.quit()

win.flip()
core.wait(1)

with open('data/subj' + expinfo['id'] + '-' + expinfo['tstamp'] + '.txt',
          'w') as datfile:
    datfile.write('# ' + str(expinfo) + '\n')
    datfile.write('cityA;cityB;response;rt\n')
    with open('session/' + expinfo['session'], 'r') as sesfile:
        exec(sesfile)


with open('session/cities.txt', 'r') as cities:
    # skip header
    cities.readline()
    cities.readline()
    cities.readline()
    cities.readline()

    countries = getCountries('session/cities.txt')
    file_path = 'data/subj' + expinfo['id'] + '-' + expinfo['tstamp'] + 'abfrage.txt'
    with open(file_path, 'w') as datfile:
        datfile.write('Name;Known;resp_country;Country;DistA;DistB;DistC;Size\n')
        for line in cities:
            number, position, name, size, country, continent = line.strip('\n').split(';')
            distractors = countries.copy()
            distractors.remove(country)
            random.shuffle(list(distractors))
            distractors = list(distractors)[:3]
            response_line = askProminence(name, country, distractors)
            datfile.write('%s;%s;%s;%s;%s;%s;%s;%s\n' % response_line)


visual.TextStim(win, 'Thank you', height=th).draw()
win.flip()
event.waitKeys()
