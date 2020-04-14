#Autor: Michal Dostal, xdosta51
#Program: Interpret jazyka ippcode20

import sys #parse arg
import xml.etree.ElementTree as ET #parse XML
import re #regex
rozsirenije=False
insta=False
rozsirenifile=""
input_arg="" #soubor pro input
source_arg="" #soubor pro source
input_text="" #text na stdin input
source_text="" #text na stdin source
myList = {} #list instrukci a argumentu
stacek = [] #stack na defvar
# Funkce na kontrolu spravneho nazvu pro promennou
def upravstring(stringnaupravu):
    stringnaupravu = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x.group(1))), stringnaupravu)
    return stringnaupravu
def controlvar(var1):
    if var1.attrib['type'] != 'var':
        exit(32)
    if (re.match('^(LF|TF|GF)@[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$', var1.text)):
        return True
    else:
        return False
# Funkce na kontrolu spravneho nazvu navesti
def controllabel(var1):
    if var1.attrib['type'] != 'label':
        exit(32)
    if (re.match('^[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$', var1.text)):
        return True
    else:
        return False
# Funkce na kontrolu spravneho nazvu symbolu, coz je konstanta nebo promenna
def controlsymb(var1):
    if var1.attrib['type'] in ['int', 'bool', 'string', 'nil']:
        if var1.attrib['type'] == 'int':
            if(re.match('^[-+]?[0-9]+$', var1.text)):
                return "int"
        if var1.attrib['type'] == 'bool':
            if(re.match('^(true|false)$', var1.text)):
                return "bool"
        if var1.attrib['type'] == 'nil':
            
            if(re.match('^nil$', var1.text)):
                return "nil"
        if var1.attrib['type'] == 'string':
            return "string"
        else:
            return False
    elif (re.match('^(LF|TF|GF)@[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$', var1.text)):
            return "var"
    else:
        exit(32)
# funkce na kontrolu spravneho typu
def controlType(var1):
    if var1.attrib['type'] != "type":
        exit(32)
    if var1.text is None or not re.match('^(int|bool|string)$', var1.text):
        exit(32)
    return True
# zde zacina parse argumentu, implementovaneho manualne bez funkce getopts ci argparse
if (len(sys.argv) <= 1): # nebyl zadan zadny argument vede na chybu povinny je jeden
    exit(10)
for argum in sys.argv: # cyklus ktery prochazi pres vsechny argumenty
    if argum == "--help" or argum =="--h":
        if len(sys.argv) == 2:
            print("Zde bude vypsana napoveda")
            exit(0) # byla zadana napoveda a byl to jen jeden argument vypise se napovedi a exit kod 0
        else:
            exit(10) # byla sice zadana napoveda, ale taky k tomu byl zadan jeste nejaky argument, to samozrejme vede na chybu
    elif argum.find("--input=") != -1: # nasli jsme argument input, to znamena ze nam byl zadan nazev souboru s input textem
        input_arg = argum[8:]
        if (input_arg):
            continue
        else: # pokud za tim nic nebylo spatny argument zrovna koncime
            exit(10)
    elif argum.find("--source=") != -1: # nasli jsme argument source, byl nam zadan nazev souboru, kde je telo programu XML
        source_arg = argum[9:]
        if (source_arg):
            continue
        else: # pokud chybel koncime s chybou
            exit(10)
    elif argum.find("--stats=") != -1:
        rozsirenifile = argum[8:]
        rozsirenije = True
        if rozsirenifile:
            continue
        else:
            exit(10)
    elif argum == "./interpret.py": # prvni argument je nazev souboru skipujeme
        continue
    elif argum == "interpret.py": # prvni argument je nazev souboru skipujeme
        continue   
    elif argum == "--insts": # prvni argument je nazev souboru skipujeme
        insta = True
        continue  
    elif argum == "--vars": # prvni argument je nazev souboru skipujeme
        insta = True
        continue   
    else: # jiny argument vede na chybu pro zatim neni implementovani rozsireni
        exit(10)
if not source_arg and not input_arg:
    exit(10)
polacek = []
if rozsirenije:
    for artanges in sys.argv:
        if artanges == "--vars":
            polacek.append("vars")
        elif artanges == "--insts":
            polacek.append("inst")
        else:
            continue
if not rozsirenije and insta:
    exit(10)

# pokud nam nebyl zadan input soubor, nacteme si to ze vstupu
my_stdin = sys.stdin
if input_arg:
    try: # pokud nam by zadan pokusim se otevrit pokud to nepujde koncime s chybou
        sys.stdin = open(input_arg, "r")
    except: 
        exit(11)         
if not source_arg:# pokud nam nebyl zadani soubor s program nacteme si ho ze vstupu
    for line in my_stdin:
        source_text += line
else:
    try: # pokud nam byl zadan spatne koncime s chybou
        fource = open(source_arg, "r")
        source_text=(fource.read())
    except:
        exit(11)

try: # zde si nacteme XML program pokud neni soubor nacteme ze stringu, jinak bereme soubor
    if not source_arg:
        root = ET.fromstring(source_text)
    else:
        tree = ET.parse(source_arg)
        root = tree.getroot()
except FileNotFoundError: # byl problem se souborem koncime s chybou
    exit(11)
except Exception as e: # xml ma spatny format koncime s chybou 31
    exit(31)
