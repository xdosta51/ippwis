<?php 

    declare(strict_types = 1);
    // hlavicka xml output
    $start = new DOMDocument('1.0', 'UTF-8');
    $start->formatOutput = true;
    $xmlStart = $start->createElement("program");
    $xmlStart->setAttribute("language", "IPPcode20");
    $xmlStart = $start->appendChild($xmlStart);
    // glob. promenne pro rozsireni
    $rozsirenije = false;
    $navesti = 0;
    $instrukce = 0;
    $skoky = 0;
    $komentosy = 0;
    $labels[0] = "";
    // kontrola argumentu
    if($argc > 1)
    {
        if ($argv[1] == '--help')
        {
            if ($argc > 2) {
                exit(10);
            }
            fwrite(STDOUT, "Skript typu filtr (parse.php v jazyce PHP 7.4)\nnacte ze standardniho vstupu zdrojovy kod v IPP-\ncode20 (viz sekce 6), zkontroluje lexikalni\na syntaktickou spravnost kodu a vypise na standardni\nvystup XML reprezentaci programu dle specifikace v sekci\n");
            exit(0);
        }
        else if (preg_match("/--stats=/", $argv[1])) {
            $filee = substr($argv[1], 8);
            $myfile = fopen($filee, "w") or die("Unable to open file!");
            $rozsirenije = true;
        }
        else 
        {
            for ($x = 0; $x < count($argv); $x++) {
                if (preg_match("/--stats=/", $argv[$x])) {
                    $filee = substr($argv[$x], 8);
                    $myfile = fopen($filee, "w") or die("Unable to open file!");
                    $rozsirenije = true;
                    break;
                }
            }
            if (!$rozsirenije) {
            fwrite(STDERR, "spatne argumenty\n");
            exit(10);
            }
        }
    }
    // parse potrebny pro vypis rozsireni na konci
    $extensions[0] = '';
    if ($rozsirenije) {
        $indexator = 0;
        foreach ($argv as $arg) {
            if ($arg == "parse.php")
                continue;
            else if($arg == "--loc")
                $extensions[$indexator] = "loc";
            else if($arg == "--labels")
                $extensions[$indexator] = "labels";
            else if($arg == "--comments")
                $extensions[$indexator] = "comments";
            else if($arg == "--jumps")
                $extensions[$indexator] = "jumps";
            else if (preg_match("/--stats=/", $arg))
                continue;
            else 
                exit(10);   
            $indexator++;
        }
    }
    // potrebna cast pro spocitani komentaru v programu
    $rozsireni = trim(stream_get_contents(STDIN));
    $rozsireni2 = explode("\n", $rozsireni);

    for ($pruchod = 0; $pruchod < count($rozsireni2); $pruchod++) {
        if (preg_match('/#.*/', $rozsireni2[$pruchod])) 
            $komentosy++;
    }
    // zde nahradim komentare za nic
    $input = preg_replace('/#.*/', '', $rozsireni);
    // pokud je soubor prazdny chyba
    if (!$input) {
        fprintf(STDERR, "Chybi hlavicka\n");
        exit(21);
    }
    // nahrazeni tabulatoru mezer newlinu
    $input = preg_replace('/[ \t]/', ' ', $input);
    $input = preg_replace('/\n/', "\n", $input);
    $input = explode("\n", preg_replace('/  */', ' ', $input));
    // pruchod odstraneni prebytenych mezer na zacatku atd
    for ($i = 0; $i < count($input); $i++) {
        $input[$i] = trim($input[$i]);
        $input[$i] = preg_replace('/^ /', '', $input[$i]);
    }
    // rozdeleni na tokeny podle mezery
    for ($i = 0; $i < count($input); $i++) {
        $input[$i] = explode(" ", $input[$i]);
    }
    // potrebne pro kontrolu hlavicky
    $zacatek = 0;

    for ($i=0; $i < count($input); $i++) {
        if (!$input[$i][0]) {
            $zacatek++;
        }
        else if ($input[$i][0])
            break;
    }
    $input[$zacatek][0] = strtoupper($input[$zacatek][0]);
    if ($input[$zacatek][0] != ".IPPCODE20")
    {
        exit(21);
    }
    // zde se kontroluje syntaxe varu
    function controlvar($var1) {
        if (preg_match("/^(LF|TF|GF)@[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$/", $var1))
            return true;
        else 
            return false;
    }
    //tato funnkce kontroluj syntax konstanty
    function controlsymb($var1) {
        if(preg_match('/^int|bool|string|nil/', $var1))
        {
            if(preg_match('/^int@[+|-]?\d+$/', $var1))
                return "int";
            if(preg_match('/^bool@(true|false)$/', $var1))
                return "bool";
            if(preg_match('/^nil@nil$/', $var1))
                return "nil";
            if(preg_match('~^string@~', $var1))
                return "string";
            else 
                return false;
        }
        else if (preg_match("/^(LF|TF|GF)@[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$/", $var1))
            return "var";
        else 
            return false;
    }
    // tato funkce kontroluje syntaxy navesti
    function controllabel($var1) {
        if (preg_match("~^[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$~", $var1))
            return true;
        else 
            return false;
    }
    // kontrola syntaxe type
    function controltype($var1) {
        if(preg_match('/^int|bool|string|nil/', $var1))
            return true; 
        else 
            return false;
    }
    // funkce ktera mi vrati to co je potrebne pro vypis do xml
    function getint($var1){
        
        if(preg_match('/^int@[+|-]?\d+$/', $var1))
            $match = substr($var1, 4);
        else if(preg_match('/^bool@(true|false)$/', $var1)) 
            $match = substr($var1, 5);
        else if(preg_match('/^nil@nil$/', $var1))
            $match = 'nil';
        else if(preg_match('~^string@~', $var1))
            $match = substr($var1, 7);
        else if (preg_match("/^(LF|TF|GF)@[a-zA-Z_\-$&%*?!][a-zA-Z0-9_\-$&%*?!]*$/", $var1))
            $match = $var1;
        else 
            return false;
        return htmlspecialchars($match);
    }
    // promenna pro kontrolu hlavicky
    $jednahlavicka = 0;
    // promenna pro pocitani poradi instrukce
    $order = 1;
    // pruchod po radcich kontrola syntaxe 
    for ($i=0; $i < count($input); $i++) {
        
        $input[$i][0] = strtoupper($input[$i][0]);

        if (!$input[$i][0])
            continue;

        $instrukce++;

        if ($input[$i][0] == "CREATEFRAME" || $input[$i][0] == "PUSHFRAME" || $input[$i][0] == "POPFRAME" 
        || $input[$i][0] == "RETURN" || $input[$i][0] == "BREAK") {
            if (count($input[$i]) != 1) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            if ($input[$i][0] == "RETURN")
                $skoky++;
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $xmlStart->appendChild($instruction);  
            $order++;
        }
        else if ($input[$i][0] == "JUMP" || $input[$i][0] == "LABEL" || $input[$i][0] == "CALL") {
            if ((count($input[$i]) != 2) || !(controllabel($input[$i][1]))) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            if ($input[$i][0] == "LABEL") { 
                $pricti = true;
                for ($x = 0; $x < count($labels); $x++){
                    if ($input[$i][1] == $labels[$x])
                        $pricti = false;
                }
                if ($pricti) {
                    $labels[count($labels)] = $input[$i][1];
                    $navesti++;
                }
            }
            else 
                $skoky++;

            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "label");
            $instruction->appendChild($args1);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "DEFVAR" || $input[$i][0] == "POPS") {
            if ((count($input[$i]) != 2) || !(controlvar($input[$i][1]))) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "var");
            $instruction->appendChild($args1);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "PUSHS" || $input[$i][0] == "WRITE" 
        || $input[$i][0] == "DPRINT" || $input[$i][0] == "EXIT") {
            if ((count($input[$i]) != 2) || !(controlsymb($input[$i][1]))) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", getint($input[$i][1]));
            $args1->setAttribute("type", controlsymb($input[$i][1]));
            $instruction->appendChild($args1);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "MOVE" || $input[$i][0] == "INT2CHAR" || $input[$i][0] == "STRLEN" 
        || $input[$i][0] == "TYPE" || $input[$i][0] == "NOT") {
            if ((count($input[$i]) != 3) || !(controlvar($input[$i][1])) || !(controlsymb($input[$i][2])))  {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "var");
            $args2 = $start->createElement("arg2", getint($input[$i][2]));
            $args2->setAttribute("type", controlsymb($input[$i][2]));
            $instruction->appendChild($args1);
            $instruction->appendChild($args2);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "READ") {
            if ((count($input[$i]) != 3) || !(controlvar($input[$i][1])) || !(controltype($input[$i][2])))  {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "var");
            $args2 = $start->createElement("arg2", $input[$i][2]);
            $args2->setAttribute("type", "type");
            $instruction->appendChild($args1);
            $instruction->appendChild($args2);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "JUMPIFNEQ" || $input[$i][0] == "JUMPIFEQ") {
            if ((count($input[$i]) != 4) || !(controllabel($input[$i][1])) || !(controlsymb($input[$i][2])) || !(controlsymb($input[$i][3]))) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $skoky++;
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "label");
            $args2 = $start->createElement("arg2", getint($input[$i][2]));
            $args2->setAttribute("type", controlsymb($input[$i][2]));
            $args3 = $start->createElement("arg3", getint($input[$i][3]));
            $args3->setAttribute("type", controlsymb($input[$i][3]));
            $instruction->appendChild($args1);
            $instruction->appendChild($args2);
            $instruction->appendChild($args3);
            $xmlStart->appendChild($instruction);   
            $order++;
        }

        else if ($input[$i][0] == "ADD" || $input[$i][0] == "SUB" || $input[$i][0] == "MUL" || $input[$i][0] == "IDIV" || $input[$i][0] == "LT"
        || $input[$i][0] == "GT" || $input[$i][0] == "EQ" || $input[$i][0] == "AND" || $input[$i][0] == "OR" || $input[$i][0] == "STRI2INT" || $input[$i][0] == "CONCAT"
        || $input[$i][0] == "GETCHAR" || $input[$i][0] == "SETCHAR") {
            if ((count($input[$i]) != 4) || !(controlvar($input[$i][1])) || !(controlsymb($input[$i][2])) || !(controlsymb($input[$i][3]))) {
                fprintf(STDERR, "jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode20.\n");
                exit(23);
            }
            $instruction = $start->createElement("instruction");
            $instruction->setAttribute("order", "$order");
            $instruction->setAttribute("opcode", $input[$i][0]);
            $args1 = $start->createElement("arg1", htmlspecialchars($input[$i][1]));
            $args1->setAttribute("type", "var");
            $args2 = $start->createElement("arg2", getint($input[$i][2]));
            $args2->setAttribute("type", controlsymb($input[$i][2]));
            $args3 = $start->createElement("arg3", getint($input[$i][3]));
            $args3->setAttribute("type", controlsymb($input[$i][3]));
            $instruction->appendChild($args1);
            $instruction->appendChild($args2);
            $instruction->appendChild($args3);
            $xmlStart->appendChild($instruction);   
            $order++;
        }
        // kontrola jedne hlavicky
        else if($input[$i][0] == ".IPPCODE20" && !$jednahlavicka) {
            $instrukce--;
            $jednahlavicka = 1;
            continue;
        }
        // instrukce ktera neni podporovana
        else {
            fprintf(STDERR, "neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode20\n");
                exit(22);
        }
    }
    echo $start->saveXML();
    // zde se provede vypis do souboru pokud bylo rozsireni
    foreach ($extensions as $prvek) {
        if ($prvek == "labels"){
            fwrite($myfile, strval($navesti));
            fwrite($myfile, "\n");}
        else if ($prvek == "loc"){
            fwrite($myfile, strval($instrukce));
            fwrite($myfile, "\n");}
        else if ($prvek == "comments"){
            fwrite($myfile, strval($komentosy));
            fwrite($myfile, "\n");}
        else if ($prvek == "jumps"){
            fwrite($myfile, strval($skoky));
            fwrite($myfile, "\n");}
    }
?>
