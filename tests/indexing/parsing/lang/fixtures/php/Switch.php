<?php

function colorName(int $code): string
{
    $name = "";
    switch ($code) {
        case 1:
            $name = "red";
            $name = strtoupper($name);
            break;
        case 2:
            $name = "green";
            $name = $name . "!";
            break;
        default:
            $name = "unknown";
            $name = substr($name, 0, 3);
    }
    return $name;
}
