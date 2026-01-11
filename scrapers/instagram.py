import instaloader
from datetime import datetime

class InstagramScraper:
    def __init__(self):
        # User-agent untuk menghindari blokir
        self.L = instaloader.Instaloader(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def get_detailed_data(self, username, max_posts=10, since_date=None):
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. Profile Umum
            data = {
                "metadata": {
                    "scraped_at": scraped_at,
                    "total_posts_on_profile": profile.mediacount,
                    "platform": "Instagram" # Memastikan metadata platform ada
                },
                "profile_info": {
                    "userid": profile.userid,
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "bio": profile.biography,
                    "profile_pic": profile.profile_pic_url,
                    "is_business": profile.is_business_account,
                    "business_category": profile.business_category_name,
                    "external_url": profile.external_url,
                    "followers": profile.followers,
                    "following": profile.followees,
                    "is_verified": profile.is_verified,
                    "scraped_at": scraped_at
                },
                "posts": []
            }

            total_likes = 0
            total_comments = 0

            # 2. Data Postingan dengan Filter
            for post in profile.get_posts():
                # Filter 1: Batas Jumlah Postingan
                if len(data["posts"]) >= max_posts:
                    break
                
                # Filter 2: Batas Tanggal (Since Date)
                if since_date and post.date_utc.date() < since_date:
                    # Instaloader mengambil post dari yang terbaru, 
                    # jadi jika sudah melewati since_date, kita bisa berhenti (break)
                    break

                total_likes += post.likes
                total_comments += post.comments
                
                post_item = {
                    "username": username,
                    "date": post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                    "caption": post.caption,
                    "likes": post.likes,
                    "comments_count": post.comments,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "hashtags": post.caption_hashtags,
                    "mentions": post.caption_mentions,
                    "is_video": post.is_video,
                    "typename": post.typename,
                    "video_view_count": post.video_view_count if post.is_video else 0,
                    "location": post.location.name if post.location else None,
                    "tagged_users": post.tagged_users
                }
                data["posts"].append(post_item)

            # 3. Analytics (Engagement Rate) berdasarkan data yang difilter
            post_count = len(data["posts"])
            if post_count > 0 and profile.followers > 0:
                avg_eng = (total_likes + total_comments) / post_count
                er = (avg_eng / profile.followers) * 100
                data["profile_info"]["engagement_rate"] = round(er, 2)
                data["profile_info"]["avg_likes"] = round(total_likes / post_count, 1)
            else:
                data["profile_info"]["engagement_rate"] = 0
                data["profile_info"]["avg_likes"] = 0

            return data
        except Exception as e:
            return {"error": str(e), "metadata": {"status": "Error", "platform": "Instagram"}}