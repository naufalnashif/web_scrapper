import requests
from scrapers.base import BaseScraper

class ShopeeScraper(BaseScraper):
    def get_data(self, sku: str):
        try:
            # sku format -> shopid:itemid
            shopid, itemid = sku.split(':')
            url = f"https://shopee.co.id/api/v4/item/get?itemid={itemid}&shopid={shopid}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Referer": f"https://shopee.co.id/product/{shopid}/{itemid}"
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
            item = data['data']
            
            # Normalisasi agar Dashboard Instagram tetap jalan
            return {
                "platform": "Shopee",
                "profile_info": {
                    "userid": item['itemid'],
                    "username": item['name'], # Nama Produk sebagai Username
                    "full_name": f"Shop ID: {item['shopid']}",
                    "bio": item['description'][:500],
                    "profile_pic": f"https://down-id.img.sgrid.id/file/{item['image']}",
                    "followers": item['liked_count'], # Mapping: Likes -> Followers
                    "following": item['stock'],       # Mapping: Stock -> Following
                },
                "posts": [
                    {
                        "date": "PRICE", 
                        "caption": f"Price: Rp {item['price']/100000}", 
                        "likes": item['view_count'], 
                        "comments_count": item['cmt_count']
                    }
                ]
            }
        except Exception as e:
            return {"error": f"Shopee Error: {str(e)}"}