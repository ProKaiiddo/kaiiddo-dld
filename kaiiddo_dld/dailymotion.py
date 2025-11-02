import re
import json
import requests
import time
import uuid
from datetime import datetime

class BaseDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': '*/*',
        })
    
    def fetch_info(self, url):
        raise NotImplementedError("Subclasses must implement this method")

class DailymotionDL(BaseDownloader):
    def __init__(self):
        super().__init__()
        self.graphql_url = "https://graphql.api.dailymotion.com/"
        self.token_url = "https://graphql.api.dailymotion.com/oauth/token"
        self.access_token = None
        self.token_expiry = None
        
        # Dailymotion API credentials (these are public/client-side)
        self.client_id = "f1a362d288c1b98099c7"
        self.client_secret = "eea605b96e01c796ff369935357eca920c5da4c5"
        self.traffic_segment = "534176"
        self.visitor_id = "504342c6-2243-43bf-b1d5-e779c385e399"
    
    def generate_visitor_id(self):
        """Generate a random visitor ID if needed"""
        return str(uuid.uuid4())
    
    def get_access_token(self):
        """Dynamically fetch access token from Dailymotion"""
        # Check if we have a valid token
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            return self.access_token
        
        # Prepare token request headers
        token_headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.dailymotion.com',
            'Referer': 'https://www.dailymotion.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Prepare token request data
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'traffic_segment': self.traffic_segment,
            'visitor_id': self.visitor_id
        }
        
        try:
            response = self.session.post(
                self.token_url,
                headers=token_headers,
                data=token_data
            )
            response.raise_for_status()
            
            token_info = response.json()
            self.access_token = token_info.get('access_token')
            
            # Set token expiry (subtract 60 seconds for safety margin)
            expires_in = token_info.get('expires_in', 35713)
            self.token_expiry = time.time() + expires_in - 60
            
            print(f"✅ Successfully fetched new access token (expires in {expires_in}s)")
            return self.access_token
            
        except Exception as e:
            print(f"❌ Failed to fetch access token: {e}")
            return None
    
    def setup_headers(self):
        """Setup headers with dynamic Bearer token"""
        token = self.get_access_token()
        if not token:
            raise Exception("Failed to obtain access token")
        
        self.session.headers.update({
            'Accept': '*/*, */*',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json, application/json',
            'Origin': 'https://www.dailymotion.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.dailymotion.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'X-DM-AppInfo-Id': 'com.dailymotion.neon',
            'X-DM-AppInfo-Type': 'website',
            'X-DM-AppInfo-Version': 'v2025-10-28T10:19:15.606Z',
            'X-DM-Neon-SSR': '0',
            'X-DM-Preferred-Country': 'in',
            'accept-language': 'en-US',
            'authorization': f'Bearer {token}',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    def extract_video_id(self, url):
        match = re.search(r'/video/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None
    
    def format_duration(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def format_date(self, date_string):
        """Format date string to readable format"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return date_string
    
    def display_video_info(self, data):
        """Extract and display video information in terminal"""
        if 'data' not in data or 'video' not in data['data']:
            print("❌ No video data found in response")
            return
        
        video = data['data']['video']
        
        print("\n" + "="*60)
        print("🎬 DAILYMOTION VIDEO INFORMATION")
        print("="*60)
        
        # Basic Information
        print(f"📹 ID: {video.get('id', 'N/A')}")
        print(f"🔗 XID: {video.get('xid', 'N/A')}")
        print(f"📺 Title: {video.get('title', 'N/A')}")
        print(f"⏱️ Duration: {self.format_duration(video.get('duration', 0))} ({video.get('duration', 0)} seconds)")
        print(f"🔄 Status: {video.get('status', 'N/A')}")
        print(f"📅 Created: {self.format_date(video.get('createdAt', 'N/A'))}")
        
        # Quality Information
        print(f"🎯 Best Quality: {video.get('bestAvailableQuality', 'N/A')}")
        print(f"📐 Resolution: {video.get('videoWidth', 'N/A')}x{video.get('videoHeight', 'N/A')}")
        print(f"📊 Aspect Ratio: {video.get('aspectRatio', 'N/A')}")
        
        # Thumbnails
        print("\n🖼️ THUMBNAILS:")
        thumbnails = [
            ('x60', video.get('thumbnailx60')),
            ('x120', video.get('thumbnailx120')),
            ('x240', video.get('thumbnailx240')),
            ('x360', video.get('thumbnailx360')),
            ('x480', video.get('thumbnailx480')),
            ('x720', video.get('thumbnailx720')),
            ('x1080', video.get('thumbnailx1080'))
        ]
        
        for size, url in thumbnails:
            if url:
                print(f"  {size}: {url}")
        
        # Channel Information
        if 'channel' in video:
            channel = video['channel']
            print(f"\n👤 CHANNEL:")
            print(f"  📛 Name: {channel.get('displayName', 'N/A')}")
            print(f"  🔖 Username: {channel.get('name', 'N/A')}")
            print(f"  🆔 Channel ID: {channel.get('xid', 'N/A')}")
            print(f"  🧩 Account Type: {channel.get('accountType', 'N/A')}")

            
            # Channel Stats
            if 'stats' in channel:
                stats = channel['stats']
                if 'views' in stats:
                    print(f"  👁️ Channel Views: {stats['views'].get('total', 0):,}")
                if 'followers' in stats:
                    print(f"  ❤️ Followers: {stats['followers'].get('total', 0):,}")
                if 'videos' in stats:
                    print(f"  📹 Videos: {stats['videos'].get('total', 0):,}")
        
        # Video Statistics
        if 'stats' in video and 'views' in video['stats']:
            print(f"\n📊 VIDEO STATS:")
            print(f"  👁️ Total Views: {video['stats']['views'].get('total', 0):,}")
        
        # Engagement Metrics
        if 'metrics' in video and 'engagement' in video['metrics']:
            engagement = video['metrics']['engagement']
            if 'likes' in engagement and 'edges' in engagement['likes']:
                likes_edge = engagement['likes']['edges']
                if likes_edge and 'node' in likes_edge[0]:
                    print(f"  👍 Likes: {likes_edge[0]['node'].get('total', 0):,}")
        
        # Additional Info
        print(f"\nℹ️ ADDITIONAL INFO:")
        print(f"  📝 Description: {video.get('description', 'No description')}")
        print(f"  🏷️ Category: {video.get('category', 'N/A')}")
        print(f"  🌐 Language: {video.get('language', {}).get('codeAlpha2', 'N/A')}")
        print(f"  📍 Country: {video.get('channel', {}).get('country', {}).get('codeAlpha2', 'N/A')}")
        print(f"  🔞 Explicit: {'Yes' if video.get('isExplicit') else 'No'}")
        print(f"  👶 For Kids: {'Yes' if video.get('isCreatedForKids') else 'No'}")
        print(f"  🔒 Private: {'Yes' if video.get('isPrivate') else 'No'}")
        print(f"  📢 Ads Enabled: {'Yes' if video.get('canDisplayAds') else 'No'}")
        
        print("="*60)
    
    def fetch_info(self, url):
        video_id = self.extract_video_id(url)
        if not video_id:
            return {"error": "Invalid Dailymotion URL"}
        
        # Get fresh token and setup headers
        self.setup_headers()
        
        # Updated GraphQL query for WATCHING_VIDEO
        query = '''
fragment VIDEO_FRAGMENT on Video {
  id
  xid
  isPublished
  duration
  title
  description
  thumbnailx60: thumbnailURL(size: "x60")
  thumbnailx120: thumbnailURL(size: "x120")
  thumbnailx240: thumbnailURL(size: "x240")
  thumbnailx360: thumbnailURL(size: "x360")
  thumbnailx480: thumbnailURL(size: "x480")
  thumbnailx720: thumbnailURL(size: "x720")
  thumbnailx1080: thumbnailURL(size: "x1080")
  aspectRatio
  sharingURLs {
    edges {
      node {
        id
        serviceName
        url
        __typename
      }
      __typename
    }
    __typename
  }
  category
  categories(filter: {category: {eq: CONTENT_CATEGORY}}) {
    edges {
      node {
        id
        name
        slug
        __typename
      }
      __typename
    }
    __typename
  }
  iab_categories: categories(
    filter: {category: {eq: IAB_CATEGORY}, percentage: {gte: 70}}
  ) {
    edges {
      node {
        id
        slug
        __typename
      }
      __typename
    }
    __typename
  }
  bestAvailableQuality
  createdAt
  viewerEngagement {
    id
    liked
    favorited
    __typename
  }
  metrics {
    id
    engagement {
      id
      likes(filter: {rating: {eq: STAR_STRUCK}}) {
        edges {
          node {
            id
            total
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
  isPrivate
  isCreatedForKids
  isExplicit
  canDisplayAds
  videoWidth: width
  videoHeight: height
  status
  hashtags {
    edges {
      node {
        id
        name
        __typename
      }
      __typename
    }
    __typename
  }
  stats {
    id
    views {
      id
      total
      __typename
    }
    __typename
  }
  channel {
    __typename
    id
    xid
    name
    displayName
    isArtist
    logoURLx25: logoURL(size: "x25")
    logoURL(size: "x60")
    isFollowed
    accountType
    coverURLx375: coverURL(size: "x375")
    stats {
      id
      views {
        id
        total
        __typename
      }
      followers {
        id
        total
        __typename
      }
      videos {
        id
        total
        __typename
      }
      __typename
    }
    country {
      id
      codeAlpha2
      __typename
    }
    organization @skip(if: $isSEO) {
      id
      xid
      owner {
        id
        xid
        __typename
      }
      __typename
    }
  }
  language {
    id
    codeAlpha2
    __typename
  }
  tags {
    edges {
      node {
        id
        label
        __typename
      }
      __typename
    }
    __typename
  }
  moderation {
    id
    reviewedAt
    __typename
  }
  geoblockedCountries {
    id
    allowed
    denied
    __typename
  }
  transcript {
    edges {
      node {
        id
        timecode
        text
        __typename
      }
      __typename
    }
    __typename
  }
  chapters(first: 1000) {
    edges {
      node {
        timecode
        title
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}

fragment LIVE_FRAGMENT on Live {
  id
  xid
  startAt
  endAt
  isPublished
  title
  description
  thumbnailx60: thumbnailURL(size: "x60")
  thumbnailx120: thumbnailURL(size: "x120")
  thumbnailx240: thumbnailURL(size: "x240")
  thumbnailx360: thumbnailURL(size: "x360")
  thumbnailx480: thumbnailURL(size: "x480")
  thumbnailx720: thumbnailURL(size: "x720")
  thumbnailx1080: thumbnailURL(size: "x1080")
  aspectRatio
  category
  createdAt
  viewerEngagement {
    id
    liked
    favorited
    __typename
  }
  metrics {
    id
    engagement {
      id
      bookmarks(filter: {bookmark: {eq: LIKE}}) {
        edges {
          node {
            id
            total
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
  isPrivate
  isExplicit
  isCreatedForKids
  bestAvailableQuality
  canDisplayAds
  videoWidth: width
  videoHeight: height
  stats {
    id
    views {
      id
      total
      __typename
    }
    __typename
  }
  channel {
    __typename
    id
    xid
    name
    displayName
    isArtist
    logoURLx25: logoURL(size: "x25")
    logoURL(size: "x60")
    isFollowed
    accountType
    coverURLx375: coverURL(size: "x375")
    stats {
      id
      views {
        id
        total
        __typename
      }
      followers {
        id
        total
        __typename
      }
      videos {
        id
        total
        __typename
      }
      __typename
    }
    country {
      id
      codeAlpha2
      __typename
    }
    organization @skip(if: $isSEO) {
      id
      xid
      owner {
        id
        xid
        __typename
      }
      __typename
    }
  }
  language {
    id
    codeAlpha2
    __typename
  }
  tags {
    edges {
      node {
        id
        label
        __typename
      }
      __typename
    }
    __typename
  }
  moderation {
    id
    reviewedAt
    __typename
  }
  geoblockedCountries {
    id
    allowed
    denied
    __typename
  }
  __typename
}

query WATCHING_VIDEO($xid: String!, $isSEO: Boolean!) {
  video: media(xid: $xid) {
    __typename
    ... on Video {
      id
      ...VIDEO_FRAGMENT
      __typename
    }
    ... on Live {
      id
      ...LIVE_FRAGMENT
      __typename
    }
  }
}
'''
        
        payload = {
            "operationName": "WATCHING_VIDEO",
            "variables": {
                "xid": video_id,
                "isSEO": False
            },
            "query": query
        }
        
        try:
            print(f"🔍 Fetching info for video: {video_id}")
            response = self.session.post(self.graphql_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print("✅ Successfully fetched video info")
            
            # Display formatted information
            self.display_video_info(result)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