#kontrola spravnosti jazyka
if str(root.attrib['language']).lower() != 'ippcode20':
    exit(32)
#kontrola zda je spravne root
for atribs in root.attrib:
    if atribs not in ['language', 'name', 'description']:
        exit(32)
#kontrola zda je spravne root.tag
if root.tag != 'program':
    exit(32)
#kontrola zda je language obsazen
if 'language' not in root.attrib:
    exit(31)
dir_labels = {} # slovnik navesti
laboli = []
napoli_argumentu = []
dvestejneorderinstrukce = []
for instruction in root: # zaciname cyklit pre xml dokument
    if not len(instruction.attrib) == 2:
        exit(32)
    if instruction.tag != 'instruction': # kontrola zda je instruction
        exit(32)
    if instruction.find('opcode'): # kontrola zda je opcode
        exit(32)
    for argum in instruction: # kontrola zda jsou spravne argumenty
        if argum.tag != "arg1" and argum.tag != "arg2" and argum.tag != "arg3":
            exit(32)
    try:
        instruction.attrib['opcode'] = str(instruction.attrib['opcode']).upper() # prevedeme si opcode do upper
    except:
        exit(32)
    try: # osetreni prazdneho stringu, vedlo to na chybu
        if instruction[1].attrib:
            if not instruction[1].text:
                instruction[1].text = ''
        if instruction[2].attrib:
            if not instruction[2].text:
                instruction[2].text = ''
    except:
        pass # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu
    
    try:
        int(instruction.attrib['order'])
    except:
        exit(32)
    if instruction.attrib['order'] == "0":
        exit(32)
    try:
        if instruction.attrib['order'] in dvestejneorderinstrukce:
            exit(32)
        else:
            dvestejneorderinstrukce.append(instruction.attrib['order'])
    except:
        exit(32)
    stackprodvastejneargumenty = []
    if instruction.attrib['order'] != 0:
        if int(instruction.attrib['order']) < 0:
            exit(32)

    for testovani in instruction:
        if testovani.tag[3:] in stackprodvastejneargumenty:
            exit(32)
        else:
            stackprodvastejneargumenty.append(testovani.tag[3:])

    for argumenty3 in instruction:
        if argumenty3.tag[3:] == "3":
            if (len(instruction)) <= 2:
                exit(32)
            napoli_argumentu.append(argumenty3)
    for argumenty2 in instruction:
        if argumenty2.tag[3:] == "2":
            if (len(instruction)) <= 1:
                exit(32)
            napoli_argumentu.append(argumenty2)
    for argumenty1 in instruction:
        if argumenty1.tag[3:] == "1":
            napoli_argumentu.append(argumenty1)

    try:
        instruction[0] = napoli_argumentu.pop()
    except:
        pass
    try:
        instruction[1] = napoli_argumentu.pop()
    except:
        pass  
    try:
        instruction[2] = napoli_argumentu.pop()
    except:
        pass
        

    if instruction.attrib['opcode'] in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'BREAK', 'RETURN']:
        if (len(list(instruction)) == 0):
            myList[instruction.attrib['order']] = instruction.attrib['opcode']
        else: 
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['DEFVAR', 'POPS']:
        if (len(list(instruction)) == 1):
            if not (controlvar(instruction[0])):
                exit(32)
            else:  
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text
        else:
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['PUSHS', 'WRITE', 'DPRINT', 'EXIT']:
        if (len(list(instruction)) == 1):
            if not(controlsymb(instruction[0])):
                exit(32)
            else:
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text
        else:
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['CALL', 'JUMP', 'LABEL']:
        if (len(list(instruction)) == 1):
            if not(controllabel(instruction[0])):
                exit(32)
            else:
                if instruction.attrib['opcode'] == "LABEL":
                    if instruction[0].text in laboli:
                        exit(52)
                    else:
                        laboli.append(instruction[0].text)
                    dir_labels[instruction[0].text] = instruction.attrib['order']
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text
        else:
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['MOVE', 'NOT', 'INT2CHAR', 'TYPE', 'STRLEN']:
        if (len(list(instruction)) == 2):
            if not (controlvar(instruction[0])) or not (controlsymb(instruction[1])):
                exit(32)
            else:
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text + ' ' + instruction[1].attrib['type'] + ' ' + instruction[1].text
        else:
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']:
        if (len(list(instruction)) == 3):
            if not (controlvar(instruction[0])) or not (controlsymb(instruction[1])) or not (controlsymb(instruction[2])):
                exit(32)
            else:
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text + ' ' + instruction[1].attrib['type'] + ' ' + instruction[1].text + ' ' + instruction[2].attrib['type'] + ' ' + instruction[2].text
        else:
            exit(32)
        # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] == 'READ':
        if (len(list(instruction)) == 2):
            if not (controlvar(instruction[0])) or not (controlType(instruction[1])):
                exit(32)
            else:
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text + ' ' + instruction[1].attrib['type'] + ' ' + instruction[1].text
        else:
            exit(32)
            # zaciname prepinat mezi instrukcemi, provadime syntaktickou analyzu a argumenty
    elif instruction.attrib['opcode'] in ['JUMPIFEQ', 'JUMPIFNEQ']:
        if (len(list(instruction)) == 3):
            
            if not controllabel(instruction[0]) or not controlsymb(instruction[1]) or not controlsymb(instruction[2]):
                exit(32)
            else:
                myList[instruction.attrib['order']] = instruction.attrib['opcode'] + ' ' + instruction[0].attrib['type'] + ' ' + instruction[0].text + ' ' + instruction[1].attrib['type'] + ' ' + instruction[1].text + ' ' + instruction[2].attrib['type'] + ' ' + instruction[2].text
                
        else:
            exit(32)
    else: # spatny opcode vede na chybku 32
        exit(32)
