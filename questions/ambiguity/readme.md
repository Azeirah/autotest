# Can you figure out from a trace alone where a called function is defined?

Traces at the very least contain a property 'user-defined' which is `false` for built-ins.
I want to know if it's possible to figure out where a `true` function comes from from the trace data alone.

Given this three file scenario, do we somehow have the data to disambiguate the definition of the file `ambiguous`?

```main.php

require("A.php");
require("B.php");

A();
B();
```

```A.php
function ambiguous() {
    return "A";
}
 the
function A() {
    ambiguous();
}
```

```B.php
function ambiguous() {
    return "B";
}

function B() {
    ambiguous();
}
```


## Ambiguity

Well, I learned something. You cannot define a function with a name that is already loaded. PHP will simply throw an exception, that's a good thing! Makes my work a lot easier I imagine.

So on to the real question, can we find out where a function is defined given the trace alone? Do I have to parse the main file and all included files to figure out where the function is defined? That wouldn't be great :c

## Function definition location

By inspecting the trace only, it doesn't look like we can figure out where a function is defined.
You can see where a function is called, but not where it is defined.
Maybe there's an option that can help?

...

Nope! There's no option. Finding out statically would be hell also, functions can be nested, returned, defined in weird nested class-private scopes and stuff. Possible, but not something I'd like to spend two weeks on getting right.

There is a simpler alternative, XDEBUG's profiler _does_ include where the function originated from.
If it's possible to parse both the profile _and_ the trace, and then wire them together, then we have the data we need.

There are some obvious concerns about performance and memory usage, running _both_ a trace _and_ a profiler, but that's only a concern for the future, I'm more interested in getting it done now.

