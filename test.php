<?php
    #Autor: Michal Dostal, xdosta51
    declare(strict_types = 1);
    #Globalni promenne pro pozdejsi pouziti
    $directory = ""; #promenna pro slozku directory
    $recursive = False; #nastaveni rekurzivniho pruchodu
    $parse_file = "./parse.php"; #soubor s parsrem
    $int_file = "./interpret.py"; #soubor s interpretrem
    $parse_only = False; #parse only moud
    $int_only = False; #int only moud
    $jexam_xml = "/pub/courses/ipp/jexamxml/jexamxml.jar"; #cesta k jexam souboru
    $passed = 0; #kolik proslo
    $failed = 0; #kolik failnulo
    #kontrola argumentu
    if($argc > 1)
    { #vic nez jeden argumentu
        foreach ($argv as $argum) { #pruchod polem pres argumenty
            if ($argum == "--help") {
                if ($argc > 2) #kontrola zda je jenom jeden argument --help
                    exit(10);
                echo "vypis napovedu \n"; #zde se vypise napoveda
            }
            else if (preg_match("/--directory=/", $argum)) { #parse slozky
                $directory = substr($argum, 12);
                if (!$directory) { #pokud chybi chyba 10
                    exit(10);
                }
                if (!is_dir($directory)) #kontrola zda existuje vubec
                    exit(11);
            }
            else if ($argum == "--recursive") {
                $recursive = True; # pokud ma byt prochazeno rekurzivne
            }
            else if (preg_match("/--parse-script=/", $argum)) {
                $parse_file = substr($argum, 15);
                if (!$parse_file) {
                    exit(10);
                }
                if ($int_only) {
                    exit(10); ##parse script nesmi byt dohromady s intonly
                }
            }
            else if (preg_match("/--int-script=/", $argum)) {
                $int_file = substr($argum, 13);
                if (!$int_file) {
                    exit(10);
                }
                if ($parse_only) { # int script nesmi byt zadan s parse only
                    exit(10);
                }
            }
            else if ($argum == "--parse-only") {
                $parse_only = True;
                if ($int_only || $int_file != "./interpret.py") {
                    exit(10);
                } # k parse only nesmi byt nic s int
            }
            else if ($argum == "--int-only") {
                $int_only = True;
                if ($parse_only || $parse_file != "./parse.php") {
                    exit(10);
                } # k int only nesmi byt nic s parse only
            }
            else if (preg_match("/--jexamxml=/", $argum)) {
                $jexam_xml = substr($argum, 11);
                if (!$jexam_xml) {
                    exit(10);
                }
            } ## soubor pro jexamxml
            else if (preg_match("/test.php/", $argum)) {
                continue;
            }
            else {
                exit(10); ## jiny argument vede na chybku 10
            }
        }
    }

    else { # malo argumentu taky cbytba 10
        exit(10);
    }

    if ($parse_only) {
        $indexace = 1; #indexovani jednotlivich testu a HTML
        echo "<!DOCTYPE HTML>";
	    echo "<html lang=\"cs\">" . "\n";
	    echo "<head>" . "\n";
	    echo "<meta charset=\"utf-8\">" . "\n";
	    echo "<meta name=\"viewport\" content=\"width=1920, initial-scale=1.0\">" . "\n";
        echo "<title>IPP project</title>" . "\n";
        echo "<style>" . "\n";
        echo "html {" . "\n";
        echo "background-color: #F0F8FF;" . "\n";
        echo "text-align: center;" . "\n";
        echo "}" . "\n";
        echo "body {" . "\n";
        echo "text-align: center;" . "\n";
        echo "}" . "\n";
        echo "table {" . "\n";
        echo "font-family: arial, sans-serif;" . "\n";
        echo "border-collapse: collapse;" . "\n";
        echo "width: 70%;" . "\n";
        echo "}" . "\n";
        echo "td, th {" . "\n";
        echo "border: 1px solid #dddddd;" . "\n";
        echo "text-align: left;" . "\n";
        echo "padding: 8px;" . "\n";
        echo "}" . "\n";
        echo "tr:nth-child(even) {" . "\n";
        echo "background-color: #87CEFA;" . "\n";
        echo "}" . "\n";
        echo "</style>" . "\n";
        echo "</head>" . "\n";
        echo "<body>" . "\n";
        echo "<h1> IPP Project_2: test.php</h1>" . "\n";
        echo "<h2> MODE: Parse Only </h2>" . "\n";
        echo "<table style=\"margin: 0 auto;\">" . "\n";
        echo "<tr>" . "\n";
        echo "<th> Test. No. : </th>" . "\n";
        echo "<th> Directory </th>" . "\n";
        echo "<th> Test </th>" . "\n";
        echo "<th> ERROR Code OK or NOK </th>" . "\n";
        echo "<th> Excepted Err Code </th>" . "\n";
        echo "<th> Given Err Code </th>" . "\n";
        echo "<th> DIFF OK or NOK </th>" . "\n";
        $dajrektoriis = ""; # pole pro slozky
        if ($recursive) #chceme projit rekurzivne?
            exec("find " . $directory . " -regex '.*\.src$'", $dajrektoriis); 
        else #nechceme
            exec("find " . $directory . " -maxdepth 1 -regex '.*\.src$'", $dajrektoriis);
        foreach ($dajrektoriis as $source) { #pruchod pres vsechny src soubory
            $parseOutput = tempnam("/tmp", ""); #docasny soubor pro output parseru
            $rc = 0; #predem si nastavime error code na 0
            $pathParts = explode('/', $source); #rozdelime si podle forward slash
            $testName = explode('.', end($pathParts))[0]; #ulozime si nazev testu posledni jmeno pred .src
            $testPath = ""; #vytvoreni nove polozky v tabulce
            echo "<tr>" . "\n";
            
            foreach (array_slice($pathParts, 0, -1) as $dir) {
                $testPath = $testPath . $dir . '/';
            }
            #nastaveni zakldanich hodnot nove polozky
            echo "<th>". $indexace ."</th>" . "\n";
            echo "<th>". $testPath ."</th>" . "\n";
            echo "<th>". $testName ."</th>" . "\n";
            $fullpath = $testPath . $testName;
            $srcfile = $fullpath . ".src";
            $rcfile = $fullpath . ".rc";
            $outfile = $fullpath . ".out";
            #kontrola souboru s chybovym kodem
            if (!file_exists($rcfile)) {
                $file = fopen($rcfile, "w");
                if (!$file) {
                    exit(12);
                }
                fwrite($file, "0");
                fclose($file);
            }
            else {
                $file = fopen($rcfile, "r");
                $rc = intval(fread($file, filesize($rcfile)));
                fclose($file);  
            }
            #spusti parse.php s src souborem a vystup posle do parse outer
            exec("php7.4 " . $parse_file . " < " . $srcfile, $parseouter, $parseerror);
            $outputstring = "";
            foreach ($parseouter as $every) {
                $outputstring = $outputstring . $every . "\n";
            } #slepeni outputu z parseru
            $parseouter = ""; #napsani outputu do souboru na porovnani
            $outputFile = fopen($parseOutput, "w");
            fwrite($outputFile, $outputstring);
            fclose($outputFile);
            $diff_code = 0; #nastaveni diff codu na 0
            $exec = "";
            if ($parseerror == $rc) {
                if ($parseerror == 0) {
                    if (!file_exists($outfile)) {
                        $file = fopen($outfile, "w");
                        fclose($file);
                    }
                    exec("java -jar $jexam_xml $parseOutput $outfile ", $exec, $diff_code);
                    if ($diff_code == 0) {
                        $passed++;
                    }
                    else {
                        $failed++;
                    }
                }
                else {
                    $passed++;
                }
            }
            else {
                $failed++;
                $nokok = "ERROR &#10007; !!";
            }
            if ((!$diff_code) && ($parseerror == $rc)) {
                $nokok = "OK &#10003;";
            }
            else {
                $nokok = "ERROR &#10007; !!";
            }
            if ($parseerror == $rc) {
                echo "<th style=\"background-color: #00FF00;\">". "&#10003;"."</th>" . "\n";
                echo "<th>". $rc ."</th>" . "\n";
                echo "<th>". $parseerror ."</th>" . "\n";
                if ($nokok == "ERROR &#10007; !!") 
                    echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                else
                    echo "<th style=\"background-color: #00FF00;\">". $nokok ."</th>" . "\n";
            }
            else {
                echo "<th style=\"background-color: red;\">". "&#10007;"."</th>" . "\n";
                echo "<th>". $rc ."</th>" . "\n";
                echo "<th>". $parseerror ."</th>" . "\n";
                if ($nokok == "ERROR &#10007; !!") 
                    echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                else
                    echo "<th style=\"background-color: #00FF00;\">". $nokok ."</th>" . "\n";
            }
            echo "</tr>" . "\n";
            $indexace++;
            
        }
        $all = $passed + $failed;
        $all = $indexace-1;
        echo "</table>" . "\n";
        echo "<br><br><br>Summary:<br> ______________________<br> <br> <br>" . "\n";
        echo "Tests total: " . $all    . "\n";
        echo "Tests passed: " . $passed   . "\n";
        echo "Tests failed: " . $failed . "\n";
        echo "<br>";
        echo "<br>";
        echo "<br>";
        if (!$failed){
            echo "All tests passed!! Congratulations &#128515;";
        }
        else {
            echo "Some tests failed, check whats wrong &#128577;";
        }
        echo "<br><br><br>";
        echo "</html>" . "\n";
    }
    #obdobne probiha i pro int only 
    else if ($int_only) {
        $indexace = 1;
        echo "<!DOCTYPE HTML>" . "\n";
	    echo "<html lang=\"cs\">" . "\n";
	    echo "<head>" . "\n";
	    echo "<meta charset=\"utf-8\">" . "\n";
	    echo "<meta name=\"viewport\" content=\"width=1920, initial-scale=1.0\">" . "\n";
        echo "<title>IPP project</title>" . "\n";
        echo "<style>" . "\n";
        echo "html {" . "\n";
        echo "background-color: #F0F8FF;" . "\n";
        echo "text-align: center;" . "\n";
        echo "}" . "\n";
        echo "body {" . "\n";
        echo "text-align: center;" . "\n";
        echo "padding-bottom: 100px;" . "\n";
        echo "}" . "\n";
        echo "table {" . "\n";
        echo "font-family: arial, sans-serif;" . "\n";
        echo "border-collapse: collapse;" . "\n";
        echo "width: 70%;" . "\n";
        echo "}" . "\n";
        echo "td, th {" . "\n";
        echo "border: 1px solid #dddddd;" . "\n";
        echo "text-align: left;" . "\n";
        echo "padding: 8px;" . "\n";
        echo "}" . "\n";
        echo "tr:nth-child(even) {" . "\n";
        echo "background-color: #87CEFA;" . "\n";
        echo "}" . "\n";
        echo "</style>" . "\n";
	    echo "</head>" . "\n";
	    echo "<body>" . "\n";
        echo "<h1> IPP Project_2: test.php</h1>" . "\n";
	    echo "<h2> MODE: Interpret Only </h2>" . "\n";
	    echo "<table style=\"margin: 0 auto;\">" . "\n";
        echo "<tr>" . "\n";
        echo "<th> Test. No. : </th>" . "\n";
        echo "<th> Directory </th>" . "\n";
        echo "<th> Test </th>" . "\n";
        echo "<th> ERR Code OK or NOK </th>" . "\n";
        echo "<th> Excepted Err Code </th>" . "\n";
        echo "<th> Given Err Code </th>" . "\n";
        echo "<th> DIFF OK or NOK </th>" . "\n";
        $dajrektoriis = "";
        if ($recursive) 
            exec("find " . $directory . " -regex '.*\.src$'", $dajrektoriis); 
        else 
            exec("find " . $directory . " -maxdepth 1 -regex '.*\.src$'", $dajrektoriis);
        foreach ($dajrektoriis as $source) {
            $parseOutput = tempnam("/tmp", "");
            $rc = 0;
            $pathParts = explode('/', $source);
            $testName = explode('.', end($pathParts))[0];
            $testPath = "";
            echo "<tr>";
            
            foreach (array_slice($pathParts, 0, -1) as $dir) {
                $testPath = $testPath . $dir . '/';
            }
            echo "<th>". $indexace ."</th>";
            echo "<th>". $testPath ."</th>";
            echo "<th>". $testName ."</th>";
            $fullpath = $testPath . $testName;
            $srcfile = $fullpath . ".src";
            $rcfile = $fullpath . ".rc";
            $outfile = $fullpath . ".out";
            $infile = $fullpath . ".in";

            if (!file_exists($infile)) {
                $file = fopen($infile, "w");
                fclose($file);
            }
            if (!file_exists($rcfile)) {
                $file = fopen($rcfile, "w");
                if (!$file) {
                    exit(12);
                }
                fwrite($file, "0");
                fclose($file);
            }
            else {
                $file = fopen($rcfile, "r");
                $rc = intval(fread($file, filesize($rcfile)));
                fclose($file);  
            }
            exec("python3.8 " . $int_file . " --source=" . $srcfile . " < " . $infile, $outputfiler, $errcode);
            $outputstring = "";
            foreach ($outputfiler as $every) {
                $outputstring = $outputstring . $every . "\n";
            }
            $outputfiler = "";
            $outputFile = fopen($parseOutput, "w");
            fwrite($outputFile, $outputstring);
            fclose($outputFile);
            $exec = "";
            $diff_code = 0;
            if ($errcode == $rc) {
                if ($errcode == 0) {
                    if (!file_exists($outfile)) {
                        $file = fopen($outfile, "w");
                        fclose($file);
                    }

                    exec("diff -Z " . $outfile . " " . $parseOutput, $outt, $diff_code);
                    
                    if ($diff_code == 0) {
                        $passed++;
                    }
                    else {
                        $failed++;
                    }
                }
                else {
                    $passed++;
                }
            }
            else {
                $failed++;
                $nokok = "ERROR &#10007; !!";
            }
            if ((!$diff_code) && ($errcode == $rc)) {
                $nokok = "OK &#10003;";
            }
            else {
                $nokok = "ERROR &#10007; !!";
            }
            if ($errcode == $rc) {
                echo "<th style=\"background-color: #00FF00;\">". "&#10003;"."</th>" . "\n";
                echo "<th>". $rc ."</th>" . "\n";
                echo "<th>". $errcode ."</th>" . "\n";
                if ($nokok == "ERROR &#10007; !!") 
                    echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                else
                    echo "<th style=\"background-color: #00FF00;\">". $nokok ."</th>" . "\n";
            }
            else {
                echo "<th style=\"background-color: red;\">". "&#10007;"."</th>" . "\n";
                echo "<th>". $rc ."</th>" . "\n";
                echo "<th>". $errcode ."</th>" . "\n";
                if ($nokok == "ERROR &#10007; !!") 
                    echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                else
                    echo "<th style=\"background-color: #00FF00;\">". $nokok ."</th>" . "\n";
            }
            echo "</tr>" . "\n";
            $indexace++;
        }
        $all = $passed + $failed;
        echo "</table>" . "\n";
        echo "<br><br><br>Summary:<br> ______________________<br> <br> <br>" . "\n";
        echo "Tests total: " . $all    . "\n";
        echo "Tests passed: " . $passed   . "\n";
        echo "Tests failed: " . $failed . "\n";
        echo "<br>";
        echo "<br>";
        echo "<br>";
        if (!$failed){
            echo "All tests passed!! Congratulation &#128515;";
        }
        else {
            echo "Some tests failed.. Check What's wrong &#128577;";
        }
        echo "<br><br><br>";
	    echo "</body>" . "\n";
	    echo "</html>" . "\n";
    }
    else {
        $indexace = 1;
        echo "<!DOCTYPE HTML>" . "\n";
	    echo "<html lang=\"cs\">" . "\n";
	    echo "<head>" . "\n";
	    echo "<meta charset=\"utf-8\">" . "\n";
	    echo "<meta name=\"viewport\" content=\"width=1920, initial-scale=1.0\">" . "\n";
        echo "<title>IPP project</title>" . "\n";
        echo "<style>" . "\n";
        echo "html {" . "\n";
        echo "background-color: #F0F8FF;" . "\n";
        echo "text-align: center;" . "\n";
        echo "}" . "\n";
        echo "body {" . "\n";
        echo "text-align: center;" . "\n";
        echo "}" . "\n";
        echo "table {" . "\n";
        echo "font-family: arial, sans-serif;" . "\n";
        echo "border-collapse: collapse;" . "\n";
        echo "width: 70%;" . "\n";
        echo "}" . "\n";
        echo "td, th {" . "\n";
        echo "border: 1px solid #dddddd;" . "\n";
        echo "text-align: left;" . "\n";
        echo "padding: 8px;" . "\n";
        echo "}" . "\n";
        echo "tr:nth-child(even) {" . "\n";
        echo "background-color: #87CEFA;" . "\n";
        echo "}" . "\n";
        echo "</style>" . "\n";
	    echo "</head>" . "\n";
	    echo "<body>" . "\n";
        echo "<h1> IPP Project_2: test.php</h1>" . "\n";
	    echo "<h2> MODE: BOTH </h2>" . "\n";
	    echo "<table style=\"margin: 0 auto;\">" . "\n";
        echo "<tr>" . "\n";
        echo "<th> Test. No. : </th>" . "\n";
        echo "<th> Directory </th>" . "\n";
        echo "<th> Test </th>" . "\n";
        echo "<th> ERR Code OK or NOK </th>" . "\n";
        echo "<th> Excepted Err Code </th>" . "\n";
        echo "<th> Given Err Code </th>" . "\n";
        echo "<th> DIFF OK or NOK </th>" . "\n";
        $dajrektoriis = "";
        if ($recursive) 
            exec("find " . $directory . " -regex '.*\.src$'", $dajrektoriis); 
        else 
            exec("find " . $directory . " -maxdepth 1 -regex '.*\.src$'", $dajrektoriis);
        foreach ($dajrektoriis as $source) {
            $parseOutput = tempnam("/tmp", "");
            $rc = 0;
            $pathParts = explode('/', $source);
            $testName = explode('.', end($pathParts))[0];
            $testPath = "";
            echo "<tr>" . "\n";
            
            foreach (array_slice($pathParts, 0, -1) as $dir) {
                $testPath = $testPath . $dir . '/';
            }
            $fullpath = $testPath . $testName;
            echo "<th>". $indexace ."</th>" . "\n";
            echo "<th>". $testPath ."</th>" . "\n";
            echo "<th>". $testName ."</th>" . "\n";
            $srcfile = $fullpath . ".src";
            $rcfile = $fullpath . ".rc";
            $outfile = $fullpath . ".out";
            $infile = $fullpath . ".in";


            if (!file_exists($rcfile)) {
                $file = fopen($rcfile, "w");
                if (!$file) {
                    exit(12);
                }
                fwrite($file, "0");
                fclose($file);
            }
            else {
                $file = fopen($rcfile, "r");
                $rc = intval(fread($file, filesize($rcfile)));
                fclose($file);  
            }
            
            exec("php7.4 " . $parse_file . " < " . $srcfile, $parseouter, $parseerror);
            $outputstring = "";
            foreach ($parseouter as $every) {
                $outputstring = $outputstring . $every . "\n";
            }
            $parseouter = "";
            $outputFile = fopen($parseOutput, "w");
            fwrite($outputFile, $outputstring);
            fclose($outputFile);
            $diff_code = 0;
            $exec = "";
            if ($parseerror == 0) {
                if (!file_exists($infile)) {
                    $file = fopen($infile, "w");
                    fclose($file);
                }
                if (!file_exists($outfile)) {
                    $file = fopen($outfile, "w");
                    fclose($file);
                }
                exec("python3.8 " . $int_file . " --source=" . $parseOutput . " < " . $infile, $outputfiler, $errcode);
                $outputstring = "";
                foreach ($outputfiler as $every) {
                    $outputstring = $outputstring . $every . "\n";
                }
                $outputfiler = "";
                $outputFile = fopen($parseOutput, "w");
                fwrite($outputFile, $outputstring);
                fclose($outputFile);
                $exec = "";
                $diff_code = 0;
                if ($errcode == $rc) {
                    if ($errcode == 0) {
                        exec("diff -Z " . $outfile . " " . $parseOutput, $outt, $diff_code);
                        
                        if ($diff_code == 0) {
                            $passed++;
                        }
                        else {
                            $failed++;
                        }
                    }
                    else {
                        $passed++;
                    }
                }
                else {
                    $failed++;
                    $nokok = "ERROR &#10007; !!";
                }
                if ((!$diff_code) && ($errcode == $rc)) {
                    $nokok = "OK &#10003;";
                }
                else {
                    $nokok = "ERROR &#10007; !!";
                }
                if ($errcode == $rc) {
                    echo "<th style=\"background-color: #00FA00;\">". "&#10003;"."</th>" . "\n";
                    echo "<th>". $rc ."</th>" . "\n";
                    echo "<th>". $errcode ."</th>" . "\n";
                    if ($nokok == "ERROR &#10007; !!") 
                        echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                    else
                        echo "<th style=\"background-color: #00FA00;\">". $nokok ."</th>" . "\n";
                }
                else {
                    echo "<th style=\"background-color: red;\">". "&#10007;"."</th>" . "\n";
                    echo "<th>". $rc ."</th>" . "\n";
                    echo "<th>". $errcode ."</th>" . "\n";
                    if ($nokok == "ERROR &#10007; !!") 
                        echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
                    else
                        echo "<th style=\"background-color: #00FA00;\">". $nokok ."</th>" . "\n";
                }
                echo "</tr>" . "\n";
            $all = $passed + $failed;
            }
            else {
                $failed++;
                echo "<th style=\"background-color: red;\">". "&#10007;"."</th>" . "\n";
                echo "<th>". 0 ."</th>" . "\n";
                echo "<th>". $parseerror ."</th>" . "\n";
                $nokok = "ERROR &#10007; !!";
                echo "<th style=\"background-color: red;\">". $nokok ."</th>" . "\n";
            }
            $indexace++;
        }
        $all = $indexace-1;
        echo "</table>" . "\n";
        echo "<br><br><br>Summary:<br> ______________________<br> <br> <br>" . "\n";
        echo "Tests total: " . $all    . "\n";
        echo "Tests passed: " . $passed   . "\n";
        echo "Tests failed: " . $failed . "\n";
        echo "<br>";
        echo "<br>";
        echo "<br>";
        if (!$failed){
            echo "All tests passed!! Congratulation &#128515;";
        }
        else {
            echo "Some tests failed.. Check What's wrong &#128577;";
        }
        echo "<br><br><br>";
        echo "</body>" . "\n";
        echo "</html>" . "\n";
    }

?>