#definice pouzivanych ramcu, slovnicky
dir_var_GF = {}
dir_var_TF = {'Nedefinovano': True}
dir_var_LF = {'Nedefinovano': True}
#stack pro ulozeni TF ramcu na LF
type_stack = []
#promenna skakej
skakej = 0
#funkce na DEFVAR provadi definici promenne do slovniku 
def defvar(var1):
    if "GF" in var1:
        for key, item in dir_var_GF.items():
            if key == var1:
                exit(52)
        dir_var_GF[var1] = {'Value': None, 'Type' : None}
    if "TF" in var1:
        for key, item in dir_var_TF.items():
            if key == var1[3:]:
                exit(52)
        if (dir_var_TF['Nedefinovano']):
            exit(55)
        dir_var_TF[var1[3:]] = {'Value': None, 'Type' : None}
    if "LF" in var1:
        for key, item in dir_var_LF.items():
            if key == var1[3:]:
                exit(52)
        if (dir_var_LF['Nedefinovano']):
            exit(55)
        dir_var_LF[var1[3:]] = {'Value': None, 'Type' : None}
#funkce ktera nastavuje promennou hleda ve vsech slovnicich
def setvar(var1):
    try:
        if "GF" in var1:
            dir_var_GF[var1]['Value'] = stacek.pop()
            dir_var_GF[var1]['Type'] = type_stack.pop()
        if "TF" in var1:
            dir_var_TF[var1[3:]]['Value'] = stacek.pop()
            dir_var_TF[var1[3:]]['Type'] = type_stack.pop()
        if "LF" in var1:
            dir_var_LF[var1[3:]]['Value'] = stacek.pop()
            dir_var_LF[var1[3:]]['Type'] = type_stack.pop()
    except:
        if "TF" in var1:
            if dir_var_TF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_TF[var1[3:]]['Value']
            except:
                exit(54)
        if "LF" in var1:
            if dir_var_LF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_LF[var1[3:]]['Value']
            except:
                exit(54)
        if "GF" in var1:
            try:
                vysledek = dir_var_GF[var1]['Value']
            except:
                exit(54)
        exit(56)
#funkce ktera vraci hodnotu promenne
def getvar(var1):
    if "GF" in var1:
        try:
            odpoved = dir_var_GF[var1]['Value']
        except:
            exit(54)
        if dir_var_GF[var1]['Value'] is None:
            exit(56)
        return odpoved
    if "TF" in var1:
        if dir_var_TF['Nedefinovano']:
            exit(55)
        try:
            odpoved = dir_var_TF[var1[3:]]['Value'] 
        except:
            exit(54)
        if dir_var_TF[var1[3:]]['Value'] is None:
            exit(56)
        return odpoved
    if "LF" in var1:
        if dir_var_LF['Nedefinovano']:
            exit(55)
        try:
            odpoved = dir_var_LF[var1[3:]]['Value']
        except:
            exit(54)
        if dir_var_LF[var1[3:]]['Value'] is None:
            exit(56)
        return odpoved
#promenna abychom vedeli kde jsme v souboru prestali se ctenim
read = 0
#funkce gettype pro instrukci type ktera nam vrati type 
def gettype(var1, var2, var3):
    if "GF" in var2:
        typ = dir_var_GF[var2]['Type']
    if "TF" in var2:
        typ = dir_var_TF[var2[3:]]['Type'] 
    if "LF" in var2:
        typ = dir_var_LF[var2[3:]]['Type'] 
    if "string" in var3:
        typ = "string"
    if "int" in var3:
        typ = "int"
    if "bool" in var3:
        typ = "bool"
    if "nil" in var3:
        typ = "nil"
    if typ is None:
        stacek.append("")
        type_stack.append("")
    else:
        stacek.append(typ)
        type_stack.append("string")
    setvar(var1)
