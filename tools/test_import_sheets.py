import tempfile,unittest
from pathlib import Path
import openpyxl
from import_sheets import parse_xlsx,parse_html_sheet,number_value
class CatalogImportTests(unittest.TestCase):
 def test_readable_view_preserves_merged_cells_links_image_and_price(self):
  html='''<table><tr><th>1</th><td rowspan="2">Golden Goose Super-Star</td><td rowspan="2"><img src="https://example.com/shoe.jpg"></td><td rowspan="2"><a href="https://shop.example/product/1">LINK</a></td><td>¥1.250,00</td></tr><tr><th>2</th><td>$180.00</td></tr></table>'''
  products,report=parse_html_sheet(html,{'id':'x'},'123')
  self.assertEqual(len(products),1);p=products[0]
  self.assertEqual(p['name'],'Golden Goose Super-Star');self.assertEqual(p['amount'],1250);self.assertEqual(p['currency'],'CNY');self.assertEqual(p['image'],'https://example.com/shoe.jpg');self.assertEqual(p['url'],'https://shop.example/product/1')
 def test_xlsx_hyperlink_and_unknown_currency(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td);w=openpyxl.Workbook();s=w.active
   s.append(['Autry Shoes','LINK',73.85]);s['B1'].hyperlink='https://shop.example/autry'
   s.append(['Birkenstock Boston','LINK','28 €']);s['B2'].hyperlink='https://shop.example/boston'
   w.save(td/'test.xlsx');products,report=parse_xlsx(td/'test.xlsx',{'id':'test'},td)
   self.assertEqual(len(products),2);self.assertIsNone(products[0]['currency']);self.assertIsNone(products[0]['euro']);self.assertEqual(products[1]['euro'],28)
 def test_number_formats(self):
  self.assertEqual(number_value('1,250.00'),1250);self.assertEqual(number_value('1.250,00'),1250);self.assertEqual(number_value('32,98'),32.98)
if __name__=='__main__':unittest.main()
