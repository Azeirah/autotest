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

* Organize test-cases for the trace and profile parser
* Add a convenient way to automatically turn capturing on and off with one accessible command
* Work on reducing database size
  * Minimize filename redunancy by creating a `files` table
  * (I know that db size is _very_ optimizable, standard zipping takes from 3.2GB to 140MB, 7z ultra from 3.2GB to _43MB_, compression ratio of 74x!)
* Parsing is very slow
  * Parallelize?
  * Automatically parse in the background with a daemon/service?
  * Speed up parsing bij offloading that in Rust/C++?
* Normalize parameters
  * Add a `params` or even `values` table
  * 1-to-many for `function_call` to `params`
### Relevant documentation

[The documentation of xdebug's profile format](http://valgrind.org/docs/manual/cl-format.html)