import yt_dlp
from datetime import datetime

class TikTokScraper:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }

    def get_data(self, username, max_posts=10, since_date=None):
        clean_username = username.replace('@', '').strip()
        url = f"https://www.tiktok.com/@{clean_username}"
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # --- PEMBERSIHAN DATA PROFIL ---
                # Mengambil baris pertama sebelum noise metadata MS4wLj...
                raw_name = info.get('uploader', clean_username)
                clean_full_name = raw_name.split('\n')[0].split('MS4w')[0].strip()
                
                raw_bio = info.get('description', 'No Bio')
                clean_bio = raw_bio.split('000FALSE')[0].split('MS4w')[0].strip()

                data = {
                    "metadata": {
                        "scraped_at": scraped_at,
                        "platform": "TikTok",
                        "status": "Success"
                    },
                    "profile_info": {
                        "userid": info.get('id', clean_username),
                        "username": clean_username,
                        "full_name": clean_full_name if clean_full_name else clean_username,
                        "bio": clean_bio if clean_bio else "No Bio",
                        "profile_pic": info.get('thumbnails', [{}])[0].get('url', '') if info.get('thumbnails') else '',
                        "followers": info.get('follower_count', 0),
                        "following": 0, 
                        "total_likes": info.get('like_count', 0),
                        "is_verified": False,
                        "engagement_rate": 0,
                        "scraped_at": scraped_at
                    },
                    "posts": []
                }

                # --- EXTRACTION DENGAN FILTER LIMIT & DATE ---
                entries = info.get('entries', [])
                valid_posts = []
                total_likes_for_er = 0
                
                for entry in entries:
                    # Filter 1: Limit Jumlah Postingan
                    if len(valid_posts) >= max_posts:
                        break
                        
                    post_ts = entry.get('timestamp')
                    if post_ts:
                        post_dt = datetime.fromtimestamp(post_ts)
                        
                        # Filter 2: Limit Berdasarkan Tanggal
                        if since_date and post_dt.date() < since_date:
                            continue
                            
                        likes = entry.get('like_count', 0) or 0
                        total_likes_for_er += likes
                        
                        valid_posts.append({
                            "username": clean_username,
                            "date": post_dt.strftime('%Y-%m-%d %H:%M:%S'),
                            "caption": entry.get('title', 'No Caption'),
                            "likes": likes,
                            "comments_count": entry.get('comment_count', 0),
                            "views": entry.get('view_count', 0),
                            "shares": entry.get('repost_count', 0),
                            "url": entry.get('webpage_url', ''),
                            "is_video": True,
                            "duration": entry.get('duration', 0)
                        })

                data["posts"] = valid_posts

                # Kalkulasi ER berdasarkan postingan yang berhasil difilter
                if data['profile_info']['followers'] > 0 and valid_posts:
                    avg_likes = total_likes_for_er / len(valid_posts)
                    er = (avg_likes / data['profile_info']['followers']) * 100
                    data['profile_info']['engagement_rate'] = round(er, 2)

                return data

        except Exception as e:
            return {
                "metadata": {"scraped_at": scraped_at, "platform": "TikTok", "status": "Error"},
                "error": str(e)
            }