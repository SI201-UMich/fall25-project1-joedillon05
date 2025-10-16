import csv

def write_txt_output(filename, top_song, avg_duration, percent_above):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Top song by view count:\n{top_song}\n\n")
        f.write(f"Average duration for Pop songs: {avg_duration:.2f} seconds\n\n")
        f.write(f"Percent of songs with channel followers > 1M: {percent_above:.2f}%\n")

def write_csv_output(filename, songs):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=songs[0].keys())
        writer.writeheader()
        writer.writerows(songs)