<?php

function parseOrZero(string $text): int
{
    $value = 0;
    try {
        $value = intval($text);
        $value = $value * 2;
    } catch (InvalidArgumentException $e) {
        $value = 0;
        $text = $e->getMessage();
    } finally {
        $text = trim($text);
        $value = $value + strlen($text);
    }
    return $value;
}

function elementAt(array $xs, int $i, int $fallback): int
{
    $result = 0;
    try {
        $result = $xs[$i];
        $result = $result + $i;
    } catch (OutOfRangeException $e) {
        $result = $fallback;
        $fallback = $fallback - 1;
    } catch (TypeError $e) {
        $result = 0;
    }
    return $result;
}