#funkce takova mensi matematicka knihovna provadi vetsinu instrukci
def mathisop(var1, var2, var3, operand):
    try: #prvne se provede samotne ulozeni hodnot do docasnych promennych
        vysledek = 0
        operand2 = var2
        operand3 = var3
        if "GF" in var2:
            operand2 = dir_var_GF[var2]['Value']
        if "TF" in var2:
            operand2 = dir_var_TF[var2[3:]]['Value'] 
        if "LF" in var2:
            operand2 =  dir_var_LF[var2[3:]]['Value']
        if "GF" in var3:
            operand3 = dir_var_GF[var3]['Value']
        if "TF" in var3:
            operand3 = dir_var_TF[var3[3:]]['Value'] 
        if "LF" in var3:
            operand3 =  dir_var_LF[var3[3:]]['Value']
        if operand == "+": #zde provadime scitani
            vysledek = int(operand2) + int (operand3)
            stacek.append(vysledek)
            type_stack.append("int")
            setvar(var1)
        if operand == "-": #zde zase odcitani
            vysledek = int(operand2) - int (operand3)
            stacek.append(vysledek)
            type_stack.append("int")
            setvar(var1)
        if operand == "*": #zde nasobime
            vysledek = int(operand2) * int (operand3)
            stacek.append(vysledek)
            type_stack.append("int")
            setvar(var1)
        if operand == "/": # a zde zase delime
            vysledek = int(operand2) // int (operand3)
            stacek.append(vysledek)
            type_stack.append("int")
            setvar(var1)
        if operand == ">": # tady se ptame, jestli je cislo na leve strane vetsi
            try:
                vysledek = int(operand2) > int (operand3)
            except:
                try:
                    operand2 = upravstring(operand2)
                    operand3 = upravstring(operand3)
                    vysledek = operand2 > operand3
                except:
                    exit(53)
            vysledek = str(vysledek).lower()
            stacek.append(vysledek)
            type_stack.append("bool")
            setvar(var1)
        if operand == "<": # a tady je to presne naopak
            try:
                vysledek = int(operand2) < int (operand3)
            except:
                try:
                    operand2 = upravstring(operand2)
                    operand3 = upravstring(operand3)
                    vysledek = operand2 < operand3
                except:
                    exit(53)
            vysledek = str(vysledek).lower()
            stacek.append(vysledek)
            type_stack.append("bool")
            setvar(var1)
        if operand == "==": # rovnaji se 2 cisla? 
            try:
                vysledek = int(operand2) == int (operand3)
            except:
                try:
                    operand2 = upravstring(operand2)
                    operand3 = upravstring(operand3)
                    vysledek = operand2 == operand3
                except:
                    exit(53)
            vysledek = str(vysledek).lower()
            stacek.append(vysledek)
            type_stack.append("bool")
            setvar(var1)
        if operand == "&&": # tady se provede logicky and
            if operand2 == "false":
                operand2 = False
            else:
                operand2 = True
            if operand3 == "false":
                operand3 = False
            else:
                operand3 = True
            vysledek = operand2 and operand3
            stacek.append(str(vysledek).lower())
            type_stack.append("bool")
            setvar(var1)
        if operand == "||": # a tady se provede logicky or
            if operand2 == "false":
                operand2 = False
            else:
                operand2 = True
            if operand3 == "false":
                operand3 = False
            else:
                operand3 = True
            vysledek = operand2 or operand3
            stacek.append(str(vysledek).lower())
            type_stack.append("bool")
            setvar(var1)
        if operand == "notor": # tady je not
            if operand2 == "true":
                vysledek = "false"
            elif operand2 == "false":
                vysledek = "true"
            stacek.append(vysledek)
            type_stack.append("bool")
            setvar(var1)
    except:
        if operand3 == "0" and operand == "/":
            exit(57)
        exit(53)
#funcke na zjisteni delky retezce
def zjistidelku(kamulozit, zkamazjistit):
    operand3 = zkamazjistit
    try:
        if "GF" in zkamazjistit:
            operand3 = dir_var_GF[zkamazjistit]['Value']
        if "TF" in zkamazjistit:
            operand3 = dir_var_TF[zkamazjistit[3:]]['Value'] 
        if "LF" in zkamazjistit:
            operand3 =  dir_var_LF[zkamazjistit[3:]]['Value']
    except:
        exit(55)
    if operand3 is None:
        exit(56)
    operand3 = upravstring(operand3)
    operand3 = len(operand3)
    stacek.append(operand3)
    type_stack.append("int")
    setvar(kamulozit)
#funkce na ziskani charakteru na urcite pozici
def getcharer(kamulozit, zkamazjistit, indexa, prevod):
    try:
        operand1 = indexa
        operand3 = zkamazjistit
        if "GF" in zkamazjistit:
            operand3 = dir_var_GF[zkamazjistit]['Value']
        if "TF" in zkamazjistit:
            operand3 = dir_var_TF[zkamazjistit[3:]]['Value'] 
        if "LF" in zkamazjistit:
            operand3 =  dir_var_LF[zkamazjistit[3:]]['Value']
        if "GF" in indexa:
            operand1 = dir_var_GF[indexa]['Value']
        if "TF" in indexa:
            operand1 = dir_var_TF[indexa[3:]]['Value'] 
        if "LF" in indexa:
            operand1 =  dir_var_LF[indexa[3:]]['Value']
        charecek = operand3[int(operand1)]
        if int(operand1) < 0:
            exit(58)
        if prevod:
            charecek = ord(charecek)
            type_stack.append("int")
        else:
            type_stack.append("string")
        stacek.append(charecek)
        setvar(kamulozit)
    except:
        exit(58)
