## Implementační dokumentace k 2. úloze do IPP 2019/2020
### Jméno a příjmení: Michal Dostál
### Login: xdosta51

### Skript: interpret.py
Skript **interpret.py** napsaný v jazyce *python3.8* provádí interpretaci *XML reprezentace* jazyka *IPPCode20*. Tento skript není napsaný objektově orientovaně a
skládá se pouze z jednoho souboru *interpret.py*, po načtení *XML reprezentace* se provádí kontrola správnosti XML souboru, pokud tento soubor není dobře formátovaný,
program končí s chybou 31. Hned poté se provádí syntaktická analýza, kde se kontroluje, jak správný počet argumentů k jednotlivým operačním kódům, ale taky správnost
zápisu jednotlivých argumentů. Také se kontroluje, zda jednotlivé argumenty vůbec k operačním kódum odpovídají. V další části se kontroluje unikátnost návěští, unikátnost pořadí instrukce, a taky správnost pořadí instrukce. Postupně se skládá slovnik, který se naplni daty instrukce a klíčem je pořadí instrukce, které je 
obsaženo v *XML souboru*. Poté, co jsou slovníky naplněny a syntaktická analýza proběhla v pořádku, se inicializují rámce pro globální, dočasné a zásobníkové proměnné.
Pokud všechno proběhlo v pořádku, tak se provádí již samotná interpretace, která může v průběhu programu skončit se sémantickou chybou a podle toho odpovídajícím
chybovým kódem. Pokud vše proběhlo v pořádku, interpretace se povedla a program doběhl do konce, program končí s kódem 0.

### Testovací rámec: test.php
Skript *test.php* po správném spuštění hledá v zadaném, pokud je, nebo aktuálním adresáři, pomocí příkazu **exec(find)**, může hledat rekurzivně, nebo nemusí,
podle toho se nastavuje flag *max_depth*, který říká do jaké hloubky má příkaz *find* hledat. 
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
V druhém projektu se mi podařilo implementovat rozšíření **STATI**, které je implementováno v části *interpret.py*. Toto rozšíření počítá maximální počet inicializovaných proměnných a počet vykonaných instrukcí. Počítadlo pro instrukce je implementováno tak, že při každé vykonané instrukci si do globalní proměnné 
přičtu jedničku. Počítadlo pro proměnné už bylo složitější a je implementováno tak, že při každém vykonání instrukce se spočítají proměnné ve všech platných rámcích, 
provede se porovnání s globální proměnnou, která si pamatuje poslední maximální počet a pokud je nový počet větší, globální proměnná se přepíše. Důležité bylo ošetřit
toto rozšíření u funkce EXIT, kdy je potřeba jednak skončit s potřebným chybovým kodem, ale taky nezapomenout před samotným ukončením vypsat do souboru potřebná data.
