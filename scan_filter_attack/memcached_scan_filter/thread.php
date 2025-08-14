<?php
if (threadfound($argv) == true) {
	die(thread($argv[1], $argv[2], $argv[3]));
} else {
	$argn_invalid = FALSE;
	foreach([1,2,3,4] as $argn){
		if (!isset($argv[$argn])){
			$argn_invalid = TRUE;
		}
	}
	if ($argn_invalid){
		$self = basename($_SERVER["SCRIPT_FILENAME"], '.php') . '.php';
		echo "Usage: php {$self} [Input.txt] [Output.txt] [Response Size] [Threads]",PHP_EOL;
		die(10086);
	}
	unset($argn_invalid);
	die(start_threading($argv[1], $argv[2], $argv[3], $argv[4]));
}