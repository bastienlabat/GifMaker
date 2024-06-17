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
import logging
import cv2
from PIL import Image
from transparent_background import Remover
import imageio
from pygifsicle import optimize

logging.basicConfig(level=logging.INFO)  # Logger to display progress in terminal
# Load model
# remover = Remover()
remover = Remover(mode="fast") 
# remover = Remover(mode="base-nightly")  # nightly release checkpoint


def find_folder(folder_name):
    """Locates folder with the specified name on the computer."""

    # Start searching from the root directory
    root_dir = os.path.expanduser("~")  # This sets root_dir to the user's home directory
    print(root_dir)
    for root, dirs, files in os.walk(root_dir):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    #If folder is not found
    return None


def find_videos(folder_path):
    # Get list of video files in the folder_name
    video_list = [
        os.path.join(folder_path, file_name)
        for file_name in os.listdir(folder_path)
        if file_name.endswith((".mov", ".mp4"))
    ]

    if not video_list:
        logging.info(f"No video files found in '{folder_path}'.")
        return
    else:
        return video_list

def transform_video_to_gif_no_background(video_path,fps_out=5):
    """Takes video with certain fps, takes key frames such that resulting gif has specific fps, edits the background out and transforms the edited frames into gifs"""
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Error: Could not open video file."

    # Get input video frame rate
    fps_in = cap.get(cv2.CAP_PROP_FPS)

    # Initialize frame indices
    index_in = -1
    index_out = -1

    # List to store frames for the GIF
    gif_frames = []
    logging.info(f"Editing '{video_path}'...")
    while True:
        # Until index don't match such that resulting frames match target fps, it skips to next frame
        success = cap.grab()#grab() skips to next frame
        if not success:
            break
        index_in += 1

        out_due = int(index_in / fps_in * fps_out)

        # If target index is > to current we need to include this frame
        if out_due > index_out:
            success, frame = cap.retrieve()
            if not success:
                break
            index_out += 1

            # Process frame to remove background
            frame = cv2.resize(frame,(640,360))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).convert("RGB")
            logging.info(f"Removing background from frame {index_out}...")

            processed_frame = remover.process(img,type='white')

            # Append the processed frame to the gif_frames list
            gif_frames.append(processed_frame)

    # Save frames as a GIF
    try:

        logging.info(f"Converting '{video_path}' to GIF...")
        gif_path = os.path.splitext(video_path)[0] + ".gif"

        imageio.mimsave(gif_path, gif_frames,loop=0)
        logging.info(f"Compressing '{video_path}'...")
        optimize(gif_path)

        logging.info(f"GIF '{gif_path}' created successfully.")
    except Exception as e:
        logging.error(f"Error converting '{video_path}' to GIF: {str(e)}")


if __name__ == "__main__":
# Check if folder_name argument is provided

    if len(sys.argv) != 2:
       print("Wrong number of arguments. Enter folder_name only")
       sys.exit(1)

    folder_name = sys.argv[1]
    logging.info(f"Looking for folder {folder_name}")
    folder_path = find_folder(folder_name)
    if not folder_path:
        logging.error(f"The folder '{folder_name}' could not be found on the computer.")
        sys.exit(1)

    video_list = find_videos(folder_path)
    for video_path in video_list:
        transform_video_to_gif_no_background(video_path)
