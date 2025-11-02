# kaiiddo-dld

[![PyPI version](https://badge.fury.io/py/kaiiddo-dld.svg)](https://pypi.org/project/kaiiddo-dld/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/kaiiddo-dld.svg)](https://pypi.org/project/kaiiddo-dld/)

A Python package for downloading and fetching information from social media platforms. Currently supports Dailymotion, with extensible architecture for adding more platforms.

## Features

- **Dailymotion Support**: Fetch detailed video information including metadata, thumbnails, channel info, and statistics.
- **Extensible Design**: Built with a base downloader class to easily add support for other social media platforms.
- **Rich Information Display**: Formatted terminal output with emojis and structured data.
- **GraphQL API Integration**: Uses Dailymotion's GraphQL API for efficient data retrieval.
- **Automatic Token Management**: Handles OAuth token fetching and renewal automatically.

## Installation

Install the package via pip:

```bash
pip install kaiiddo-dld
```

### Requirements

- Python >= 3.6
- requests >= 2.25.0

## Usage

### Basic Example

```python
from kaiiddo_dld import DailymotionDL

# Create a downloader instance
downloader = DailymotionDL()

# Fetch video information
url = "https://www.dailymotion.com/video/x8m8z5z"
result = downloader.fetch_info(url)

# The result is a dictionary containing all video data
# Information is also displayed in the terminal automatically
```

### Output Example

When you run the fetch_info method, you'll see formatted output like:

```
============================================================
🎬 DAILYMOTION VIDEO INFORMATION
============================================================
📹 ID: x8m8z5z
🔗 XID: x8m8z5z
📺 Title: Sample Video Title
⏱️ Duration: 05:23 (323 seconds)
🔄 Status: published
📅 Created: 2023-10-01 12:00:00
🎯 Best Quality: 1080p
📐 Resolution: 1920x1080
📊 Aspect Ratio: 1.7778

🖼️ THUMBNAILS:
  x60: https://s1.dmcdn.net/v/...
  x120: https://s1.dmcdn.net/v/...
  ...

👤 CHANNEL:
  📛 Name: Channel Name
  🔖 Username: channel_username
  🆔 Channel ID: x12345
  🧩 Account Type: user
  👁️ Channel Views: 1,234,567
  ❤️ Followers: 12,345
  📹 Videos: 67

📊 VIDEO STATS:
  👁️ Total Views: 89,012
  👍 Likes: 1,234

ℹ️ ADDITIONAL INFO:
  📝 Description: Video description here...
  🏷️ Category: entertainment
  🌐 Language: en
  📍 Country: US
  🔞 Explicit: No
  👶 For Kids: No
  🔒 Private: No
  📢 Ads Enabled: Yes
============================================================
```

## API Reference

### BaseDownloader

Base class for all social media downloaders.

- `__init__()`: Initializes a requests session with default headers.
- `fetch_info(url)`: Abstract method to be implemented by subclasses.

### DailymotionDL

Downloader for Dailymotion videos.

- `__init__()`: Initializes with Dailymotion API credentials and endpoints.
- `fetch_info(url)`: Fetches and displays video information for a given Dailymotion URL.
- `extract_video_id(url)`: Extracts video ID from Dailymotion URL.
- `get_access_token()`: Fetches OAuth access token from Dailymotion API.
- `setup_headers()`: Sets up request headers with authentication.
- `display_video_info(data)`: Formats and prints video information to terminal.
- `format_duration(seconds)`: Converts seconds to HH:MM:SS format.
- `format_date(date_string)`: Formats ISO date string to readable format.

## Supported Platforms

- **Dailymotion**: Full support for video information fetching.

More platforms can be added by extending the `BaseDownloader` class.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Aryan Rathod**
- Email: hello.kaiiddo@example.com
- GitHub: [ProKaiiddo](https://github.com/ProKaiiddo)

## Repository

[https://github.com/ProKaiiddo/kaiiddo-dld](https://github.com/ProKaiiddo/kaiiddo-dld)

---

*Note: This package is currently in alpha (v0.1.0). API may change in future versions.*
