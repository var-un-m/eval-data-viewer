import json
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import requests
from PIL import Image, ImageTk
import threading
import csv
import os
import random

class VideoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Viewer")
        self.root.geometry("900x700")
        
        self.data = []
        self.available_indices = []
        self.current_entry = None
        self.current_video_url = None
        self.playing = False
        self.cap = None
        self.csv_file = "dataset.csv"
        
        # Initialize CSV if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Username', 'VideoURL'])
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Load JSON button
        self.load_btn = tk.Button(control_frame, text="Load JSON", command=self.load_json, 
                                   font=("Arial", 12), padx=20, pady=5, relief=tk.RAISED, bd=2)
        self.load_btn.grid(row=0, column=0, padx=5)
        
        # Info label
        self.info_label = tk.Label(control_frame, text="No data loaded", 
                                   font=("Arial", 11), anchor="w")
        self.info_label.grid(row=0, column=1, padx=20)
        
        # Video display
        self.canvas = tk.Canvas(self.root, width=800, height=450, bg="black")
        self.canvas.pack(pady=10)
        
        # Current entry info
        self.entry_info = tk.Label(self.root, text="", font=("Arial", 10), wraplength=800)
        self.entry_info.pack(pady=5)
        
        # Navigation and action frame
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        self.random_user_btn = tk.Button(nav_frame, text="Random Username", 
                                         command=self.random_username,
                                         font=("Arial", 11), state=tk.DISABLED, 
                                         padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.random_user_btn.grid(row=0, column=0, padx=5)
        
        self.random_video_btn = tk.Button(nav_frame, text="Random Video URL", 
                                          command=self.random_video_url,
                                          font=("Arial", 11), state=tk.DISABLED,
                                          padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.random_video_btn.grid(row=0, column=1, padx=5)
        
        self.play_btn = tk.Button(nav_frame, text="Play", command=self.play_video_action,
                                  font=("Arial", 11), state=tk.DISABLED,
                                  padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.play_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = tk.Button(nav_frame, text="Stop", command=self.stop_video,
                                  font=("Arial", 11), state=tk.DISABLED, 
                                  padx=15, pady=5, relief=tk.RAISED, bd=2)
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        # Add to dataset button (prominent)
        self.add_dataset_btn = tk.Button(self.root, text="Add to Dataset", 
                                        command=self.add_to_dataset,
                                        font=("Arial", 14, "bold"), 
                                        state=tk.DISABLED, padx=30, pady=10, 
                                        relief=tk.RAISED, bd=3)
        self.add_dataset_btn.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Arial", 10), fg="green", anchor="w")
        self.status_label.pack(pady=5)
        
        # Force update to ensure proper rendering
        self.root.update_idletasks()
        
    def load_json(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
            
            # Flatten the data structure
            self.data = []
            for entry in raw_data:
                if "Rings" in entry:
                    for ring in entry["Rings"]:
                        if ring.get("VideoURLs"):  # Only add if has videos
                            self.data.append(ring)
            
            # Initialize available indices for random sampling
            self.available_indices = list(range(len(self.data)))
            random.shuffle(self.available_indices)
            
            self.info_label.config(text=f"Loaded {len(self.data)} entries")
            self.random_user_btn.config(state=tk.NORMAL)
            self.random_video_btn.config(state=tk.NORMAL)
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.add_dataset_btn.config(state=tk.NORMAL)
            
            self.status_label.config(text="Click 'Random Username' to start", fg="blue")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {str(e)}")
    
    def random_username(self):
        if not self.data:
            return
        
        self.stop_video()
        
        # If we've gone through all entries, reshuffle
        if not self.available_indices:
            self.available_indices = list(range(len(self.data)))
            random.shuffle(self.available_indices)
            self.status_label.config(text="Reshuffled all usernames", fg="orange")
        
        # Get a random entry
        index = self.available_indices.pop()
        self.current_entry = self.data[index]
        
        # Randomly select a video URL from this entry
        video_urls = self.current_entry.get("VideoURLs", [])
        if video_urls:
            self.current_video_url = random.choice(video_urls)
        
        username = self.current_entry.get('Username', 'N/A')
        remaining = len(self.available_indices)
        
        self.entry_info.config(
            text=f"Username: {username} | Remaining usernames: {remaining}\n"
                 f"URL: {self.current_video_url}"
        )
        
        self.status_label.config(text="Ready to play. Click 'Play' button.", fg="blue")
    
    def random_video_url(self):
        if not self.current_entry:
            self.status_label.config(text="Please select a username first", fg="red")
            return
        
        self.stop_video()
        
        video_urls = self.current_entry.get("VideoURLs", [])
        if not video_urls:
            self.status_label.config(text="No videos available for this user", fg="red")
            return
        
        # Randomly select a different video URL
        self.current_video_url = random.choice(video_urls)
        
        username = self.current_entry.get('Username', 'N/A')
        remaining = len(self.available_indices)
        
        self.entry_info.config(
            text=f"Username: {username} | Remaining usernames: {remaining}\n"
                 f"URL: {self.current_video_url}"
        )
        
        self.status_label.config(text="Ready to play. Click 'Play' button.", fg="blue")
    
    def play_video_action(self):
        if not self.current_video_url:
            self.status_label.config(text="Please select a username first", fg="red")
            return
        
        # Download and play video in a separate thread
        threading.Thread(target=self.download_and_play_video, 
                        args=(self.current_video_url,), daemon=True).start()
    
    def download_and_play_video(self, video_url):
        try:
            # Delete any existing temp file first
            temp_file = "temp_video.mp4"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Error deleting old temp file: {e}")
            
            self.status_label.config(text="Downloading video...", fg="orange")
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.cap = cv2.VideoCapture(temp_file)
            if not self.cap.isOpened():
                raise Exception("Failed to open video")
            
            self.status_label.config(text="Playing video (looping)", fg="green")
            self.playing = True
            self.play_video_loop()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
    
    def play_video_loop(self):
        if not self.playing or not self.cap:
            return
        
        ret, frame = self.cap.read()
        
        if ret:
            # Resize frame to fit canvas
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            scale = min(800/w, 450/h)
            new_w, new_h = int(w*scale), int(h*scale)
            frame = cv2.resize(frame, (new_w, new_h))
            
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.canvas.create_image(400, 225, image=imgtk)
            self.canvas.image = imgtk
            
            # Schedule next frame (approximately 30 FPS)
            self.root.after(33, self.play_video_loop)
        else:
            # Video ended, loop it
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.root.after(33, self.play_video_loop)
    
    def stop_video(self):
        self.playing = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.canvas.delete("all")
        
        # Delete temporary video file
        temp_file = "temp_video.mp4"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"Error deleting temp file: {e}")
    
    def add_to_dataset(self):
        if not self.current_entry or not self.current_video_url:
            messagebox.showwarning("Warning", "Please select a username and video first")
            return
        
        username = self.current_entry.get('Username', 'N/A')
        
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([username, self.current_video_url])
            
            self.status_label.config(text=f"Added to dataset: {username}", fg="green")
            messagebox.showinfo("Success", 
                              f"Added to dataset:\nUsername: {username}\nURL: {self.current_video_url}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to dataset: {str(e)}")
    
    def on_closing(self):
        self.stop_video()
        
        # Clean up temp file on exit
        temp_file = "temp_video.mp4"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                print(f"Error deleting temp file on exit: {e}")
        
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoViewer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()