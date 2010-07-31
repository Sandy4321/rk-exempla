import unittest
import tempfile
import atomic_file

import os
from os import path

class TestAtomicFile(unittest.TestCase):
    def setUp(self):
        self.directory = path.dirname(__file__)
        self.name = tempfile.mktemp()

    def tearDown(self):
        try:
            os.remove(self.name)
        except OSError:
            pass

    def testCreate(self):
        af = atomic_file.AtomicFile(name=self.name, dir=self.directory)
        self.assert_(not path.exists(self.name))
        self.assert_(path.exists(path.join(self.directory,
                                           af.tempfile.name)))
        af._swap()
        self.assert_(path.exists(self.name))
        self.assert_(not path.exists(path.join(self.directory,
                                           af.tempfile.name)))

    def testWrite(self):
        af = atomic_file.AtomicFile(name=self.name, dir=self.directory)
        text = 'THE TEXT\n'
        af.write(text)
        af._swap()
        self.assertEqual(file(self.name).read(), text)

    def testMoreWrite(self):
        af = atomic_file.AtomicFile(name=self.name, dir=self.directory)
        lines = ['THE TEXT', 'MORE TEXT', 'AGAIN!']
        for line in lines:
            print >> af, line
        af._swap()
        self.assertEqual(file(self.name).read(), '\n'.join(lines) + '\n')

    def testContext(self):
        with atomic_file.AtomicFile(name=self.name, dir=self.directory) as af:
            self.assert_(not path.exists(self.name))
            self.assert_(path.exists(path.join(self.directory,                                               af.tempfile.name)))
        self.assert_(path.exists(self.name))
        self.assert_(not path.exists(path.join(self.directory,
                                           af.tempfile.name)))