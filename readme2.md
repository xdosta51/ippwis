## Implementační dokumentace k 2. úloze do IPP 2019/2020
### Jméno a příjmení: Michal Dostál
### Login: xdosta51

### Spuštění skriptů

#### interpret.py
Program se spouští pomocí příkazu *python3.8 interpret.py*, kde na **STDIN** očekává buď *XML reprezentaci* jazyka *IPPCode20*, nebo data potřebná pro instrukci *read*.
Skript dále podporuje argumenty *--source=file*, kde file je soubor s XML reprezentací již zmiňovaného kódu IPPCode20, *--input=file*,
kde soubor file jsou potřebná data pro instrukci *read*, pokud jsou potřeba. Dale podporuje přepínač *--help*, ktery se nesmí dále kombinovat s ostatními argumenty,
jinak se jedna o chybu 10. Jelikož tento skript podporuje rozšíření **STATI**, tak je možné zadat argument *--stats=file*, kde file je jméno souboru,
kam se budou statistiky interpretu vypisovat. Tento argument je libovolně kombinovatelný s argumenty *--vars* pro výpis maximálního počtu inicializovaných proměnných
ve všech platných rámcích, a taky argument *--insts* pro výpis počtu vykonaných instrukcí. Pokud jsou zadany argumenty *--vars*, nebo *--insts* 
bez argumentu *--stats=file*, program končí s chybou 10, v opačném případě skript vytvoří prázdný soubor.

#### test.php
Skript *test.php* se spouští pomocí příkazu *php7.4 test.php* s jeho volitelnými argumenty *--directory=folder*, kde folder je složka s testy, které máme procházet.
Dále skript podporuje argument *--recursive*, tímto přepínačem se spustí prohledávání nejen v zadané složce, ale i rekurzivně ve všech jeho podadresářích. Bez 
přepínačů *--int-only* a *--parse-only* testovací rámec pracuje v režimu *both*, kdy první spustí *parse.php* a na jeho vstup pošle program napsaný v jazyce *IPPCode20*, 
výstup bude poté přesměrován do interpretu a pokud oba proběhly bez chyby, provádí se **diff** nad očekávaným vstupem a výstupem z testovaného interpretu. Pokud je 
zadán přepínač *--int-only*, tak se testuje pouze interpret a jako **.src** soubor bude *XML reprezentace* IPPCode20. S přepínačem *--parse-only* se testuje pouze
program *parse.php*.

### Skript: interpret.py
Skript **interpret.py** napsaný v jazyce *python3.8* provádí interpretaci *XML reprezentace* jazyka *IPPCode20*. Tento skript není napsaný objektově orientovaně a
skládá se pouze z jednoho souboru *interpret.py*, po načtení *XML reprezentace* se provádí kontrola správnosti XML souboru, pokud tento soubor není dobře formátovaný,
tak program končí s chybou 31. Hned poté se provádí syntaktická analýza, kde se kontroluje, jak správný počet argumentů k jednotlivým operačním kódům, ale taky správnost
zápisu jednotlivých argumentů. Také se kontroluje, zda jednotlivé argumenty vůbec k operačním kódum odpovídají. V této části se také kontroluje unikátnost návěští, unikátnost pořadí instrukce, a taky správnost pořadí instrukce. Postupně se skládá slovnik, který se naplni daty instrukce a klíčem je pořadí instrukce, které je 
obsaženo v *XML souboru*. Poté, co jsou slovníky naplněny a syntaktická analýza proběhla v pořádku, se inicializují rámce pro globální, dočasné a zásobníkové proměnné.
Pokud všechno proběhlo v pořádku, tak se provádí již samotná interpretace, která může v průběhu programu skončit se sémantickou chybou a podle toho odpovídajícím
exit kódem. Pokud vše proběhlo v pořádku, interpretace se povedla a program doběhl do konce, program končí s kódem 0.

### Testovací rámec: test.php
Skript *test.php* po správném spuštění hledá v zadaném, pokud je, nebo aktuálním adresáři, pomocí příkazu **exec(find)**, může hledat rekurzivně, nebo nemusí,
podle toho se nastavuje flag *max_depth*, který říká do jaké hloubky ma příkaz *find* hledat. 
Tento program může běžet ve 3 režimech:
 - Režim: both, nesmí byt zadány argumenty --int-only a --parse-only
 - Režim: parse-only, pokud byl zadán argument --parse-only
 - Režim: int-only, pokud byl zadán argument --int-only

Podle těchto 3 režimů se skript řídí a testuje jednotlivé aplikace. v režimu both se nejprve provede překlad programu IPPCode20 pomocí skriptu parse.php a jeho
výstup se poté pošle do skriptu interpret.py. V režimu parse-only se provádí pouze testování aplikace parse.php, k porovnání výstupu ovšem nelze použít program 
diff a proto je nutné použít aplikaci jexamxml, ktera se spouští příkazem *--java -jar*. Poslední režim testuje program interpret.py a v *.src* souborech očekává
již přeloženou *XML Reprezentaci*. Skript může končit s chybou 10, 11, 12, pokud došlo k problému se souborovým systémem, nebo s chybovým kódem 0. Přehlednou 
stránku v HTML5, kde jsou obsaženy jednotlivé adresáře a v tom příslušné testy, které prošly, nebo které selhaly vypíše na **STDOUT**.

### Rozšíření
V druhém projektu se mi podařilo implementovat rozšíření **STATI**, které je implementováno v části *interpret.py*. Toto rozšíření počítá maximální počet inicializovaných proměnných a počet vykonaných instrukcí. Počítadlo pro proměnné jsem implementoval tak, že při každé vykonané instrukce si do globalní proměnné 
přičtu jedničku. Počítadlo pro proměnné už bylo horší a je implementováno tak, že při každém vykonání instrukce se spočítají proměnné ve všech platných rámcích, 
provede se porovnání s globální proměnnou, která si pamatuje poslední maximální počet a pokud je nový počet větší, globální proměnná se přepíše. Důležité bylo ošetřit
toto rozšíření u funkce EXIT, kdy je potřeba jednak skončit s potřebným chybovým kodem, ale taky nezapomenout před samotným ukončením vypsat do souboru potřebná data.