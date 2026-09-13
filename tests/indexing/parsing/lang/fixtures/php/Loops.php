<?php

function joinParts(array $parts): string
{
    $out = "";
    for ($i = 0; $i < count($parts); $i++) {
        $out .= $parts[$i];
        $out .= ",";
    }
    return $out;
}

function largest(array $xs): int
{
    $max = $xs[0];
    foreach ($xs as $x) {
        $max = $x > $max ? $x : $max;
    }
    return $max;
}

function fib(int $n): int
{
    $a = 0;
    $b = 1;
    while ($n > 0) {
        $next = $a + $b;
        $a = $b;
        $b = $next;
        $n = $n - 1;
    }
    return $a;
}

function digits(int $n): int
{
    $count = 0;
    do {
        $n = intdiv($n, 10);
        $count = $count + 1;
    } while ($n != 0);
    return $count;
}
