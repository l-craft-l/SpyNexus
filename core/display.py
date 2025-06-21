import time
import sys

########################
#Colors output#############
########################

##Print colour

def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk))

##Colour caracter

def maCyan(text): return f'\033[96m{text}\033[00m'
def maGreen(text): return f'\033[92m{text}\033[00m'
def maYellow(text): return f'\033[93m{text}\033[00m'
def maRed(text): return f'\033[91m{text}\033[00m'
def maBlue(text): return f'\033[94m{text}\033[00m'
def maMagenta(text): return f'\033[95m{text}\033[00m'
def maBlack(text): return f'\033[90m{text}\033[00m'
def maOrange(text): return f'\033[38;5;214m{text}\033[00m'
def maPink(text): return f'\033[38;5;213m{text}\033[00m'
def maLightBlue(text): return f'\033[38;5;153m{text}\033[00m'
def maLightGreen(text): return f'\033[38;5;112m{text}\033[00m'
def maLightYellow(text): return f'\033[38;5;227m{text}\033[00m'
def maBrown(text): return f'\033[38;5;94m{text}\033[00m'
def maTeal(text): return f'\033[38;5;30m{text}\033[00m'
def maSkyBlue(text): return f'\033[38;5;75m{text}\033[00m'

##Special output

def maBold(text): return f'\033[1m{text}\033[00m'
def maUnderline(text): return f'\033[4m{text}\033[00m'
def backRed(text): return f'\033[41m{text}\033[0m'

##Icons

display_info = f'{maBold("[")}{maCyan("i")}{maBold("]")}'
display_error = f'{maBold("[")}{maRed("!!!")}{maBold("]")}'
display_validate = f'{maBold("[")}{maGreen("√")}{maBold("]")}'
display_extra = f'{maBold("[")}{maBlue("×")}{maBold("]")}'
display_question = f'{maBold("[")}{maYellow("?")}{maBold("]")}'

##faces

happy = '(⁠✷⁠‿⁠✷⁠)'
sad = '(⁠╥⁠﹏⁠╥⁠)'
nervous = '(⁠;⁠ŏ⁠﹏⁠ŏ⁠)'
pointing = '←⁠(⁠>⁠▽⁠<⁠)⁠ﾉ'
angry = '(⁠╯⁠ರ⁠ ⁠~⁠ ⁠ರ⁠)⁠╯⁠︵⁠ ⁠┻⁠━⁠┻'
surprised = '(⁠´⁠⊙⁠ω⁠⊙⁠`⁠)!'
waiting = '(⁠-⁠_⁠-⁠;⁠)⁠・⁠・⁠・'

##write effect
def write_effect(text, speed):
    if not isinstance(text, str):
        text = str(text)
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def wait_out(wait):
    w_text = f'{maYellow("..........")} {maYellow(waiting)}'
    write_effect(w_text, 0.05)
    time.sleep(wait)

def space_between():
    prYellow("--------------------------------------------")

def between_tag(name_tag):
    write_effect(f'\n--------{maSkyBlue(name_tag)}--------\n', 0.005)

def check_key(keyb):
    keyb = keyb.lower()
    if keyb != 'y' and keyb != 'n':
        write_effect(f"\n{display_error} Please enter a valid option. ({maGreen('y')}/{maRed('n')})", 0.03)
        return None
    elif keyb == 'y':
        return True
    else:
        return False
