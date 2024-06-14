#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title GifMaker
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon 📺
# @raycast.argument1 { "type": "text", "placeholder": "folder_name" }

# Documentation:
# @raycast.description Transforms Video Files into Gifs from folder name
# @raycast.author bastien_labat
# @raycast.authorURL https://raycast.com/bastien_labat



import os
import sys
from moviepy.editor import VideoFileClip
import logging

logging.basicConfig(level=logging.INFO) #Logger to display progress in terminal

def find_folder(folder_name):
    """Locates folder with the specified name on the computer."""

    # Start searching from the root directory
    root_dir = os.path.abspath('/')
    for root, dirs, files in os.walk(root_dir):
        if folder_name in dirs:
            return os.path.join(root, folder_name)

    # If folder not found
    return None


def transform_videos_into_gifs(folder_name):
    """Transforms videos in the folder_name into GIFs"""

    # Check if the folder_name exists
    if not os.path.exists(folder_name):
        logging.error(f"The folder_name '{folder_name}' does not exist.")
        return

    # Get list of video files in the folder_name
    video_files = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if file.endswith(('.mov', '.mp4'))]

    if not video_files:
        logging.info(f"No video files found in '{folder_name}'.")
        return

    for video_file in video_files:
        try:
            logging.info(f"Converting '{video_file}' to GIF...")
            gif_name = os.path.splitext(video_file)[0] + ".gif"
            video_clip = VideoFileClip(video_file)
            video_clip.write_gif(gif_name, fps=15, program = 'ffmpeg')
            logging.info(f"GIF '{gif_name}' created successfully.")
        except Exception as e:
            logging.error(f"Error converting '{video_file}' to GIF: {str(e)}")

if __name__ == "__main__":
    # Check if folder_name argument is provided
    if len(sys.argv) != 2:
        print("Usage: python GifMaker.py <folder_name>")
        sys.exit(1)

    folder_name = sys.argv[1]
    logging.info(f"Looking for folder {folder_name}")
    folder_path = find_folder(folder_name)
    if not folder_path:
        logging.error(f"The folder '{folder_name}' could not be found on the computer.")
        sys.exit(1)

    transform_videos_into_gifs(folder_path)
