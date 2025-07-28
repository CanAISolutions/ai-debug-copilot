import unittest

from app.utils.vector_store import embed_files, query_snippets


class TestVectorStore(unittest.TestCase):
    def setUp(self):
        # Reset vector store by embedding empty list
        embed_files([])

    def test_query_without_embedding(self):
        # Should return empty list when no embeddings exist
        snippets = query_snippets('anything', k=5)
        self.assertEqual(snippets, [])

    def test_embed_and_query(self):
        # Embed two simple documents
        files = [
            {'filename': 'a.py', 'content': 'alpha beta gamma'},
            {'filename': 'b.py', 'content': 'beta delta'},
            {'filename': 'c.py', 'content': ''},  # empty content should be ignored
        ]
        embed_files(files)
        # Query for a term present in both documents; expect at most k snippets
        snippets = query_snippets('beta', k=2)
        self.assertTrue(len(snippets) <= 2)
        # Each snippet should be a substring of one of the non-empty contents
        for snip in snippets:
            self.assertTrue(snip in ['alpha beta gamma', 'beta delta'])

    def test_query_limited_k(self):
        files = [
            {'filename': f'file{i}.py', 'content': f'content {i}'} for i in range(10)
        ]
        embed_files(files)
        snippets = query_snippets('content', k=3)
        self.assertEqual(len(snippets), 3)


if __name__ == '__main__':
    unittest.main()