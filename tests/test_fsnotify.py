# -*- coding: utf-8 -*-
"""Tests for pyneric.fsnotify"""

try:
    from pyneric import fsnotify
except ImportError:
    import warnings
    warnings.warn("The tests for pyneric.fsnotify will not be run since the "
                  "module is not functional in the current Python environment."
                  "  Install pyinotify >= 0.9 to enable these tests.",
                  ImportWarning)
else:
    import sys
    if sys.version_info[0] < 3:
        from Queue import Empty, Queue
    else:
        from queue import Empty, Queue
    import operator
    import os
    import tempfile
    from unittest import TestCase

    import pyinotify


    # The number of seconds before determining that all events are received.
    # This might need to be increased if the test system is under heavy load.
    NOTIFIER_WAIT_SECONDS = 2


    class FileSystemNotifierTestCase(TestCase):

        def setUp(self):
            self.queue = Queue()
            self.tmp_dir = tempfile.mkdtemp()
            self.notifier = fsnotify.FileSystemNotifier(self.queue)
            self.notifier.start()

        def tearDown(self):
            self.notifier.stop()

        def get_events(self):
            while True:
                try:
                    yield self.queue.get(timeout=NOTIFIER_WAIT_SECONDS)
                except Empty:
                    return

        def test_notify(self, auto_add=False):
            # Create a subdirectory prior to watching.
            dir_path = os.path.join(self.tmp_dir, "existing_dir")
            os.mkdir(dir_path)

            self.notifier.add_watch(self.tmp_dir, pyinotify.ALL_EVENTS,
                                    rec=True, auto_add=auto_add)
            # rec=True causes the following for the existing directory.
            masks = [pyinotify.IN_OPEN, pyinotify.IN_ACCESS,
                     pyinotify.IN_CLOSE_NOWRITE]
            expected = [(dir_path, x | pyinotify.IN_ISDIR) for x in masks]
            actual = [(x.pathname, x.mask) for x in self.get_events()]
            self.assertEqual(expected, actual)

            # Create a new subdirectory.
            new_dir_path = os.path.join(self.tmp_dir, "new_dir")
            os.mkdir(new_dir_path)
            masks = [pyinotify.IN_CREATE]
            if auto_add:
                # auto_add causes new directories to be opened twice.
                masks.extend([pyinotify.IN_OPEN] * 2 +
                             [pyinotify.IN_ACCESS] * 4 +
                             [pyinotify.IN_CLOSE_NOWRITE] * 2)
            expected = [(new_dir_path, x | pyinotify.IN_ISDIR) for x in masks]
            actual = [(x.pathname, x.mask) for x in self.get_events()]
            self.assertEqual(expected, actual)

            # Create a file under the preexisting then the new directory.
            for dir_ in (dir_path, new_dir_path):
                file_path = os.path.join(dir_, "new_file")
                with open(file_path, 'w') as f:
                    f.write("some stuff")
                masks = []
                if auto_add or dir_ == dir_path:
                    masks.extend([pyinotify.IN_CREATE, pyinotify.IN_OPEN,
                                  pyinotify.IN_MODIFY,
                                  pyinotify.IN_CLOSE_WRITE])
                expected = [(file_path, x) for x in masks]
                actual = [(x.pathname, x.mask) for x in self.get_events()]
                self.assertEqual(expected, actual)

            # No more events are expected.
            events = list(self.get_events())
            if events:
                msg = "Unexpected events: {}".format([str(x) for x in events])
                self.assertTrue(False, msg=msg)

        def test_notify_auto_add(self):
            self.test_notify(auto_add=True)

        def test_invalid_attribute(self):
            self.assertRaises(AttributeError, getattr, self.notifier, 'x')
