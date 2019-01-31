# Autotest

A project exploring the possibilities of parsing run-time function trace parameters and return values to automatically generate test cases and generate insight into the working of your application.

## Usage overview

This is a work-in-progress, but these are the most interesting starting points:

### Dependencies

* A recent version of PHP
* xdebug
* python3 64-bit (64-bit is _important_! This application can run into memory issues without using Python 64-bit, be careful.)
* sqlite3

See the dockerfile for approximate dependencies.
The dockerfile is not meant to run this application with (although it might in the future), for now, it's used to document the dependencies.

### Setting-up php traces

To get started, you need to install xdebug and configure your php.ini

```
# configure your extension, path is liiikely different
zend_extension=/usr/lib/php/20151012/xdebug.so

[xdebug]
xdebug.auto_trace=1
xdebug.collect_params=3
xdebug.trace_output_dir=/home/mb/Documents/autotest/trace-data/
xdebug.trace_format=1
xdebug.collect_return=1
xdebug.trace_output_name="%u %U"

xdebug.var_display_max_data=-1
xdebug.var_display_max_children=-1
xdebug.var_display_max_depth=-1

xdebug.profiler_enable=1
xdebug.profiler_output_dir=/home/mb/Documents/autotest/trace-data/
xdebug.profiler_output_name="%u %U.xp"
```

In addition to your php.ini you also need to activate the apache module `mod_unique` in httpd.conf

```
LoadModule unique_id_module modules/mod_unique_id.so
```

You can find additional info on xdebug configuration parameters [here](https://xdebug.org/docs/all_settings)

### Generating tracefiles

Once you've set-up your php.ini configuration, due to the `xdebug.auto_trace=1` option, any php file you run automatically gets traced. The trace files get sent to your `xdebug.trace_output_name` folder.

### Basic tracefile analysis

```sh
python3 PHPTraceCLI.py <tracefile>
```

This is a simple command-line-interface to introspect php trace files. Like the entire project, it's a WIP, but it supports some useful functionality. The tool itself is documented well enough so you can run it and it will explain itself.

### TODO

* [x] Organize test-cases for the trace and profile parser
* [x] Add a convenient way to automatically turn capturing on and off with one accessible command
* [x] Add a "watch" command
* [x] Work on reducing database size
  * [x] Minimize filename redunancy by creating a `files` table
  * [x] (I know that db size is _very_ optimizable, standard zipping takes from 3.2GB to 140MB, 7z ultra from 3.2GB to _43MB_, compression ratio of 74x!)
* [x] Normalize parameters
  * [x] Add a `params` or even `values` table
  * [x] 1-to-many for `function_call` to `params`
* [x] Add more diagnostics to the insights
    * [x] Memory usage per function call
    * [x] Time per function call
* [x] Add type column to the `values` table for all PHP types.
* [ ] Higher level diagnostics
    * [ ] Parameter type inference
    * [ ] ...?

### Goals

This is mostly a research project, though the goal is to provide real-world value in a (php) work environment.

This research started as a way to ask and answer one question:

During programming, after changing a function, "did I break something", "did I introduce a breaking change?".

The standard answer is "write tests", but I'm in an environment where tests are not allowed; so I had to improvise (innovation stems from necessity!)

This tool is based on a single, important insight: Code that runs, is code that works. If you, the developer, log-in to your webapplication, and the login authentication was succesful, then you've implicitly written a test-case. Unfortunately, this information is lost.

By recording program execution traces, you can record information about function calls, and therefore, preserve these otherwise lost implicit tests. Hence, the name "autotest".

However, over time, it became clear that you can do much more than just aid the developer in finding regressions, and with the information captured, the goal is to provide the IDE with the data/information it needs to provide the developer with answer to her questions, which would otherwise need to be gathered manually.


#### Questions

While programming, an interesting way to frame the interaction between you (dev), the output (web-browser/application) and the IDE you use, is "asking the IDE questions".

For instance, while programming

"Who calls this function?"
"Who does this function call?"
"How many variables are in this function?"
"..."

The purpose of the IDE, within this framing, is to make (1) help you ask the right questions, (2) provide you with the best answer as quickly as possible whenever it is being asked for and (3) help you integrate your new insights into the code with as little effort as possible.

Where IDE's fall short, however, is that there are many questions I ask of my code every single day, that the IDE has _no_ way of answering. Here are several examples, the IDE does provide _some_ answers to _some_ of these questions, but most involve a painful amount of manual effort.

"Did the function I'm currently looking at run before?"
"In an if/else statement, has this branch ever been executed?"
"Is this function fast or slow?"
"Has this function ever thrown an exception in practice?"
"Does this function consume a lot of memory?"




### Relevant documentation

[The documentation of xdebug's profile format](http://valgrind.org/docs/manual/cl-format.html)
