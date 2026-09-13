<?php

class Outer
{
    private function makeInner(): object
    {
        return new class {
            public function innerMethod(): string
            {
                return "inner";
            }
        };
    }
}
