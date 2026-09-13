<?php

function process(array $xs, int $threshold): int
{
    $total = 0;
    foreach ($xs as $x) {
        if ($x > $threshold) {
            try {
                $total = $total + intdiv(100, $x);
            } catch (DivisionByZeroError $e) {
                $total = $total - 1;
            }
        }
    }
    return $total;
}
