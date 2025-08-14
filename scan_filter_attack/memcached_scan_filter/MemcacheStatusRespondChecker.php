<?php

function thread($ip, $output, $responselength) {
	//stats,Tester
	$len = LengthMemcachedUDPStat($ip, TEST_TIMEOUT);
	if ($len >= $responselength) {
		addentry($output, $ip);
		print($ip . " " . $len . " [x" . round($len / STAT_QUERY_LENGTH, 2) . "]\n");
	}
}
include __DIR__ . "/libmemc.php";
include __DIR__ . "/libtest.php";
include __DIR__ . "/thread.php";