#funkce ktera nastavi char na urcite pozici
def nastavchar(kamnastav, indexa, zkamazjistit):
    try:
        operand1 = indexa
        operand3 = zkamazjistit
        if "GF" in zkamazjistit:
            operand3 = dir_var_GF[zkamazjistit]['Value']
        if "TF" in zkamazjistit:
            operand3 = dir_var_TF[zkamazjistit[3:]]['Value'] 
        if "LF" in zkamazjistit:
            operand3 =  dir_var_LF[zkamazjistit[3:]]['Value']
        if "GF" in indexa:
            operand1 = dir_var_GF[indexa]['Value']
        if "TF" in indexa:
            operand1 = dir_var_TF[indexa[3:]]['Value'] 
        if "LF" in indexa:
            operand1 =  dir_var_LF[indexa[3:]]['Value']
        if "GF" in kamnastav:
            tady = dir_var_GF[kamnastav]['Value']
        if "TF" in kamnastav:
            tady = dir_var_TF[kamnastav[3:]]['Value']
        if "LF" in kamnastav:
            tady = dir_var_LF[kamnastav[3:]]['Value']
        operand3 = upravstring(operand3)
        tady = str(tady)
        tady = list(tady)
        if int(operand1) < 0:
            exit(58)
        tady[int(operand1)] = operand3[0]
        tady = ''.join(tady)
        stacek.append(tady)
        type_stack.append("string")
        setvar(kamnastav)
    except:
        exit(58)
#funkce ktera nam do prvniho argumentu spoji argument druhy atreti jedna se o retezce
def spojretezec(kamnastav, prvni, druhy):
    operand1 = prvni
    operand2 = druhy
    if "GF" in prvni:
        operand1 = dir_var_GF[prvni]['Value']
    if "TF" in prvni:
        operand1 = dir_var_TF[prvni[3:]]['Value'] 
    if "LF" in prvni:
        operand1 =  dir_var_LF[prvni[3:]]['Value']
    if "GF" in druhy:
        operand2 = dir_var_GF[druhy]['Value']
    if "TF" in druhy:
        operand2 = dir_var_TF[druhy[3:]]['Value'] 
    if "LF" in druhy:
        operand2 =  dir_var_LF[druhy[3:]]['Value']
    vysledek = operand1 + operand2
    stacek.append(vysledek)
    type_stack.append("string")
    setvar(kamnastav)
def vrattype(arg1, arg2):
    if "var" in arg1:
        if "GF" in arg2:
            return dir_var_GF[arg2]['Type']
        if "TF" in arg2:
            try:
                return dir_var_TF[arg2[3:]]['Type']
            except:
                exit(54)
        if "LF" in arg2:
            try:
                return dir_var_LF[arg2[3:]]['Type']
            except:
                exit(54)
    else:
        return arg1

#funcke ktera nastavuje prommenou MOVE
def nastav_promennou(kamnastav, conastav, jakytyp):
    operand2 = conastav
    if "GF" in conastav:
        operand2 = dir_var_GF[conastav]['Value']
    if "TF" in conastav:
        operand2 = dir_var_TF[conastav[3:]]['Value'] 
    if "LF" in conastav:
        operand2 = dir_var_LF[conastav[3:]]['Value']
    if operand2 == "nil":
        operand2 = ""
    stacek.append(operand2)
    if jakytyp == "var":
        jakytyp = vrattype(jakytyp, conastav)
    type_stack.append(jakytyp)
    setvar(kamnastav) 
#funkce rovna se pouziva se u JUMPIFEQ a JUMPIFNEQ
def rovnase(op1, op2):
    vysledek = 0
    operand1 = op1
    operand2 = op2
    if "GF" in op1:
        operand1 = dir_var_GF[op1]['Value']
    if "TF" in op1:
        operand1 = dir_var_TF[op1[3:]]['Value'] 
    if "LF" in op1:
        operand1 =  dir_var_LF[op1[3:]]['Value']
    if "GF" in op2:
        operand2 = dir_var_GF[op2]['Value']
    if "TF" in op2:
        operand2 = dir_var_TF[op2[3:]]['Value'] 
    if "LF" in op2:
        operand2 =  dir_var_LF[op2[3:]]['Value']
    try:
        if int(operand1) == int(operand2):
            return True
        return False
    except:
        try:
            operand1 = upravstring(operand1)
            operand2 = upravstring(operand2)
            if operand1 == operand2:
                return True
        except:
            exit(55)
novepolicko = []
iteracka=0
for vsechno in dvestejneorderinstrukce:
    novepolicko.append(int(vsechno))
novepolicko.sort()

def vratchybovykod(arg1, arg2, arg3, arg4, arg5):
    if arg1 == "var":
        if "GF" in arg2:
            try:
                vysledek = dir_var_GF[arg2]['Value']
            except:
                exit(54)
            if vysledek is None:
                exit(56)
        if "TF" in arg2:
            if dir_var_TF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_TF[arg2[3:]]['Value']
            except:
                exit(54)
            if vysledek is None:
                exit(56)
        if "LF" in arg2:
            if dir_var_LF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_LF[arg2[3:]]['Value']
            except:
                exit(54)
            if vysledek is None:
                exit(56)
    if arg3 == "var":
        if "GF" in arg4:
            try:
                vysledek = dir_var_GF[arg4]['Value']
            except:
                exit(54)
            if vysledek is None:
                if arg2 == "volameronalda":
                    return
                exit(56)
        if "TF" in arg4:
            if dir_var_TF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_TF[arg4[3:]]['Value']
            except:
                exit(54)
            if vysledek is None:
                if arg2 == "volameronalda":
                    return
                exit(56)
        if "LF" in arg4:
            if dir_var_LF['Nedefinovano']:
                exit(55)
            try:
                vysledek = dir_var_LF[arg4[3:]]['Value']
            except:
                exit(54)
            if vysledek is None:
                if arg2 == "volameronalda":
                    return
                exit(56)
    if arg5 is None:
        return
    if "GF" in arg5:
        try:
            vysledek = dir_var_GF[arg5]['Value']
        except:
            exit(54)
    if "TF" in arg5:
        if dir_var_TF['Nedefinovano']:
                exit(55)
        try:
            vysledek = dir_var_TF[arg5[3:]]['Value']
        except:
            exit(54)
    if "LF" in arg5:
        if dir_var_LF['Nedefinovano']:
            exit(55)
        try:
            vysledek = dir_var_LF[arg5[3:]]['Value']
        except:
            exit(54)
