import os
import unittest

from build import get_relative_path, SRC_DIR, BUILD_DIR

class TestBuildHelpers(unittest.TestCase):

  def test_get_relative_path(self):
    prefix = os.getcwd()
    relPath = "subdir/foo.bar"
    testPaths = [
      relPath,
      os.path.join(prefix, SRC_DIR, relPath),
      os.path.join(prefix, BUILD_DIR, relPath),
    ]
    for path in testPaths:
      self.assertEqual(get_relative_path(path), relPath)
    self.assertEqual(
      get_relative_path(os.path.join(
        prefix, SRC_DIR + "/" + BUILD_DIR, relPath)),
      BUILD_DIR + "/" + relPath)
    self.assertEqual(
      get_relative_path(os.path.join(
        prefix, BUILD_DIR + "/" + SRC_DIR, relPath)),
      SRC_DIR + "/" + relPath)


if __name__ == '__main__':
    unittest.main()
