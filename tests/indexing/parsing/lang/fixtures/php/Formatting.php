<?php

function tier(int $score): string
{
    $label = "";
    if ($score >= 90)
    {
        $label = "gold";
        $score -= 90;
    }
    elseif ($score >= 50)
    {
        $label = "silver";
    }
    else
    {
        $label = "bronze";
        $score = 0;
    }
    return $label;
}

function product(
    array $factors,
    int $start
): int {
    $total = 1;
    for (
        $i = $start;
        $i < count($factors);
        $i++
    ) {
        $total *= $factors[$i];
    }
    return $total;
}
