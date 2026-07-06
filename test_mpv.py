import mpv
import time

print("Initializing mpv...")
player = mpv.MPV(ytdl=True, video=False, log_handler=print)

print("Playing audio...")
player.play("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

time.sleep(5)
print("Finished test.")
