# Autotest

A project exploring the possibilities of parsing run-time function trace parameters and return values to automatically generate test cases and generate insight into the working of your application.

## Usage overview

This is a work-in-progress, but these are the most interesting starting points:

### Dependencies

* A recent version of PHP
* xdebug
* python3
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
xdebug.trace_output_name="%t"

xdebug.profiler_enable=1
xdebug.profiler_output_dir=/home/mb/Documents/autotest/trace-data/
xdebug.profiler_output_name="%t.xp"
```

You can find additional info on xdebug configuration parameters [here](https://xdebug.org/docs/all_settings)

### Generating tracefiles

Once you've set-up your php.ini configuration, due to the `xdebug.auto_trace=1` option, any php file you run automatically gets traced. The trace files get sent to your `xdebug.trace_output_name` folder.

### Basic tracefile analysis

```sh
python3 PHPTraceCLI.py <tracefile>
```

This is a simple command-line-interface to introspect php trace files. Like the entire project, it's a WIP, but it supports some useful functionality. The tool itself is documented well enough so you can run it and it will explain itself.