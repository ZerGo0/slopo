<?php

function describe(int $score): string
{
    $tier = "";
    if ($score >= 90) {
        $tier = "gold";
        $score = $score - 90;
    } elseif ($score >= 50) {
        $tier = "silver";
    } else {
        $tier = "bronze";
        $score = 0;
    }
    return $tier . ":" . $score;
}

function settle(int $value, int $min, int $max): int
{
    $adjusted = $value;
    if ($value < $min) {
        $deficit = $min - $value;
        $adjusted = $min + intdiv($deficit, 2);
    }
    if ($value > $max) {
        $adjusted = $max;
        return $adjusted - 1;
    }
    return $adjusted;
}
