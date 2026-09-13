<?php

abstract class Repository
{
    abstract public function abstractMethod(): void;

    public function emptyBody(): void
    {
    }

    public function withLogic(array $items): int
    {
        $total = 0;
        foreach ($items as $item) {
            if ($item > 0) {
                $total += $item;
            }
        }
        return $total;
    }
}
