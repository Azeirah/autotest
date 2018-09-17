<?php
require dirname(__FILE__) . './../vendor/autoload.php';

$dom = new IvoPetkov\HTML5DOMDocument();
$dom->loadHTML(file_get_contents('./large-html-sample.html'));
echo $dom->saveHTML();
