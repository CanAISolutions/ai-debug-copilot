import unittest

from app.utils.context import parse_error_log, extract_context


class TestContextExtraction(unittest.TestCase):
    def test_parse_error_log(self):
        log = (
            'Traceback (most recent call last):\n'
            '  File "/home/user/project/main.py", line 10, in <module>\n'
            '    do_something()\n'
            '  File "utils/helper.py", line 5, in do_something\n'
            '    raise ValueError()\n'
            'main.py:25: some other error message\n'
        )
        refs = parse_error_log(log)
        # We expect two references: main.py line 10 and helper.py line 5 and main.py line 25
        self.assertIn(('main.py', 10), refs)
        self.assertIn(('helper.py', 5), refs)
        self.assertIn(('main.py', 25), refs)

    def test_extract_context(self):
        # Create a dummy file with 100 numbered lines
        lines = [f'line {i}' for i in range(1, 101)]
        content = "\n".join(lines)
        decoded_files = [{'filename': 'main.py', 'content': content}]
        refs = [('main.py', 50)]
        snippets = extract_context(decoded_files, refs, context_lines=2)
        self.assertEqual(len(snippets), 1)
        snippet = snippets[0]
        # Lines 48-52 should be included
        self.assertEqual(snippet['start'], 48)
        self.assertEqual(snippet['end'], 52)
        snippet_lines = snippet['snippet'].splitlines()
        self.assertEqual(len(snippet_lines), 5)
        # Check that the first and last lines match expected
        self.assertEqual(snippet_lines[0], 'line 48')
        self.assertEqual(snippet_lines[-1], 'line 52')

    def test_extract_context_unknown_file(self):
        decoded_files = [{'filename': 'main.py', 'content': 'print("hi")'}]
        refs = [('other.py', 1)]
        snippets = extract_context(decoded_files, refs)
        self.assertEqual(snippets, [])


if __name__ == '__main__':
    unittest.main()