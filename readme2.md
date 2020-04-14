## Implementační dokumentace k 2. úloze do IPP 2019/2020
### Jméno a příjmení: Michal Dostal
### Login: xdosta51

### Spusteni skriptu

#### interpret.py
Program se spousti pomoci prikazu *python3.8 interpret.py*, kde na **STDIN** ceka bud *XML reprezentaci* jazyka *IPPCode20*, nebo data potrebna pro instrukci *read*.
Skript dale podporuje argumenty *--source=file*, kde file je soubor s XML reprezentaci jiz zminovaneho kodu IPPCode20, *--input=file*,
kde soubor file jsou potrebna data pro instrukci *read*, pokud jsou potreba. Dale podporuje prepinac *--help*, ktery se nesmi dale kombinovat s ostatnimi argumenty,
jinak se jedna o chybu 10. Jelikoz tento skript podporuje rozsireni **STATI**, tak je mozne zadat argument *--stats=file*, kde file je jmeno souboru,
kam se budou statistiky interpretu vypisovat. Tento argument je libovolne kombinovatelny s argumenty *--vars* pro vypis maximalniho poctu inicializovanych promennych
ve vsech platnych ramcich, a taky argument *--insts* pro vypis poctu vykonanych instrukci. Pokud jsou zadany argumenty *--vars*, nebo *--insts* 
bez argumentu *--stats=file*, program konci s chybou 10, v opacnem pripade skript vytvori prazdny soubor.

#### test.php
Skript *test.php* se spousti pomoci prikazu *php7.4 test.php* s jeho volitelnymi argumenty *--directory=folder*, kde folder je slozka s testy, ktere mame prochazet.
Dale skript podporuje argument *--recursive*, timto prepinacem se spusti prohledavani nejen v zadane slozce, ale i rekurzivne ve vsech jeho podadresarich. Bez 
prepinacu *--int-only* a *--parse-only* testovaci ramec pracuje v rezimu both, kdy prvni spusti *parse.php* a na jeho vstup posle program napsany v jazyce *IPPCode20*, 
vystup bude pote presmerovan do interpretu a pokud oba probehly bez chyby, provadi se **diff** nad ocekevanym vstupem a vystupem z testovaneho interpretu. Pokud je 
zadan prepinac *--int-only*, tak se testuje pouze interpret a jako **.src** soubor bude *XML reprezentace* IPPCode20. S prepinacem *--parse-only* se testuje pouze
program *parse.php*.

### interpret.py
Skript **interpret.py** napsany v jazyce *python3.8* provadi interpretaci *XML reprezentace* jazyka *IPPCode20*. Tento skript neni napsany objektove orientovane a
sklada se pouze z jednoho souboru *interpret.py*, po nacteni *XML reprezentace* se provadi kontrola spravnosti XML souboru, pokud tento soubor neni dobre formatovany,
tak program konci s chybou 31. Hned pote se provadi syntakticka analyza, kde se kontroluje, jak spravny pocet argumentu k jednotlivym operacnim kodum, ale taky spravnost
zapisu jednotlivych argumentu. Take se kontroluje, zda jednotlive argumenty vubec k operacnim kodum odpovidaji. V teto casti se take kontroluje unikatnost navesti, unikatnost poradi instrukce, a taky spravnost poradi instrukce. Postupne se sklada slovnik, ktery se naplni daty instrukce a klicem je poradi instrukce, ktere je 
obsazeno v *XML souboru*. Pote, co jsou slovniky naplneny a syntakticka analyza probehla v poradku, se inicializuji ramce pro globalni, docasne a zasobnikove promenne.
Pokud vsechno probehlo v poradku, tak se provadi jiz samotna interpretace, ktera muze v prubehu programu skoncit se semantickou chybou a podle toho odpovidajicim
exit kodem. Pokud vse probehlo v poradku a interpretace se povedla a program dobehl do konce, program konci s chybovym kodem 0.

### test.php
Skript *test.php* po spravnem spusteni hleda v zadanem, pokud je, nebo aktualnim adresari, pomoci prikazu **exec(find)**, muze hledat rekurzivne, nebo nemusi,
podle toho se nastavuje flag *max_depth*, ktery rika do jake hloubky ma prikaz *find* hledat. 
Tento program muze bezet ve 3 rezimech:
 - Rezim: Both, nesmi byt zadany argumenty --int-only a --parse-only
 - Rezim: parse-only, pokud byl zadan argument --parse-only
 - Rezim: int-only, pokud byl zadan argument --int-only
 
Podle techto 3 rezimu se skript ridi a testuje jednotlive aplikace. v rezimu Both se nejprve provede preklad program IPPCode20 pomoci programu parse.php a jeho
vystup se pote posle do skripu interpret.py. V rezimu parse-only se provadi pouze testovani aplikace parse.php, k porovnani vystupu ovsem nelze pouzit program 
diff a proto je nutne pouzit aplikaci jexamxml, ktera se spousti prikazem *--java -jar*. Posledni rezim testuje program interpret.py a v *.src* souborech ocekava
jiz prelozenou *XML Reprezentaci*. Skript muze koncit s chybou 10, 11, 12, pokud doslo k problemu se souborovym systemem, nebo s chybovym kodem 0 a prehlednou 
stranku v HTML5, kde jsou obsazeny vsechny testy a znazorneny jednotlive adresare a jmena testu, ktere prosly, nebo selhaly vypise na **STDOUT**