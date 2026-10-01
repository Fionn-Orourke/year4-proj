import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from references.processor import identify, entries, next_id, record
class T(unittest.TestCase):
 def test_entries(self): self.assertEqual(entries('# Reference Inbox\n\nPaste one source entry per block.\n\nhttps://a.example\n\n10.1234/x'),['https://a.example','10.1234/x'])
 def test_doi(self): self.assertEqual(identify('doi: 10.1234/ABC.'),('doi','10.1234/ABC'))
 def test_url(self): self.assertEqual(identify('See https://example.org/doc.'),('url','https://example.org/doc'))
 def test_id(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/'REF-001.md').write_text(''); (p/'REF-009.md').write_text(''); self.assertEqual(next_id(p),'REF-010')
 def test_scope(self):
  t=record('REF-001',{'title':'T','url':'https://e','authors':[],'source_type':'web'},'2026-10-01'); self.assertIn('[Not assessed by Reference Automation V1]',t); self.assertIn('Accessed: 2026-10-01.',t)
if __name__=='__main__': unittest.main()
