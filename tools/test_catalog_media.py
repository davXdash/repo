import io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from catalog_media import download_thumbnail,identity
class ImageCacheTests(unittest.TestCase):
 def test_agent_links_share_product_identity(self):
  self.assertEqual(identity('https://litbuy.com/product/weidian/123?inviteCode=x'),'weidian:123')
  self.assertEqual(identity('https://www.usfans.com/product/3/123?ref=y'),'weidian:123')
  self.assertNotEqual(identity('https://cnfans.com/product?platform=TAOBAO&id=123'),'weidian:123')
 def test_thumbnail_is_local_and_survives_expired_remote_url(self):
  data=io.BytesIO();Image.new('RGB',(900,600),'white').save(data,'PNG')
  class Response(io.BytesIO):
   def __enter__(self):return self
   def __exit__(self,*args):self.close()
  with tempfile.TemporaryDirectory() as directory:
   p={'url':'https://weidian.com/item.html?itemID=123','image':'https://docs.google.com/sheets-images-rt/fresh'}
   with patch('urllib.request.urlopen',return_value=Response(data.getvalue())) as request:
    result=download_thumbnail(p,Path(directory));self.assertTrue(result.startswith('imports/media/'));self.assertEqual(request.call_count,1)
   file=Path(directory)/result.removeprefix('imports/');self.assertTrue(file.exists())
   with Image.open(file) as im:self.assertLessEqual(max(im.size),480)
   with patch('urllib.request.urlopen',side_effect=Exception('expired')) as request:
    self.assertEqual(download_thumbnail(p,Path(directory)),result);request.assert_not_called()
if __name__=='__main__':unittest.main()
