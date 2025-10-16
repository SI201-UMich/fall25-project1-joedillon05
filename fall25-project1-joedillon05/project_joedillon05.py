import csv
from pathlib import Path
import re


def write_txt_output(filename, top_song, avg_duration, percent_above):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Top song by view count:\n")
        if top_song:
            f.write(f"{top_song.get('title','')} by {top_song.get('channel','')} (views: {top_song.get('view_count',0)})\n\n")
        else:
            f.write("No top song found\n\n")
        f.write(f"Average duration for Pop songs: {avg_duration:.2f} seconds\n\n")
        f.write(f"Percent of songs with channel followers > 1M: {percent_above:.2f}%\n")


def write_csv_output(filename, songs):
    if not songs:
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(songs[0].keys()))
        writer.writeheader()
        writer.writerows(songs)


def percent_songs_above_follower_threshold(songs, threshold):
    count = 0
    for song in songs:
        followers = song.get('channel_follower_count', 0)
        try:
            if int(followers) > threshold:
                count += 1
        except Exception:
            continue
    percent = (count / len(songs)) * 100 if songs else 0
    return percent


def get_top_song(songs):
    """Return the top song by view count from cleaned songs."""
    if not songs:
        return None
    sorted_songs = sorted(songs, key=lambda x: int(x.get('view_count', 0)), reverse=True)
    return sorted_songs[0]


def _to_int(value):
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    # remove non-digits
    s = re.sub(r"[^0-9]", "", str(value))
    try:
        return int(s) if s else 0
    except ValueError:
        return 0


def clean_song_data(songs):
    cleaned = []
    for song in songs:
        # preserve original fields but normalize numeric types
        duration = _to_int(song.get('duration', 0))
        view_count = _to_int(song.get('view_count', 0))
        followers = _to_int(song.get('channel_follower_count', 0))
        categories_raw = song.get('categories', '') or ''
        # categories may be a pipe-separated or comma-separated list; normalize to list
        if isinstance(categories_raw, str):
            if '|' in categories_raw:
                categories = [c.strip() for c in categories_raw.split('|') if c.strip()]
            else:
                categories = [c.strip() for c in categories_raw.split(',') if c.strip()]
        else:
            categories = []

        cleaned_song = {
            'title': song.get('title', '') or song.get('fulltitle', ''),
            'view_count': view_count,
            'channel': song.get('channel', ''),
            'channel_follower_count': followers,
            'duration': duration,
            'categories': categories,
        }
        cleaned.append(cleaned_song)
    return cleaned


def read_youtube_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

# --- moved up so they're defined before use ---
def get_top_songs_by_views(songs, n):
    # Reference at least 3 columns: title, view_count, channel
    # songs expected to be cleaned (view_count is int)
    sorted_songs = sorted(songs, key=lambda x: x.get('view_count', 0), reverse=True)
    return [
        {
            'title': song.get('title', ''),
            'view_count': song.get('view_count', 0),
            'channel': song.get('channel', ''),
        }
        for song in sorted_songs[:n]
    ]

def average_duration_by_category(songs, category):
    # Reference at least 3 columns: duration, categories, title
    # songs expected to be cleaned (duration is int and categories is list)
    filtered = [s for s in songs if category in (s.get('categories') or [])]
    if not filtered:
        return 0
    total_duration = sum(s.get('duration', 0) for s in filtered)
    avg = total_duration / len(filtered)
    return avg
# --- end moved section ---
if __name__ == "__main__":
    # locate CSV relative to this script
    repo_root = Path(__file__).resolve().parent
    csv_path = repo_root / "youtube-top-100-songs-2025.csv"
    songs = read_youtube_csv(csv_path)
    print(f"Loaded {len(songs)} songs from CSV.")
    for song in songs[:5]:
        print(song)
    cleaned_songs = clean_song_data(songs)
    print(f"Loaded {len(cleaned_songs)} cleaned songs from CSV.")
    for song in cleaned_songs[:5]:
        print(song)

    # Print the top song by view count automatically
    top_song = get_top_song(cleaned_songs)
    print("Top song by view count:")
    print(top_song)

    # Calculation 1: Average duration for Pop songs
    # (Assumes original songs list has 'duration' and 'categories')
    avg_duration = average_duration_by_category(songs, 'Pop')

    # Calculation 2: Percent of songs with channel followers > 1,000,000
    percent_above = percent_songs_above_follower_threshold(cleaned_songs, 1000000)

    # Write results to output files
    write_txt_output("results.txt", top_song, avg_duration, percent_above)
    write_csv_output("top_songs.csv", get_top_songs_by_views(cleaned_songs, 10))