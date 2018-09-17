<?php

require("A.php");

A();
// can we figure out from the trace alone that the function 'ambiguous' comes from the file 'A'?
// keep in mind that we have this constraint; the trace file _alone_, we're not allowed to look at the required files
