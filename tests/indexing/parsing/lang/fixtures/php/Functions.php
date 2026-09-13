<?php

namespace App;

class Calculator
{
    public function add(int $a, int $b): int
    {
        return $a + $b;
    }

    public static function greet(string $name): string
    {
        return "Hello, {$name}!";
    }
}

function normalize(string $text): string
{
    return strtolower(trim($text));
}

function repeat(string $text, int $times): string
{
    return str_repeat($text, $times);
}
