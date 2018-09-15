<?php

function ambiguous() {
    return "A";
}

function A() {
    ambiguous();
}
