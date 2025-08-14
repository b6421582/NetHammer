<?php

function MemcachedTester($host, $timeout = 1) {
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
		while ($max > 1000) {
			if ($m->set(md5($host), $inject) == TRUE) {
				$keys_seted = TRUE;
				$puts .= "Key MaxSize: $max; ";
				break;
			} else {
				$inject = substr($inject, 1);
				$max = $max * 0.9;
				$puts .= "Size Over, try $max";
			}
		}
		if ($max <= 1000) {
			die();
		}
		$result = MemcachedUDPGet($host, $timeout, md5($host));
		if ($result) {
			puts($puts);
			if ($keys_seted) {
				$m->delete(md5($host));
			}
			return strlen($result);
		}
	} catch (Exception $e) {
		puts($puts);
		die();
	}
}


function MSEARCH($host, $timeout = 1) {
	$data = "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n";
	$socket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
	socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => $timeout, 'usec' => 0));
	socket_connect($socket, $host, 1900);
	socket_send($socket, $data, strLen($data), 0);
	$buf = "";
	$from = "";
	$port = 0;
	@socket_recvfrom($socket, $buf, 1000, 0, $from, $port);
	socket_close($socket);
	return strlen($buf);
}

function start_threading($input, $output, $responselength, $maxthreads) {
	$self = basename($_SERVER["SCRIPT_FILENAME"], '.php') . '.php';
	$usage = "Usage: php {$self} [Input.txt] [Output.txt] [Response Size] [Threads]";
	$error = "";
	if (strlen($input) == 0) {
		$error = "Error: Invalid Filename!";
	}
	if (strlen($output) == 0) {
		$error .= "\nError: Invalid Filename!";
	}
	if (is_numeric($responselength) == false) {
		$error .= "\nError: Invalid Response Length!";
	}
	if ($maxthreads < 1 || $maxthreads > 1000) {
		$error .= "\nError: Invalid Threads!";
	}
	if (strlen($error) >= 1) {
		die($error . "\n" . $usage . "\n");
	}
	print("\nSSDP Filter\t//Memcached Filter\nCoded by Layer4\n\n");
	print("nope.I am the memcached filter. faq -- arily\n");
	print("This code got a serious problem on calculating amp rate\nI don't know if it's my code's fault or the php's falut\nAlso distortion of the result will causing by the slow internet connection, slow CPU speed or the slow iface.\nIncrease timeout limit will kind of decreasing the distortion\n");
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

					$pipe[$j] = popen("php {$self} {$ip} {$output} {$responselength} THREAD", 'w'); //('php' . ' ' . $self . ' ' . $ip . ' ' . $output . ' ' . $responselength . ' ' . 'THREAD')
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
	fclose($handle);
}
