import unittest
from import_asmr import records
class ASMRTest(unittest.TestCase):
 def test_keeps_all_source_values(self):
  item=dict(id='a1',name='Golden Goose',price=28.5,link='https://litbuy.com/product/weidian/123?inviteCode=ASMRHAULER',image='/api/uploads/a.webp',category='Shoes')
  rows=records([item,item,{**item,'id':'broken','link':''}],{'id':'asmr-web'})
  self.assertEqual(len(rows),1);p=rows[0];self.assertEqual(p['url'],item['link']);self.assertEqual(p['currency'],'USD');self.assertEqual(p['amount'],28.5);self.assertEqual(p['image'],'https://asmrhauler.com/api/uploads/a.webp');self.assertIn('#product-a1',p['sourceUrl']);self.assertIn('qc-finder?link=',p['qcUrl'])
if __name__=='__main__':unittest.main()
