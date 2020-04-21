import io
import unittest
from contextlib import redirect_stderr, redirect_stdout


class TestPlayer(unittest.TestCase):
    def test_options(self):
        try:
            from awstracer.player import opt_parser
        except Exception:
            self.fail("cannot import opt_parser")
        with self.assertRaises(SystemExit):
            with redirect_stdout(io.StringIO()):
                with redirect_stderr(io.StringIO()):
                    opt_parser([])
                    # sleep delay cannot be negative so should exit
                    opt_parser(["--trace-file", "bla", "-s", "-1"])
        ns = opt_parser(["--trace-file", "bla"])
        self.assertEqual(ns.trace_file, "bla")
        # check default settings for options
        self.assertIsNone(ns.endpoint)
        self.assertIsNone(ns.params)
        self.assertIsNone(ns.profile)
        self.assertIsNone(ns.region)
        self.assertFalse(ns.dryrun)
        self.assertFalse(ns.debug)
        self.assertIsNone(ns.sleep_delay)
        self.assertTrue(ns.colorize)
        self.assertTrue(ns.stop_on_error)
        ns = opt_parser(["--trace-file", "bla", "--dryrun", "--region", "bl1", "--profile", "bl2", "--endpoint", "bl3", "-s", "2", "-d", "-f", "-c"])
        self.assertTrue(ns.dryrun)
        self.assertEqual(ns.region, "bl1")
        self.assertEqual(ns.profile, "bl2")
        self.assertEqual(ns.endpoint, "bl3")
        self.assertEqual(ns.sleep_delay, 2)
        self.assertTrue(ns.debug)
        self.assertFalse(ns.colorize)
        self.assertFalse(ns.stop_on_error)
        ns = opt_parser(["--trace-file", "bla", "--param", "p1", "val1", "--param", "p2", "val2"])
        self.assertIsInstance(ns.params, list)
        self.assertEqual(len(ns.params), 2)
        self.assertEqual(ns.params[0][0], "p1")
        self.assertEqual(ns.params[0][1], "val1")
        self.assertEqual(ns.params[1][0], "p2")
        self.assertEqual(ns.params[1][1], "val2")

    def test_player_class(self):
        try:
            from awstracer.player import TracePlayer
            from awstracer.tracer import Trace
            from awstracer.utils import json_dumps
        except Exception:
            self.fail("cannot import TracePlayer")
        with self.assertRaises(TypeError):
            with TracePlayer():
                pass
        inp = io.StringIO()
        inp.write("[]")
        inp.seek(0)
        with TracePlayer(inp) as tp:
            self.assertEqual(len(tp.traces), 0)

        # check missing arguments
        inp = io.StringIO()
        inp.write("[{}]")
        inp.seek(0)
        with self.assertRaises(ValueError):
            with TracePlayer(inp):
                pass

        t = Trace()
        t.start()
        t.set_input("bla", [])
        t.set_output("reqid", "bla", [])
        t.finish()
        inp = io.StringIO()
        inp.write("{}".format(json_dumps([t.to_dict()])))
        inp.seek(0)
        with TracePlayer(inp) as tp:
            self.assertEqual(len(tp.traces), 1)

    def test_player_methods_existence(self):
        try:
            from awstracer.player import TracePlayer
        except Exception:
            self.fail("cannot import TracePlayer")
        methods = ["play_trace", "play_single_trace", "get_shell_poc", "find_trace_connections", "find_connections", "prune_connections"]
        for m in methods:
            self.assertIn(m, dir(TracePlayer))

    def test_player_edges(self):
        try:
            from awstracer.player import Edge, MatchingNameAndValueEdge, MatchingNameEdge, MatchingValueEdge
        except Exception:
            self.fail("cannot import TracePlayer")
        self.assertIsInstance(MatchingNameAndValueEdge.__bases__[0], type(Edge))
        self.assertIsInstance(MatchingNameEdge.__bases__[0], type(Edge))
        self.assertIsInstance(MatchingValueEdge.__bases__[0], type(Edge))

    def test_player_play_trace(self):
        try:
            from awstracer.player import TracePlayer
            from awstracer.tracer import Trace
            from awstracer.utils import json_dumps
        except Exception:
            self.fail("cannot import TracePlayer")

        f = io.StringIO()
        with redirect_stdout(f):
            st = Trace()
            t = Trace()
            t.start()
            t.set_input("bla.wut", {"arg1": "val'\"`ue1"})
            t.set_output("reqid", "bla.wut", [])
            t.finish()
            inp = io.StringIO()
            inp.write("{}".format(json_dumps([t.to_dict()])))
            inp.seek(0)
            with TracePlayer(inp, prompt_color=False) as tp:
                tp.play_trace(st, dryrun=True, stop_on_error=True, sleep_delay=0)
        self.assertNotEqual(f.getvalue().find("(play) aws bla wut"), -1)
        self.assertNotEqual(f.getvalue().find("--arg1 'val'\"'\"'\"`ue1'"), -1)
