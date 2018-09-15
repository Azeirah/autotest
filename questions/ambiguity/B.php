<?php

function ambiguous() {
    return "B";
}

function B() {
    ambiguous();
}