max_promennych = 0
skakavy_stack = [] #stack pro call a return
pocet_vykonanych = 0 # pocet vykokanych instrukci
try:
    i = int(novepolicko[0]) #iterator pres slovnicek
except:
    exit(0)
TFStack = [] # stack pro pushnute ramce

def rozsireni_funkce(exit_value):
    if rozsirenije:
        f = open(rozsirenifile, "w")
        for aladin in polacek:
            if aladin == "vars":
                f.write(str(max_promennych))
                f.write("\n")
            if aladin == "inst":
                f.write(str(pocet_vykonanych))
                f.write("\n")
        f.close()
    if exit_value != 0:
        exit(exit_value)
    else:
        exit(0)

while i <= int(novepolicko[len(novepolicko)-1]):
    try:
        item = myList[str(i)]
    except:
        i=i+1
        continue
    pocet_vykonanych = pocet_vykonanych +1
    napoli = item.split(' ')
    if (napoli[0] == 'DEFVAR'):
        defvar(napoli[2])
    elif (napoli[0] == 'POPS'):
        setvar(napoli[2])
    elif (napoli[0] == 'MOVE'):
        vratchybovykod("string", "string", napoli[3], napoli[4], napoli[2])
        nastav_promennou(napoli[2], napoli[4], napoli[3])
    elif (napoli[0] == 'CREATEFRAME'):
        dir_var_TF = {'Nedefinovano': False}
    elif (napoli[0] == 'PUSHFRAME'):
        if dir_var_TF['Nedefinovano']:
            exit(55)
        TFStack.append(dir_var_TF)
        dir_var_LF = TFStack[len(TFStack)-1]
        dir_var_TF = {'Nedefinovano': True}
        dir_var_LF['Nedefinovano']  = False
    elif (napoli[0] == 'POPFRAME'):
        if dir_var_LF['Nedefinovano']:
            exit(55)
        dir_var_TF = dir_var_LF
        try:
            TFStack.pop()
            dir_var_LF = TFStack[len(TFStack)-1]
        except:
            dir_var_LF = {'Nedefinovano': True}
    elif (napoli[0] == 'CALL'):
        skakavy_stack.append(i)
        try: 
            skakej = dir_labels[napoli[2]]
            i = int(skakej)
            pocet_vykonanych = pocet_vykonanych +1
        except:
            exit(52)
    elif (napoli[0] == 'RETURN'):
        try:
            skakej = skakavy_stack.pop()
            i = int(skakej)
        except:
            exit(56)
    elif (napoli[0] == 'PUSHS'):
        if napoli[1] == "var":
            stacek.append(getvar(napoli[2]))
            type_stack.append(vrattype(napoli[1], napoli[2]))
        else:
            stacek.append(napoli[2])
            type_stack.append(napoli[1])
    elif (napoli[0] == 'ADD'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "+")
    elif (napoli[0] == 'SUB'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "-")
    elif (napoli[0] == 'MUL'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "*")
    elif (napoli[0] == 'IDIV'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "/")
    elif (napoli[0] == 'LT'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != vrattype(napoli[5], napoli[6]):
            exit(53)
        if vrattype(napoli[3], napoli[4]) == "nil" or vrattype(napoli[5], napoli[6]) == "nil":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "<")
    elif (napoli[0] == 'GT'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != vrattype(napoli[5], napoli[6]):
            exit(53)
        if vrattype(napoli[3], napoli[4]) == "nil" or vrattype(napoli[5], napoli[6]) == "nil":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], ">")
    elif (napoli[0] == 'EQ'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != vrattype(napoli[5], napoli[6]):
            if vrattype(napoli[3], napoli[4]) != "nil" and vrattype(napoli[5], napoli[6]) != "nil":
                exit(53)
            if vrattype(napoli[3], napoli[4]) == "nil" or vrattype(napoli[5], napoli[6]) == "nil":
                type_stack.append("bool")
                stacek.append("false")
                setvar(napoli[2])
                i = i+1
                continue
        else:
            mathisop(napoli[2], napoli[4], napoli[6], "==")
    elif (napoli[0] == 'AND'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "bool":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "bool":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "&&")
    elif (napoli[0] == 'OR'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "bool":
            exit(53)
        if vrattype(napoli[5], napoli[6]) != "bool":
            exit(53)
        mathisop(napoli[2], napoli[4], napoli[6], "||")
    elif (napoli[0] == 'NOT'):
        vratchybovykod("string", "string", napoli[3], napoli[4], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "bool":
            exit(53)
        mathisop(napoli[2], napoli[4], "nic", "notor")
    elif (napoli[0] == 'INT2CHAR'):
        vratchybovykod("string", "string", napoli[3], napoli[4], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int":
            exit(53)
        try:
            if "GF" in napoli[2]:
                try:
                    dir_var_GF[napoli[2]]['Value'] = chr((int(getvar(napoli[4]))))
                except:
                    dir_var_GF[napoli[2]]['Value'] = chr((int(napoli[4])))
                dir_var_GF[napoli[2]]['Type'] = "string"
            if "TF" in napoli[2]:
                try:
                    dir_var_TF[napoli[2][3:]]['Value'] = chr((int(getvar(napoli[4]))))
                except:
                    dir_var_TF[napoli[2][3:]]['Value'] = chr((int(napoli[4])))
                dir_var_TF[napoli[2][3:]]['Type'] = "string"
            if "LF" in napoli[2]:
                try:
                    dir_var_LF[napoli[2][3:]]['Value'] = chr((int(getvar(napoli[4]))))
                except:
                    dir_var_LF[napoli[2][3:]]['Value'] = chr((int(napoli[4])))
        except:
            exit(58)
            dir_var_LF[napoli[2][3:]]['Type'] = "string"
    elif (napoli[0] == 'STRI2INT'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "string" or vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        getcharer(napoli[2], napoli[4], napoli[6], True)
    elif (napoli[0] == 'READ'):
        vratchybovykod("string", "string", "string", "string", napoli[2])
        try:
            if "GF" in napoli[2]:
                dir_var_GF[napoli[2]]['Value'] = input()
                dir_var_GF[napoli[2]]['Type'] = napoli[4]
                if napoli[4] == "int":
                    try:
                        int(dir_var_GF[napoli[2]]['Value'])
                    except:
                        dir_var_GF[napoli[2]]['Type'] = "nil"
                        dir_var_GF[napoli[2]]['Value'] = ""
                if napoli[4] == "bool":
                    if dir_var_GF[napoli[2]]['Value'].lower() == "true":
                        dir_var_GF[napoli[2]]['Value'] = "true"
                    else:
                        dir_var_GF[napoli[2]]['Value'] = "false"
            if "TF" in napoli[2]:
                dir_var_TF[napoli[2][3:]]['Value'] = input()
                dir_var_TF[napoli[2][3:]]['Type'] = napoli[4]
                if napoli[4] == "int":
                    try:
                        int(dir_var_TF[napoli[2][3:]]['Value'])
                    except:
                        dir_var_TF[napoli[2][3:]]['Type'] = "nil"
                        dir_var_TF[napoli[2][3:]]['Value'] = ""
                if napoli[4] == "bool":
                    if dir_var_TF[napoli[2][3:]]['Value'].lower() == "true":
                        dir_var_TF[napoli[2][3:]]['Value'] = "true"
                    else:
                        dir_var_TF[napoli[2][3:]]['Value'] = "false"
            if "LF" in napoli[2]:
                dir_var_LF[napoli[2][3:]]['Value'] = input()
                dir_var_LF[napoli[2][3:]]['Type'] = napoli[4]
                if napoli[4] == "int":
                    try:
                        int(dir_var_LF[napoli[2][3:]]['Value'])
                    except:
                        dir_var_LF[napoli[2][3:]]['Type'] = "nil"
                        dir_var_LF[napoli[2][3:]]['Value'] = ""
                if napoli[4] == "bool":
                    if dir_var_LF[napoli[2][3:]]['Value'].lower() == "true":
                        dir_var_LF[napoli[2][3:]]['Value'] = "true"
                    else:
                        dir_var_LF[napoli[2][3:]]['Value'] = "false"
            read = read+1
        except:
            if "GF" in napoli[2]:
                dir_var_GF[napoli[2]]['Value'] = ""
                dir_var_GF[napoli[2]]['Type'] = "nil"
            if "TF" in napoli[2]:
                dir_var_TF[napoli[2][3:]]['Value'] = ""
                dir_var_TF[napoli[2][3:]]['Type'] = "nil"
            if "LF" in napoli[2]:
                dir_var_LF[napoli[2][3:]]['Value'] = ""
                dir_var_LF[napoli[2][3:]]['Type'] = "nil"
    elif (napoli[0] == 'WRITE'):
        if (napoli[1] != "var"):
            if (napoli[2]) == "nil":
                napoli[2] = ""
            napoli[2] = upravstring(napoli[2])
            print(napoli[2], end='')
        else:
            stringtowr = str(getvar(napoli[2]))
            stringtowr = upravstring(stringtowr)
            print(stringtowr, end='')
    elif (napoli[0] == 'CONCAT'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "string" or vrattype(napoli[5], napoli[6]) != "string":
            exit(53)
        spojretezec(napoli[2], napoli[4], napoli[6])
    elif (napoli[0] == 'STRLEN'):
        vratchybovykod("string", "string", napoli[3], napoli[4], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "string":
            exit(53)
        zjistidelku(napoli[2], napoli[4])
    elif (napoli[0] == 'GETCHAR'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "string" or vrattype(napoli[5], napoli[6]) != "int":
            exit(53)
        getcharer(napoli[2], napoli[4], napoli[6], False)
    elif (napoli[0] == 'SETCHAR'):
        vratchybovykod(napoli[3], napoli[4], napoli[5], napoli[6], napoli[2])
        if vrattype(napoli[3], napoli[4]) != "int" or vrattype(napoli[5], napoli[6]) != "string":
            exit(53)
        if vrattype(napoli[1], napoli[2]) is None:
            exit(56)
        if vrattype(napoli[1], napoli[2]) != "string":
            exit(53)
        nastavchar(napoli[2], napoli[4], napoli[6])
    elif (napoli[0] == 'TYPE'):
        vratchybovykod("string", "volameronalda", napoli[3], napoli[4], napoli[2])
        gettype(napoli[2], napoli[4], napoli[3])
    elif (napoli[0] == 'LABEL'):
        i = i+1
        continue
    elif (napoli[0] == 'JUMP'):
        pocet_vykonanych = pocet_vykonanych +1
        try:
            skakej = dir_labels[napoli[2]]
            i = int(skakej)
        except:
            exit(52)
    elif (napoli[0] == 'JUMPIFEQ'):
        try:
            skakej = dir_labels[napoli[2]]
        except:
            exit(52)
        vratchybovykod(napoli[5], napoli[6], napoli[3], napoli[4], None)
        if vrattype(napoli[3], napoli[4]) != vrattype(napoli[5], napoli[6]):
            if vrattype(napoli[3], napoli[4]) != "nil" and vrattype(napoli[5], napoli[6]) != "nil":
                exit(53)
            if vrattype(napoli[3], napoli[4]) == "nil" or vrattype(napoli[5], napoli[6]) == "nil":
                i = i+1
                continue
        if rovnase(napoli[4], napoli[6]):
            try:
                skakej = dir_labels[napoli[2]]
                i = int(skakej)
                pocet_vykonanych = pocet_vykonanych +1
            except:
                exit(52)
    elif (napoli[0] == 'JUMPIFNEQ'):
        try:
            skakej = dir_labels[napoli[2]]
        except:
            exit(52)
        vratchybovykod(napoli[5], napoli[6], napoli[3], napoli[4], None)
        if vrattype(napoli[3], napoli[4]) != vrattype(napoli[5], napoli[6]):
            if vrattype(napoli[3], napoli[4]) != "nil" and vrattype(napoli[5], napoli[6]) != "nil":
                exit(53)
            if vrattype(napoli[3], napoli[4]) == "nil" or vrattype(napoli[5], napoli[6]) == "nil":
                try:
                    skakej = dir_labels[napoli[2]]
                    i = int(skakej)
                    pocet_vykonanych = pocet_vykonanych +1
                except:
                    exit(52)
        if not rovnase(napoli[4], napoli[6]):
            try:
                skakej = dir_labels[napoli[2]]
                i = int(skakej)
                pocet_vykonanych = pocet_vykonanych +1
            except:
                exit(52)
    elif (napoli[0] == 'EXIT'):
        vratchybovykod("string", "string", napoli[1], napoli[2], "string")
        if (napoli[1] != "int") and napoli[1] != "var":
            exit(53)
        if napoli[1] == "var":
            if vrattype(napoli[1], napoli[2]) != "int":
                exit(53)
            napoli[2] = getvar(napoli[2])
        if int(napoli[2]) < 0 or int(napoli[2]) > 49:
            exit(57)
        if rozsirenije:
            rozsireni_funkce(int(napoli[2]))
        exit(int(napoli[2]))
    elif (napoli[0] == 'DPRINT'):
        if (napoli[1] != "var"):
            napoli[2] = upravstring(napoli[2])
            print(napoli[2], file=sys.stderr, end='')
        else:
            stringtowr = str(getvar(napoli[2]))
            stringtowr = upravstring(stringtowr)
            print(stringtowr, file=sys.stderr, end='')
    elif (napoli[0] == 'BREAK'):
        print("", file=sys.stderr)
        print("_________________", file=sys.stderr)
        print("INSTRUKCE BREAK", file=sys.stderr)
        print(myList[str(i)], file=sys.stderr)
        print("Obsah globalniho ramce:", end='', file=sys.stderr)
        print(dir_var_GF, file=sys.stderr)
        print("Obsah zasobnikoveho ramce:", end='', file=sys.stderr)
        print(dir_var_LF, file=sys.stderr)
        print("Obsah docasneho ramce:", end='', file=sys.stderr)
        print(dir_var_TF, file=sys.stderr)
        print("pocet vykonanich instrukci: ", end='', file=sys.stderr)
        print(pocet_vykonanych, file=sys.stderr)
        print("KONEC INSTRUKCE BREAK", file=sys.stderr)
        print("__________________", file=sys.stderr)
    i = i+1
    pocet_vars = 0
    for key, hodnota in dir_var_GF.items():
        if dir_var_GF[key]['Value'] is not None:
            pocet_vars = pocet_vars +1
    for key, hodnota in dir_var_TF.items():
        if key != "Nedefinovano":
            if dir_var_TF[key]['Value'] is not None:
                pocet_vars = pocet_vars +1
    for key, hodnota in dir_var_LF.items():
        if key != "Nedefinovano":
            if dir_var_LF[key]['Value'] is not None:
                pocet_vars = pocet_vars +1
    if pocet_vars > max_promennych:
        max_promennych = pocet_vars

if rozsirenije:
    rozsireni_funkce(0)

