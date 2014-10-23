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


    # This might need to be increased if the test system is under heavy load.
    NOTIFIER_WAIT_SECONDS = 1


    class FileSystemNotifierTestCase(TestCase):

        def setUp(self):
            self.queue = Queue()
            self.tmp_dir = tempfile.mkdtemp()
            self.notifier = fsnotify.FileSystemNotifier(self.queue)
            self.notifier.start()

        def tearDown(self):
            self.notifier.stop()

        def get_event(self):
            self._last_event = self.queue.get(timeout=NOTIFIER_WAIT_SECONDS)
            return self._last_event

        def assertNoEvent(self):
            try:
                self.assertRaises(Empty, self.get_event)
            except Exception:
                print("Unexpected event: {}".format(self._last_event))
                raise

        def test_notify(self, auto_add=False):
            # Create a subdirectory prior to watching.
            dir_path = os.path.join(self.tmp_dir, "existing_dir")
            os.mkdir(dir_path)

            self.notifier.add_watch(self.tmp_dir, pyinotify.ALL_EVENTS,
                                    rec=True, auto_add=auto_add)
            # rec=True causes the following for the existing directory.
            for mask in (pyinotify.IN_OPEN, pyinotify.IN_CLOSE_NOWRITE):
                event = self.get_event()
                msg = "Unexpected event: {}".format(str(event))
                self.assertEqual(dir_path, event.pathname, msg=msg)
                self.assertEqual(mask | pyinotify.IN_ISDIR, event.mask,
                                 msg=msg)
                self.assertTrue(event.dir, msg=msg)
            self.assertNoEvent()

            # Create a new subdirectory.
            new_dir_path = os.path.join(self.tmp_dir, "new_dir")
            os.mkdir(new_dir_path)
            event = self.get_event()
            msg = "Unexpected event: {}".format(str(event))
            self.assertEqual(new_dir_path, event.pathname, msg=msg)
            self.assertEqual(pyinotify.IN_CREATE | pyinotify.IN_ISDIR,
                             event.mask, msg=msg)
            self.assertTrue(event.dir, msg=msg)
            if auto_add:
                # auto_add causes new directories to be opened twice.
                for mask in ((pyinotify.IN_OPEN,) * 2 +
                             (pyinotify.IN_CLOSE_NOWRITE,) * 2):
                    event = self.get_event()
                    msg = "Unexpected event: {}".format(str(event))
                    self.assertEqual(new_dir_path, event.pathname, msg=msg)
                    self.assertEqual(mask | pyinotify.IN_ISDIR, event.mask,
                                     msg=msg)
                    self.assertTrue(event.dir, msg=msg)
            self.assertNoEvent()

            # Create a file under the preexisting then the new directory.
            for dir_ in (dir_path, new_dir_path):
                file_path = os.path.join(dir_, "new_file")
                with open(file_path, 'w') as f:
                    f.write("some stuff")
                if not auto_add and dir_ == new_dir_path:
                    self.assertNoEvent()
                    continue
                for mask in (pyinotify.IN_CREATE, pyinotify.IN_OPEN,
                             pyinotify.IN_MODIFY, pyinotify.IN_CLOSE_WRITE):
                    event = self.get_event()
                    msg = "Unexpected event: {}".format(str(event))
                    self.assertEqual(file_path, event.pathname, msg=msg)
                    self.assertEqual(mask, event.mask, msg=msg)
                    self.assertFalse(event.dir, msg=msg)
            self.assertNoEvent()

        def test_notify_auto_add(self):
            self.test_notify(auto_add=True)
