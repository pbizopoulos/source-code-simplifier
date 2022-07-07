from importlib import import_module
from os import environ, listdir
from os.path import join
from source_code_simplifier import source_code_simplifier
import unittest


class Tests(unittest.TestCase):

    def setUp(self):
        environ['PYTHONBREAKPOINT'] = '0'
        self.test_file_name_list = listdir('tests')
        self.test_file_name_list.remove('__init__.py')
        if '__pycache__' in self.test_file_name_list:
            self.test_file_name_list.remove('__pycache__')

    def test_source(self):
        for test_file_name in self.test_file_name_list:
            with self.subTest(test_file_name=test_file_name):
                module = import_module(f'tests.{test_file_name[:-3]}')
                module.main()

    def test_source_code_simplifier(self):
        for test_file_name in self.test_file_name_list:
            with self.subTest(test_file_name=test_file_name):
                if test_file_name.startswith('forbid_'):
                    with open(join('tests', test_file_name)) as file:
                        self.assertRaises(AssertionError, source_code_simplifier, file)
                elif test_file_name.endswith('_bad.py'):
                    with open(join('tests', test_file_name)) as file:
                        code_output = source_code_simplifier(file)
                    with open(join('tests', test_file_name.replace('bad', 'good'))) as file:
                        code_output_good = file.read()
                    self.assertEqual(code_output, code_output_good)


if __name__ == '__main__':
    unittest.main()
