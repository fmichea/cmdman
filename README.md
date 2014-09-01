cmdman: Simple command line program wrapper adding debugging arguments.
=======================================================================

Introduction
------------

This program provides a simple wrapper arround argparse to manage debugging of
applications easily. Here is was it does:

 - On creation of a `cmdman` instance, it initializes a new argparse parser
   accessible through `obj.parser`.
 - You can then call the `parse` function with the `args` parameter to parse
   your command line arguments. If no `args` is provided, `cmdman` simply uses
   `sys.argv` as the source. This function returns the "return code" advised by
   the feature called.

Now you have there are two possibilities: if you set up subparsers using the
`add_subparser` function, it will automatically call the associated function,
otherwise it will call the `default_func` provided in the init (default prints
help and returns 1).

If any of these functions raises a instance of a (sub)class of
`CMDMAN_CMDError`, this will be concider as a "command error" that should be
displayed properly to the user of your program. By default, it wraps the text
of the error on 70 columns, and prepends it with "ERROR: ". So for instance, if
your program does this:

    def main(args):
        if not os.path.isdir(args.output_dir):
            raise cmdman.CMDMAN_CMDError('output directory does not exist')
        # [...]

Then cmdman will display this error properly. Now the interesting part is that
you don't always want to hide the fact that this error was an exception in
reality. This is what `cmdman` is for. It adds two options to the argument
parser, `--backtrace` and `--pdb`.

The first one displays the backtrace of the actual exception, so you can ask
your users more information when they hit an error they should not.

But even more useful, if you can reproduce the bug, is the `--pdb` option that
allows you to debug from the point where the exception was raised.

To summarize, this small library provides a simple way to write command line
tools displaying user friendly errors without preventing you to debug/have your
users help you understand why they hit an error.

Full documentation of the API comming soon. Meanwhile, the code is less than
100 lines and commented, so you should probably go check it out to see what
options are available. Also, read the tests for example of usages.

How to install
--------------

    pip install cmdman

Example: examples/simple\_example.py
------------------------------------

    $ python examples/simple_example.py .
    .git
    cmdman
    examples
    LICENSE
    README.md
    requirements
    setup.py
    tests
    $ python examples/simple_example.py wedjkdj
    ERROR: directory does not exist.
    $ python examples/simple_example.py wedjkdj -b
    Traceback (most recent call last):
      File "/Users/franck/Projects/libs/cmdman/cmdman/__init__.py", line 79, in parse
        return self._default_func(args)
      File "examples/simple_example.py", line 9, in main
        raise cmdman.CMDMAN_CMDError('directory does not exist.')
    CMDMAN_CMDError: directory does not exist.
    $ python examples/simple_example.py wedjkdj -P
    > /Users/franck/Projects/libs/cmdman/examples/simple_example.py(9)main()
    -> raise cmdman.CMDMAN_CMDError('directory does not exist.')
    (Pdb) bt
      /Users/franck/Projects/libs/cmdman/cmdman/__init__.py(79)parse()
    -> return self._default_func(args)
    > /Users/franck/Projects/libs/cmdman/examples/simple_example.py(9)main()
    -> raise cmdman.CMDMAN_CMDError('directory does not exist.')
    (Pdb)

Other information
-----------------

 - Licence: New BSD Licence
 - Bug reports/Feature requests: `franck.michea@gmail.com`
