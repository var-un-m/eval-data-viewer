# Video Viewer Application

A Python-based video viewer application for browsing and cataloging video content from JSON data sources. Features random sampling, video playback, and dataset export capabilities.

## Features

- **JSON Data Loading**: Load video metadata from JSON files
- **Random Sampling**: Randomly sample usernames and their associated videos
- **Video Playback**: Stream and play videos directly from URLs
- **Manual Controls**: Full control over video selection and playback
- **Dataset Export**: Save selected videos to CSV for dataset creation
- **Smart Caching**: Videos are temporarily downloaded and automatically cleaned up

## Installation

### Prerequisites

- Python 3.7 or higher
- tkinter (usually comes with Python, see OS-specific notes below)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### OS-Specific Setup

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3-tkinter
```

**macOS/Windows:**
tkinter comes pre-installed with Python

## Usage

### Running the Application

```bash
python video_viewer.py
```

### Workflow

1. **Load JSON File**
   - Click "Load JSON" button
   - Select your JSON file containing video metadata
   - Application will automatically load and shuffle all entries

2. **Browse Videos**
   - Click "Random Username" to select a random user and video
   - Click "Random Video URL" to select a different video from the same user
   - Click "Play" to start video playback
   - Click "Stop" to stop the current video

3. **Export to Dataset**
   - When viewing a video you want to save
   - Click "Add to Dataset" button
   - Current username and video URL will be appended to `dataset.csv`

### JSON Format

The application expects JSON in the following format:

```json
[
  {
    "Prompt": "Description of the video",
    "RingCount": 1234,
    "Rings": [
      {
        "Username": "user123",
        "UserID": "abc123def456",
        "Provider": "provider_name",
        "VideoURLs": [
          "https://example.com/video1.mp4",
          "https://example.com/video2.mp4"
        ]
      }
    ]
  }
]
```

## Output

### dataset.csv

CSV file containing selected videos with the following columns:
- `Username`: The username associated with the video
- `VideoURL`: The direct URL to the video file

Example:
```csv
Username,VideoURL
user123,https://example.com/video1.mp4
user456,https://example.com/video2.mp4
```

## Features in Detail

### Random Sampling
- Application shuffles all usernames on load
- Samples without replacement until all users are viewed
- Automatically reshuffles when all users have been shown
- Each username can have multiple videos, randomly selected

### Video Management
- Videos are temporarily downloaded for playback
- Automatic cleanup when switching videos
- No persistent storage of video files
- Supports video looping during playback

### User Interface
- **Random Username**: Load a new random user
- **Random Video URL**: Switch to different video from current user
- **Play**: Start video playback
- **Stop**: Stop current video
- **Add to Dataset**: Export current video to CSV

## Technical Details

### Dependencies

- **opencv-python**: Video capture and playback
- **pillow**: Image processing for frame display
- **requests**: HTTP requests for video downloads

### Memory Management

- Videos are downloaded to temporary files
- Previous videos are deleted when loading new ones
- All temporary files cleaned up on application exit
- Memory-efficient streaming for large videos

## Troubleshooting

### "No module named 'tkinter'"
Install tkinter for your OS (see OS-Specific Setup above)

### Video won't play
- Check your internet connection
- Verify the video URL is accessible
- Some videos may have expired or restricted URLs

### Application freezes during download
- Large videos may take time to download
- Status label shows "Downloading video..." during this process
- Wait for download to complete

## License

This project is provided as-is for dataset creation and video review purposes.

## Requirements

See `requirements.txt` for complete list of Python package dependencies.
