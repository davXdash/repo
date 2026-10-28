import unittest
from import_trellox import records
class TrelloxTest(unittest.TestCase):
 def test_keeps_links_images_prices_and_distinct_offers(self):
  url='https://www.pikobuy.com/product/detail?productUrl=https%3A%2F%2Fweidian.com%2Fitem.html%3FitemID%3D123&invitedCode=Trellox'
  rows=records([dict(id=12,key='shoes-12',type='shoe',name='Adidas Samba',imageUrl='/images/shoes/test.png',bestBatchPrice='22.5',bestBudgetPrice='12',bestBatchLink=url,budgetBatchLink=url+'&budget=1')],dict(id='trellox'))
  self.assertEqual(len(rows),2);self.assertEqual(rows[0]['url'],url);self.assertEqual(rows[0]['currency'],'USD');self.assertEqual(rows[0]['amount'],22.5);self.assertEqual(rows[0]['image'],'https://trellox.de/images/shoes/test.png');self.assertEqual(rows[0]['sourceUrl'],'https://trellox.de/shoes/12');self.assertNotEqual(rows[0]['id'],rows[1]['id'])
if __name__=='__main__':unittest.main()
