import os
import subprocess
import re
import yt_dlp as youtube_dl
from tqdm import tqdm
from pytube import Playlist
from colorama import Fore, Back, Style
import scrapetube
from pydub import AudioSegment
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from htmldate import find_date
from urllib.parse import urlparse
from datetime import datetime
import requests

class VideoDownloaderApp:
    def __init__(self):
        self.links = []
        self.creation_dates = []
        self.failed_links = []
        self.error_file = "failed_links.txt"
        self.download_folder = "downloads"
        self.input_file = "input.txt"
        self.urllog_file = "urllog.txt"  # To store successfully downloaded URLs
        self.running = False
    
    def print_large_ascii_art(self, text):
        ascii_art = {
            'y': " Y   Y \n  Y Y  \n   Y   \n   Y   ",
            't': "TTTTT \n  T   \n  T   \n  T   ",
            '-': "      \n----- \n      \n      ",
            'd': "DDD   \nD   D \nD   D \nDDD   ",
            'l': "L     \nL     \nL     \nLLL   ",
            'p': "PPP  \nP  P \nPPP  \nP    "
        }


        line = '-' * (len(text) * 5 + 8)
        print(Fore.RED + line)

        for row in range(4):
            row_str = Fore.RED + "|"
            for char in text:
                row_str += Fore.WHITE + ascii_art[char].split('\n')[row].ljust(4)
            row_str += Fore.RED + "|"
            print(row_str)

        print(line)

    def add_url(self, url):
        if url:
            self.links.append(url)
            self.creation_dates.append(find_date(url))
            print(f"Added URL: {url}")

    def load_urls_from_file(self, filename):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, "input", filename)

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    url = line.strip()
                    self.links.append(url)
                    self.creation_dates.append(find_date(url))
                    print(f"Added URL from file: {url}")
        except FileNotFoundError:
            input(f"File not found in directory: {script_directory}")
        except Exception as e:
            input(f"An error occurred: {e}")



    def start_processing(self):
        print("Start Processing")
        if not self.running:
            self.running = True
            self.download_videos()
            self.running = False

    def start_processing_audio(self):
        print("Start Processing")
        if not self.running:
            self.running = True
            self.download_audio()
            self.running = False
            
    def start_processing_se(self, season, length, start):
        print("Start Processing")
        if not self.running:
            self.running = True
            self.download_videos_se(season, length, start)
            self.running = False 

    def start_processing_nt(self):
        print("Start Processing")
        if not self.running:
            self.running = True
            self.download_videos_nt()
            self.running = False 



    def download_videos(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.failed_links = []
        for i, link in enumerate(self.links):
            if not self.running:
                break

            success, video_name, download_speed = self.run_youtube_dl(link)
            if success:
                self.move_to_urllog_file(link)
                self.remove_from_input_file(link)
            else:
                self.failed_links.append(link)
                self.write_failed_links_to_file()

            progress = (i + 1) / len(self.links) * 100
            self.print_progress(progress, download_speed)

        self.links = self.failed_links.copy()

    def download_audio(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.failed_links = []
        for i, link in enumerate(self.links):
            if not self.running:
                break

            success, video_name, download_speed = self.run_youtube_dl_audio(link)
            if success:
                self.move_to_urllog_file(link)
                self.remove_from_input_file(link)
            else:
                self.failed_links.append(link)
                self.write_failed_links_to_file()

            progress = (i + 1) / len(self.links) * 100
            self.print_progress(progress, download_speed)

        self.links = self.failed_links.copy()

    def download_videos_se(self, season, length, start):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.failed_links = []
        seasonint = int(season)
        num = int(start) + 1
        for i, link in enumerate(self.links):
            if not self.running:
                break

            success, video_name, download_speed = self.run_youtube_dl_se(link, num, seasonint)
            if success:
                self.move_to_urllog_file(link)
                self.remove_from_input_file(link)
            else:
                self.failed_links.append(link)
                self.write_failed_links_to_file()

            progress = (i + 1) / len(self.links) * 100
            self.print_progress(progress, download_speed)
            num += 1
            if (num > int(length) and int(length) != 0):
                seasonint += 1
                num = 0
                
        self.links = self.failed_links.copy()

    def download_videos_nt(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.failed_links = []
        for i, link in enumerate(self.links):
            if not self.running:
                break

            success, video_name, download_speed = self.run_youtube_dl_nt(link)
            if success:
                self.move_to_urllog_file(link)
                self.remove_from_input_file(link)
            else:
                self.failed_links.append(link)
                self.write_failed_links_to_file()

            progress = (i + 1) / len(self.links) * 100
            self.print_progress(progress, download_speed)

        self.links = self.failed_links.copy()



    def run_youtube_dl(self, url):
        print(f"Downloading video from URL: {url}")
        try:
            ydl_opts = {
                'format': 'best',
                'writethumbnail': True,
                'embedthumbnail': True,
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            }
            download_speed = 0

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_name = info_dict['title']
                download_speed = info_dict.get('speed', 0)

                #with tqdm(total=info_dict.get('filesize', 0), dynamic_ncols=True, unit='B', unit_scale=True, leave=True) as progress:
                #    def hook(data):
                #        if data['status'] == 'downloading':
                #            progress.update(data['downloaded_bytes'] - progress.n)
                #        elif data['status'] == 'finished':
                #            progress.close()

                #    ydl.params.update({'progress_hooks': [hook]})
                ydl.download([url])

            print(f"Video downloaded successfully from URL at {download_speed}MB/s: {url}")
            print(Fore.MAGENTA + "-------------------------------------------------------------------------" + Fore.RESET)
            return True, video_name, download_speed

        except Exception as e:
            input(f"Error downloading video from URL: {url}: {e}")
        return False, "", download_speed
    
    def run_youtube_dl_se(self, url, episode, season):
        print(f"Downloading video from URL: {url}")
        val = "00"
        seasonval = "00"
        if episode < 10: 
            val = "0" + str(episode)
        else:
            val = str(episode)

        if season < 10:
            seasonval = "0" + str(season)
        else:
            seasonval = str(season)
        try:
            ydl_opts = {
                'format': 'best',
                'writethumbnail': True,
                'embedthumbnail': True,
                'outtmpl': os.path.join(self.download_folder, f'S{seasonval}E{val} - %(title)s.%(ext)s'),
            }
            download_speed = 0

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_name = info_dict['title']
                download_speed = info_dict.get('speed', 0)

                #with tqdm(total=info_dict.get('filesize', 0), dynamic_ncols=True, unit='B', unit_scale=True, leave=True) as progress:
                #    def hook(data):
                #        if data['status'] == 'downloading':
                #            progress.update(data['downloaded_bytes'] - progress.n)
                #        elif data['status'] == 'finished':
                #            progress.close()

                #    ydl.params.update({'progress_hooks': [hook]})
                ydl.download([url])

            print(f"Video downloaded successfully from URL at {download_speed}MB/s: {url}")
            print(Fore.MAGENTA + "-------------------------------------------------------------------------" + Fore.RESET)
            return True, video_name, download_speed

        except Exception as e:
            input(f"Error downloading video from URL: {url}: {e}")
        return False, "", download_speed

    def run_youtube_dl_nt(self, url):
        print(f"Downloading video from URL: {url}")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            }
            download_speed = 0

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_name = info_dict['title']
                download_speed = info_dict.get('speed', 0)

                #with tqdm(total=info_dict.get('filesize', 0), dynamic_ncols=True, unit='B', unit_scale=True, leave=True) as progress:
                #    def hook(data):
                #        if data['status'] == 'downloading':
                #            progress.update(data['downloaded_bytes'] - progress.n)
                #        elif data['status'] == 'finished':
                #            progress.close()

                #    ydl.params.update({'progress_hooks': [hook]})
                ydl.download([url])

            print(f"Video downloaded successfully from URL at {download_speed}MB/s: {url}")
            print(Fore.MAGENTA + "-------------------------------------------------------------------------" + Fore.RESET)
            return True, video_name, download_speed

        except Exception as e:
            input(f"Error downloading video from URL: {url}: {e}")
        return False, "", download_speed

    def run_youtube_dl_audio(self, url):
        print(f"Downloading audio from URL: {url}")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            }
            download_speed = 0

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_name = info_dict['title']
                download_speed = info_dict.get('speed', 0)

                #with tqdm(total=info_dict.get('filesize', 0), dynamic_ncols=True, unit='B', unit_scale=True, leave=True) as progress:
                #    def hook(data):
                #        if data['status'] == 'downloading':
                #            progress.update(data['downloaded_bytes'] - progress.n)
                #        elif data['status'] == 'finished':
                #            progress.close()

                #    ydl.params.update({'progress_hooks': [hook]})
                ydl.download([url])

            print(f"Video downloaded successfully from URL at {download_speed}MB/s: {url}")
            print(Fore.MAGENTA + "-------------------------------------------------------------------------" + Fore.RESET)
            return True, video_name, download_speed

        except Exception as e:
            input(f"Error downloading video from URL: {url}: {e}")
        return False, "", download_speed



    def write_failed_links_to_file(self):
        with open(self.error_file, "a") as f:
            for link in self.failed_links:
                f.write(link + "\n")

    def move_to_urllog_file(self, url):
        with open(self.urllog_file, "a") as f:
            f.write(str(datetime.now()) + url + "\n")

    def remove_from_input_file(self, url):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, self.input_file)
        try:
            with open(file_path, 'r', "a") as file:
                lines = file.readlines()
            with open(file_path, 'w', "a") as file:
                for line in lines:
                    if line.strip() != url:
                        file.write(line)
        except Exception as e:
            input(f"Error removing URL from list: {url}: {e}")

    def print_progress(self, progress, download_speed):
        pass

    def extract_playlist(self, playlisturl):
        playlist = Playlist(playlisturl)
        video_urls = [video for video in playlist.video_urls]
        for url in video_urls:
            self.links.append(url)
            self.creation_dates.append(find_date(url))
            print(f"Added URL from playlist: {url}")

    def extract_channel(self, channelid):
        videos = scrapetube.get_channel(channelid)

        for video in videos:
            self.links.append("https://www.youtube.com/watch?v=" + video['videoId'])
            self.creation_dates.append(find_date("https://www.youtube.com/watch?v=" + video['videoId']))
            print(f"Added URL from channel: https://www.youtube.com/watch?v={video['videoId']}")
        self.links.reverse()

    def convert_mp4_to_mp3(self, input_file, output_file):
        try:
            if not os.path.exists("mp3_output"):
                # Create a new directory because it does not exist
                os.makedirs("mp3_output")
            script_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_directory, "input",input_file)
            output_path = os.path.join(script_directory, "mp3_output", output_file)
            command = f"ffmpeg -i {str(file_path)} -vn -acodec libmp3lame {str(output_path)}"
            os.system(command)
            print(f"Conversion successful! MP3 file saved as {output_path}")
        except Exception as e:
            input(f"Error: {e}")

    async def fetch_title(self, session, url):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string.strip() if soup.title else "Title not found"
                    return title
                else:
                    return f"Failed to fetch URL: {url}. Status code: {response.status}"
        except aiohttp.ClientError as e:
            return f"Error fetching URL {url}: {e}"
        except Exception as ex:
            return f"Exception occurred for {url}: {ex}"

    async def get_titles(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [app.fetch_title(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results

    def get_tab_name(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extracting the title of the page or any specific element indicating the tab name
                title = soup.title.string.strip() if soup.title else None
                return title
        except Exception as e:
            input(f"Error processing URL {url}: {e}")
        return None

    def get_creation_date(self, url):
        try:
            parsed_url = urlparse(url)
            html_date = find_date(url)
            if html_date:
                return datetime.strptime(html_date, '%Y-%m-%d')
        except Exception as e:
            input(f"Error processing URL {url}: {e}")
        return None

if __name__ == '__main__':
    app = VideoDownloaderApp()
    while True:
        if not os.path.exists("input"):
                # Create a new directory because it does not exist
                os.makedirs("input")
        os.system('cls' if os.name == 'nt' else 'clear')
        app.print_large_ascii_art("yt-dlp")
        print(Style.DIM + Fore.WHITE + Back.MAGENTA + "By. Sjl101"+ Back.RESET)
        print(Fore.WHITE + f"Current links: {len(app.links)}" + Back.RESET)
        print(Style.RESET_ALL + Fore.MAGENTA + "1. Add URL")
        print(Fore.MAGENTA + "2. Load URLs from file")
        print(Fore.MAGENTA + "3. Extract playlist URLs to list")
        print(Fore.MAGENTA + "4. Extract all URLs from channel")
        if not app.running:
            print(Fore.GREEN + "5. Start processing")
        else:
            print(Fore.WHITE + "5. Processing (Running)")
        print(Fore.GREEN + "6. Start processing as a season")
        print(Fore.GREEN + "7. Start processing no thumbnail")
        print(Fore.GREEN + "8. Start processing as a MP3 file")
        print(Fore.CYAN + "9. Show list")
        print(Fore.WHITE + "10. Convert mp4 file to mp3 format")
        if not app.running:
            print(Fore.RED + "11. Exit") 
        choice = input(Fore.WHITE + "Enter your choice: ")
        if choice == '1':
            url = input(Fore.WHITE + "Enter the video URL: ")
            app.add_url(url)
        elif choice == '2':
            filename = input(Fore.WHITE + "Enter the input file name (including .txt): ")
            app.load_urls_from_file(filename)
        elif choice == '3' and not app.running:
            playlisturl = input(Fore.WHITE + "Enter Playlist URL: ")
            app.extract_playlist(playlisturl)
        elif choice == '4' and not app.running:
            channelid = input(Fore.WHITE + "Enter channel ID: ")
            app.extract_channel(channelid)
        elif choice == '5' and not app.running:
            app.start_processing()
        elif choice == '6' and not app.running:
            season = input(Fore.WHITE + "Enter season '00': ")
            seasonlength = input(Fore.WHITE + "Enter episodes per season, 0 for unlimited: ")
            seasonstart = input(Fore.WHITE + "Enter episode start: ")
            app.start_processing_se(season, seasonlength, seasonstart)
        elif choice == '7' and not app.running:
            app.start_processing_nt()    
        elif choice == '8' and not app.running:
            app.start_processing_audio()   
        elif choice == '9':
            os.system('cls' if os.name == 'nt' else 'clear')
            loop = asyncio.get_event_loop()
            titles = loop.run_until_complete(app.get_titles(app.links))
            listcount = 0
            for url, title in zip(app.links, titles):
                listcount += 1
                print(Fore.WHITE + f"{listcount}. {url}: {title}: Created: {find_date(url)}")
            print(Fore.MAGENTA + f"-----------------------------------------------------------------")
            print(Fore.CYAN + f"1. Sort by title")
            print(Fore.CYAN + f"2. Sort by creation date")
            print(Fore.CYAN + f"3. Reverse list")
            print(Fore.CYAN + f"4. Remove URL from list")
            print(Fore.CYAN + f"5. Remove all from list")
            print(Fore.CYAN + f"6. Exit list...")
            listchoice = input(Fore.WHITE + "Enter your choice: ")
            if listchoice == '1':
                print(Fore.WHITE + f"Sorting based on tab name")
                app.links.sort(key=app.get_tab_name)
                input(Fore.CYAN + f"Sorted! Press Enter to continue...")
            elif listchoice == '2':
                print(Fore.WHITE + f"Sorting based on creation date")
                app.links.sort(key=app.get_creation_date)
                input(Fore.GREEN + "Sorted! Press Enter to continue...")
            elif listchoice == '3':
                print(Fore.WHITE + f"Reversing list")
                app.links.reverse()
                input(Fore.CYAN + f"Sorted! Press Enter to continue...")
            elif listchoice == '4':
                indexinput = input(Fore.WHITE + f"Enter index for deletion: ")
                index = int(indexinput) - 1
                deletedurl = app.links[index]
                app.links.pop(index)
                input(Fore.CYAN + f"Removed {deletedurl} from list! Press Enter to continue...")
            elif listchoice == '5':
                print(Fore.WHITE + f"Clearing list")
                app.links.clear()
                input(Fore.CYAN + f"Cleared list! Press Enter to continue...")
            elif listchoice == '6':
                print(Fore.WHITE + f"")
            #input(Fore.GREEN + "Press Enter to continue...")
        elif choice == "10":
            file_path = input(Fore.WHITE + "Enter the input file name (including .mp4): ")
            output_path = input(Fore.WHITE + "Enter the name for the output file (including .mp3): ")
            print(file_path, output_path)
            app.convert_mp4_to_mp3(file_path, output_path)
        elif choice == '11' and not app.running:
            break
        
        
