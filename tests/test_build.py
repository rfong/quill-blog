import os
import unittest

from build import get_relative_path

class TestBuildHelpers(unittest.TestCase):

  def test_get_relative_path(self):
    prefix = os.getcwd()
    relPath = "subdir/foo.bar"
    testPaths = [
      relPath,
      os.path.join(prefix, "src", relPath),
      os.path.join(prefix, "build", relPath),
    ]
    for path in testPaths:
      self.assertEqual(get_relative_path(path), relPath)
    self.assertEqual(
      get_relative_path(os.path.join(prefix, "src/build", relPath)),
      "build/"+relPath)
    self.assertEqual(
      get_relative_path(os.path.join(prefix, "build/src", relPath)),
      "src/"+relPath)


if __name__ == '__main__':
    unittest.main()
