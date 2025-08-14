<?php

include __DIR__ . "/config.php";

set_error_handler(function ($errno, $errstr, $errfile, $errline, array $errcontext) {
	// error was suppressed with the @-operator
	if (0 === error_reporting()) {
		return false;
	}

	throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
});

function addentry($file, $entry) {
	if (!file_exists($file)) {
		touch($file);
		chmod($file, 0777);
	}
	$fh = fopen($file, 'a') or die("Can't open file: " . $file);
	fwrite($fh, $entry . PHP_EOL);
	fclose($fh);
}
function mc_udprelay($host, $timeout = 1, $data) {
	$data = "\x00\x00\x00\x00\x00\x01\x00\x00$data\r\n";
	$socket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
	socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => $timeout, 'usec' => 0));
	if (socket_connect($socket, $host, 11211)) {
		socket_send($socket, $data, strLen($data), 0);
		$buf = "";
		$from = "";
		$port = 0;
		$endtime = microtime(TRUE) + $timeout;
		while (microtime(true) <= $endtime) {
			try {
				$buf .= socket_read($socket, 4096);
			} catch (Exception $e) {
				break;
			}

		}
		socket_close($socket);
		return $buf;
	} else {
		puts("$host : failed to connect");
	}

}

function LengthMemcachedUDPStat($host, $timeout = 1) {
	$length = strlen(mc_udprelay($host, $timeout, "stats"));
	if ($length > 0) {
		puts("[UDP Relay] $host Response length : $length");
	}

	return $length;
}
function MemcachedUDPGet($host, $timeout = 1, $key) {
	return mc_udprelay($host, $timeout, "get $key");
}

function puts($data) {
	file_put_contents("./log", $data . PHP_EOL, FILE_APPEND);
}
function threadfound(array $argv) {
	$thread = false;
	foreach ($argv as $arg) {
		if ($arg == 'THREAD') {
			$thread = true;
			break;
		}
	}
	return $thread;
}

?>