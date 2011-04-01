#!/usr/bin/python
import os                             
import sys
import unittest

import daemon
import nose
import nose.config
import nose.core

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'yagi', '__init__.py')):
    sys.path.insert(0, possible_topdir)

if __name__ == '__main__':
    test_path = os.path.abspath(os.path.join('tests', 'unit'))
    c = nose.config.Config(stream=sys.stdout,
                      env=os.environ,
                      verbosity=3,
                      workingDir=test_path)
    nose.core.run(config=c, argv=sys.argv)
