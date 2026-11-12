"""
Generate sinhala-songs.json with 5000 Sinhala song entries.
Uses real popular artist names and generates song titles.
Lyrics are placeholder text for the owner to fill in later.
"""
import json
import random

# Real popular Sinhala artists
artists = [
    "W.D. Amaradeva", "Clarence Wijewardena", "Nanda Malini", "Sunil Edirisinghe",
    "Victor Ratnayake", "Rookantha Gunathilaka", "Sanath Nandasiri", "T.M. Jayaratne",
    "Bathiya & Santhush", "Centigradz", "Kasun Kalhara", "Satheeshan Rathnayaka",
    "Edward Jayakody", "Sangeeth Wijesuriya", "Athula Adikari", "Samitha Mudunkotuwa",
    "Chandralekha Perera", "Annesley Malawana", "Milton Mallawarachchi",
    "Deepika Priyadarshani", "Karunaratne Abeysekera", "H.R. Jothipala",
    "Latha Walpola", "Malini Bulathsinhala", "Neela Wickramasinghe",
    "Gunadasa Kapuge", "Amarasiri Peiris", "Somasiri Medagedara",
    "Rohana Weerasinghe", "Nalin Jayawardena", "Keerthi Pasquel",
    "Bachi Susan", "Iraj Weeraratne", "Lahiru Perera",
    "Umaria Sinhawansa", "Yohani", "Dinesh Gamage",
    "Shashika Nisansala", "Surendra Perera", "Dayan Witharana",
    "Jagath Wickramasinghe", "Sisira Senarathne", "Priya Sooriyasena",
    "Rukmani Devi", "Nirosha Virajini", "Radeesh Vandebona",
    "Dumal Warnakulasuriya", "Sajitha Anthony", "Thushara Joshap",
    "Chamara Weerasinghe", "Flashback", "Marians", "Arrow Star",
    "Gypsies", "Super Stars", "Sunflower", "Sahara Flash",
    "Purple Range", "Hiru Stars", "Derana Dream Star",
    "Daddy", "Ranidu", "Chitral Somapala", "Indunil Andramana",
    "Romesh Sugathapala", "Namal Udugama", "Noel Raj",
    "Amal Perera", "Dushyanth Weeraman", "Mihindu Ariyaratne",
    "Kavindya Adikari", "Ridma Weerawardena", "Chithral Somapala",
    "Kanchana Anuradhi", "Ashanthi", "BnS", "Pasan Liyanage",
    "Raini Charuka", "Sachith Peiris", "Udaya Sri",
    "Shihan Mihiranga", "Costa", "Shehan Kaushalya",
    "Nisansala", "Oshada", "Supun Perera",
    "Theekshana Anuradha", "Jaya Sri", "Lanthra Perera",
    "Himesh Hiranya", "Denuwan Kaushaka", "Nadeemal Perera",
    "Shashi Hewage", "Ruwan Hettiarachchi", "Chamara Ranawaka",
    "Senanayaka Weraliyadda", "Dayaratne Ranathunga", "Nihal Nelson",
    "Stanley Peiris", "Freddy Silva", "Desmond De Silva"
]

# Sinhala song title words/themes for generating titles
title_parts_sinhala = [
    "ආදරේ", "සිහිනේ", "මතකේ", "හදවත", "සඳ එළියේ", "මල්", "වැස්ස",
    "සුළඟ", "තරු", "රෑ", "දිනේ", "පාර", "ගඟ", "මුහුද", "අහස",
    "කඳුළු", "සිනාව", "හීනේ", "පෙම", "සෙනෙහස", "ජීවිතේ",
    "සුවඳ", "මල් පෙති", "නිල්", "රන්", "සුදු", "කළු",
    "පාසල", "ගම", "නගරේ", "ලෝකේ", "දෙවියන්", "බුදු",
    "අම්මා", "තාත්තා", "මිතුරා", "සොයුරා", "දරුවා",
    "කාලේ", "වසන්තේ", "ශ්‍රාවණේ", "අවුරුද්ද", "සරත්",
    "සැන්දෑව", "උදේ", "මධ්‍යහ්නේ", "හවස", "අලුයම",
    "පුංචි", "ලොකු", "ලස්සන", "සුන්දර", "මිහිරි",
    "තනි", "එකට", "දුර", "ළඟ", "පාවී",
    "නටනවා", "ගයනවා", "හඬනවා", "සිනාසෙනවා", "ඇවිදිනවා",
]

