from __future__ import print_function

import cmdman
import pdb
import pytest
import sys
import traceback

def test_init_unknown_kwarg():
    with pytest.raises(TypeError):
        c = cmdman.cmdman(THIS_DOES_NOT_EXIST=0)


def test_init_multiple_unknown_kwargs():
    with pytest.raises(TypeError):
        c = cmdman.cmdman(THIS_DOES_NOT_EXIST=0, THIS_NEITHER_DOES=False)


def test_simple_parser_print_help_no_args(capsys):
    with cmdman.cmdman() as c:
        assert c.parse(args=[]) == 1
        out, err = capsys.readouterr()
        assert not out
        assert err


def test_simple_parser_exits_on_help():
    with cmdman.cmdman() as c:
        with pytest.raises(SystemExit):
            c.parse(args=['--help'])


def test_simple_parser_help_no_exit():
    with cmdman.cmdman(should_exit=False) as c:
        ret = c.parse(args=['--help'])
    assert ret == 0


def test_simple_parser_no_catch_programming_error():
    def foo(args):
        raise ValueError('Do not catch me.')
    c = cmdman.cmdman(default_func=foo)
    with pytest.raises(ValueError):
        c.parse(args=[])


def test_simple_parser_gets_sysargv(monkeypatch):
    # This will be needed to monkeypatch the sys.argv value.
    cmdname = sys.argv[0]
    # This function just returns what it got as arguments so we can assert on
    # it.
    def foo(args):
        return (args.foo, args.bar)
    # Configure cmdman.
    c = cmdman.cmdman(default_func=foo)
    c.parser.add_argument('--foo', action='store_true', default=False)
    c.parser.add_argument('--bar', action='store_true', default=False)
    # Check that if we modify argv, the parameters are different for foo.
    monkeypatch.setattr(sys, 'argv', [cmdname])
    assert c.parse() == (False, False)
    monkeypatch.setattr(sys, 'argv', [cmdname, '--foo'])
    assert c.parse() == (True, False)
    monkeypatch.setattr(sys, 'argv', [cmdname, '--bar'])
    assert c.parse() == (False, True)
    monkeypatch.setattr(sys, 'argv', [cmdname, '--foo', '--bar'])
    assert c.parse() == (True, True)


def test_with_subparsers():
    def foo(args):
        return 1
    def bar(args):
        return 2
    c = cmdman.cmdman()
    c.add_subparser('foo', foo)
    c.add_subparser('bar', bar)
    assert c.parse(args=['foo']) == 1
    assert c.parse(args=['bar']) == 2


def test_print_backtrace(monkeypatch, capsys):
    pe_called, pdb_count = [], []
    def print_exc_count(*args, **kwargs):
        print('>>> This is a backtrace displayed <<<', file=sys.stderr)
        pe_called.append(1)
    def pdb_post_mortem(*args, **kwargs):
        pdb_count.append(1)
    monkeypatch.setattr(traceback, 'print_exc', print_exc_count)
    monkeypatch.setattr(pdb, 'post_mortem', pdb_post_mortem)
    assert (sum(pe_called), sum(pdb_count)) == (0, 0)
    # Configure a new parser and call it a few time to test when backtrace is
    # printed.
    def foo(args):
        raise ValueError()
    c = cmdman.cmdman(default_func=foo)
    with pytest.raises(ValueError):
        c.parse(args=[])
    assert (sum(pe_called), sum(pdb_count)) == (0, 0)
    # Still not called since we raise a ValueError even though we ask for it,
    # indeed python will display it for us, no need for it twice.
    with pytest.raises(ValueError):
        c.parse(args=['--backtrace'])
    assert (sum(pe_called), sum(pdb_count)) == (0, 0)
    # Now we use a new function that actually raises something cmdman is
    # supposed to manage.
    def bar(args):
        raise cmdman.CMDMAN_CMDError('this is an error the user can see')
    c = cmdman.cmdman(default_func=bar)
    assert c.parse(args=[]) == 1
    out, err = capsys.readouterr()
    assert err == 'ERROR: this is an error the user can see\n'
    assert (sum(pe_called), sum(pdb_count)) == (0, 0)
    # Now we finally ask to display the backtrace.
    assert c.parse(args=['--backtrace']) == 1
    out, err = capsys.readouterr()
    assert (sum(pe_called), sum(pdb_count)) == (1, 0)
    assert err == '>>> This is a backtrace displayed <<<\n'
    # Now we check we also get calls on pdb.
    assert c.parse(args=['--pdb']) == 1
    assert (sum(pe_called), sum(pdb_count)) == (1, 1)