title_parts_english = [
    "Adare", "Sihine", "Mathake", "Hadawatha", "Sanda", "Mal", "Wessa",
    "Sulanga", "Tharu", "Raa", "Dine", "Para", "Ganga", "Muhuda", "Ahasa",
    "Kandulu", "Sinawa", "Heene", "Pema", "Senehasa", "Jeewithe",
    "Suwanda", "Mal Pethi", "Nil", "Ran", "Sudu", "Kalu",
    "Pasala", "Gama", "Nagare", "Loke", "Dewiyan", "Budu",
    "Amma", "Thaththa", "Mithura", "Soyura", "Daruwa",
    "Kale", "Wasanthe", "Shrawane", "Awurudda", "Sarath",
    "Sandawa", "Ude", "Madhyahne", "Hawasa", "Aluyama",
    "Punchi", "Loku", "Lassana", "Sundara", "Mihiri",
    "Thani", "Ekata", "Dura", "Langa", "Pawee",
    "Natanawa", "Gayanawa", "Handanawa", "Sinasanawa", "Awidinawa",
]

# Genres for Sinhala songs
genres = [
    "Baila", "Pop", "Classical", "Folk", "Soft Pop", "Rock",
    "R&B", "Hip Hop", "Ballad", "Pop Ballad", "Soft Rock",
    "Dance", "Reggae", "EDM", "Acoustic", "Classical Folk",
    "Pop Rock", "Electro Pop", "Indie", "Lo-fi", "Jazz",
    "Rap", "Duet", "Film Song", "Teledrama Song", "Devotional"
]

# Generate unique song titles
songs = []
used_titles = set()
song_id = 0

# Method 1: Two-word Sinhala combos
for i in range(len(title_parts_sinhala)):
    for j in range(len(title_parts_sinhala)):
        if i != j and len(songs) < 5000:
            si_title = f"{title_parts_sinhala[i]} {title_parts_sinhala[j]}"
            en_title = f"{title_parts_english[i]} {title_parts_english[j]}"
            if si_title not in used_titles:
                used_titles.add(si_title)
                song_id += 1
                artist = artists[song_id % len(artists)]
                genre = genres[song_id % len(genres)]
                slug = en_title.lower().replace(" ", "-").replace("&", "and").replace("'", "")
                songs.append({
                    "id": song_id,
                    "slug": slug,
                    "title_si": si_title,
                    "title_en": en_title,
                    "artist": artist,
                    "genre": genre,
                    "verses": [
                        {"label": "පද 1", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"},
                        {"label": "කෝරසය", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"},
                        {"label": "පද 2", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"}
                    ],
                    "meaning": "මෙම ගීතයේ අර්ථය මෙහි එකතු කරන්න. Add the song meaning here."
                })

# Method 2: Three-word combos to reach 5000
if len(songs) < 5000:
    for i in range(len(title_parts_sinhala)):
        for j in range(len(title_parts_sinhala)):
            for k in range(len(title_parts_sinhala)):
                if i != j and j != k and i != k and len(songs) < 5000:
                    si_title = f"{title_parts_sinhala[i]} {title_parts_sinhala[j]} {title_parts_sinhala[k]}"
                    en_title = f"{title_parts_english[i]} {title_parts_english[j]} {title_parts_english[k]}"
                    if si_title not in used_titles:
                        used_titles.add(si_title)
                        song_id += 1
                        artist = artists[song_id % len(artists)]
                        genre = genres[song_id % len(genres)]
                        slug = en_title.lower().replace(" ", "-").replace("&", "and").replace("'", "")
                        songs.append({
                            "id": song_id,
                            "slug": slug,
                            "title_si": si_title,
                            "title_en": en_title,
                            "artist": artist,
                            "genre": genre,
                            "verses": [
                                {"label": "පද 1", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"},
                                {"label": "කෝරසය", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"},
                                {"label": "පද 2", "lines": "ගීත පද මෙහි එකතු කරන්න\nAdd the actual lyrics here"}
                            ],
                            "meaning": "මෙම ගීතයේ අර්ථය මෙහි එකතු කරන්න. Add the song meaning here."
                        })

# Trim to exactly 5000
songs = songs[:5000]

# Write to JSON
output_path = r"e:\Projects\versenest_website\versenest_website\data\sinhala-songs.json"
import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"total": len(songs), "songs": songs}, f, ensure_ascii=False, indent=None)

print(f"Generated {len(songs)} songs to {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
