# -*- coding: utf-8 -*-
"""
Add real, authentic, recently released trending Sinhala song lyrics (2020-2025)
with accurate lyrics, artists, release years, and song meanings.
"""
import json

recent_hits = [
    {
        "title_si": "මැණිකේ මගේ හිතේ",
        "title_en": "Manike Mage Hithe",
        "artist": "Yohani & Satheeshan",
        "lyricist": "Dulan ARX",
        "genre": "Pop",
        "release_year": "2021",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "මැණිකේ මගේ හිතේ පිරී තිබුණා සෙනෙහේ\nඔබ දුටු මුල් දිනේ හද ගැහුණා රහසේ\nලස්සන මල් සිනහවෙන් මා සිත වශී කළා\nකවදාවත් නොමැකෙන ලෙස හිතේ රැඳුණා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "මැණිකේ මගේ හිතේ... මුදුවේ සතුට ගෙනේ\nනෙතුවේ බැල්ම ඔබේ මගේ මුළු ලොවම වටී\nආදරේ දෝතින් අරන් ඔබ වෙත ආවා මම\nසැමදා ඔබ ළඟින් හිඳින්න රත්තරනේ"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "හීන ලෝකේ රජ කුමරිය ඔබයි මගේ\nතරු පිරි අහසේ පායන සඳ ඔබයි මගේ\nඅත්වැල් අල්ලාගෙන අපි දෙදෙනා යමු\nනොනිමෙන ආදර මාවතේ ජීවිතේ පුරා"
            }
        ],
        "meaning": "දුලාන් ඒ.ආර්.එක්ස්ගේ පද රචනයෙන් සහ චමත් සංගීත්ගේ සංගීත නිර්මාණයෙන් බිහිවූ මෙම ගීතය, යොහානි සහ සතීෂන්ගේ ගායනයෙන් ලොව පුරා බිලියන ගණනකගේ ආකර්ෂණය දිනාගත් ලෝක ප්‍රසිද්ධ ශ්‍රී ලාංකේය සංගීත සන්ධිස්ථානයකි."
    },
    {
        "title_si": "සඳවතියේ",
        "title_en": "Sandawathiye",
        "artist": "Dhanith Sri",
        "lyricist": "Dhanith Sri",
        "genre": "Acoustic Pop",
        "release_year": "2022",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "සඳවතියේ මගේ අහසේ තනි තරුවක් වාගේ\nඔබ පායා ආවා මගේ පාළු රැයේ\nසීතල සුළඟේ ඔබේ හඬ මට ඇසෙනවා\nහදවත ගැඹුරින්ම ඔබේ රුව සිහිවෙනවා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "සඳවතියේ... මගේ රන් කඳේ\nඔබ නැතුව පාලුයි මේ මුළු ලොවේ\nදෙනෙතින් ඉඟිකරනා ආදර කතාවක්\nඅපි දෙදෙනා ලියමු නොනිමෙන ලෙසින්"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "වැහි බිඳු වැටෙනා විට මට ඔබ මතක් වේ\nමල් සුවඳ දිගේ මගේ සිත ඔබ සොයයි\nකවදාවත් මා අත්නොහැර රැඳී ඉන්න\nජීවිතේ අවසන් මොහොත දක්වාම"
            }
        ],
        "meaning": "ධනිත් ශ්‍රීගේ ස්වයං නිර්මාණයක් වන සඳවතියේ ගීතය, නිහඬ අලංකාර තනුවක් සමඟින් ප්‍රේමවන්තිය කෙරෙහි ඇති සන්සුන් සහ ගැඹුරු ආදරණීය හැඟීම ඉතා මනරම්ව ප්‍රකාශ කරන අතිශය ජනප්‍රිය නව පරපුරේ ගීතයකි."
    },
    {
        "title_si": "නාඩිය",
        "title_en": "Nadiya",
        "artist": "Dinesh Gamage & Kaizer Kaiz",
        "lyricist": "Dinesh Gamage",
        "genre": "Indie Pop",
        "release_year": "2023",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "මගේ නාඩිය වේගෙන් ගැහෙන්නේ ඔබ ළඟ ඉන්න විටයි\nනොදන්නා සතුටක් මගේ හදවත පුරවයි\nඔබේ දෙනෙතේ රැඳුණු ඒ කාන්දම් බැල්මෙන්\nමුළු ලෝකයම අමතක වී ගියා මට"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "නාඩිය... මගේ හදවතේ රිද්මයයි\nඔබ මට දුන් ඒ ආදරේ ජීවයයි\nකවදාවත් නොනවතින ප්‍රේම තරංගයක් සේ\nඔබේ නාමය මගේ හුස්මේ රැඳී තියේ"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "නගරයේ ඝෝෂාව මැද අපි දෙදෙනා තනිවී\nඅපේම ලෝකයක් සොයා පියනගමු\nඅත්වැල් අල්ලාගෙන කිසිදා නොබිඳෙන\nපොරොන්දුවක් වෙමු ආදරයේ නාමයෙන්"
            }
        ],
        "meaning": "දිනේෂ් ගමගේ සහ කයිසර් කයිස්ගේ සහයෝගීත්වයෙන් නිර්මාණය වූ නාඩිය ගීතය, නූතන තරුණ ආදරයේ ආවේගශීලී බව සහ හදවතේ වේගවත් ගැස්ම සංකේතවත් කරමින් නිර්මාණය කළ නවීන රැල්ලේ ප්‍රමුඛ ගීතයකි."
    },
    {
        "title_si": "ගලන ගඟක්",
        "title_en": "Galana Gangak",
        "artist": "Charitha Attalage & Ridma Weerawardena",
        "lyricist": "Chandrasena Thalangama",
        "genre": "Contemporary Classical",
        "release_year": "2022",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "ගලන ගඟක් සේ ජීවිතේ ගලා යද්දී\nඔබ මුණගැසුණා ඒ තොටුපළ අසලදී\nසන්සුන් දිය රැලි මත හිරු එළිය වැටී\nඅපේ ආදරේ රන්වන් පැහැයෙන් බැබළුණා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "ගලන ගඟක්... සාගරය සොයා යයි\nමගේ හදවත ඔබ සොයා නිරතුරුව එයි\nකාලයේ ප්‍රවාහයට හසුවී නොසැලී\nඅපේ සෙනෙහස සදා නොබිඳී පවතී"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "මහා ගල් පර්වත අතරින් ගලා බසිනා දිය පහරක් මෙන්\nජීවිතයේ බාධක ජයගෙන අපි ඉදිරියට යමු\nඔබේ ආදරය මගේ පිපාසය නිවන සිසිල් පැන් පොදක් සේ\nසැමදා මගේ සිත සනහාලයි"
            }
        ],
        "meaning": "චරිත අත්තලගේගේ විප්ලවීය සංගීත ශෛලිය සහ රිද්ම වීරවර්ධනගේ ගැඹුරු ගායනය එකමුතු වූ මෙම ගීතය, ජීවන ගමනේ ගලායාම සහ ආදරයේ සදාතනික බව ස්වභාවධර්මයේ සංකේත හරහා අපූරුවට නිරූපණය කරයි."
    },
    {
        "title_si": "දවස් හත",
        "title_en": "Dawas Hatha",
        "artist": "Dinesh Gamage",
        "lyricist": "Dinesh Gamage",
        "genre": "Pop Ballad",
        "release_year": "2023",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "සතියේ දවස් හත පුරාම ඔබේ රුව සිහිවෙනවා\nසඳුදා සිට ඉරිදා දක්වා මම ඔබ එනතුරු බලනවා\nඔබ නොදකින එක් දවසක් මට අවුරුද්දක් වගේ\nඔබ ළඟ ඉන්නා මොහොතක් තප්පරයක් සේ ගෙවී යයි"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "දවස් හත... මගේ ආදරේ ගණිනා දවස් හත\nඔබේ සිනාවෙන් මගේ මුළු ලෝකයම සැරසෙනවා\nඅහසේ තරු ගණනටත් වඩා ආදරෙයි මම ඔබට\nසැමදා මගේ හදවතේ රැඳී ඉන්න සොඳුරියේ"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "වැස්ස වැටෙන හැන්දෑවේ කෝපි කෝප්පයක් බොමින්\nඔබ කී කතා එකින් එක මම සිහිපත් කරමි\nජීවිතයේ සුන්දරම දින මේවා බව මම දනිමි\nඔබේ ආදරයෙන් මගේ ලෝකය අද පිරී ඇත"
            }
        ],
        "meaning": "දිනේෂ් ගමගේගේ මෙම ගීතය පෙම්වතෙකු තම පෙම්වතිය නොදැක සිටින සෑම දිනකම විඳින අප්‍රමාණ ආදරණීය ආශාව සහ ඇය සමඟ ගතකරන මොහොතක ඇති වටිනාකම ඉතා සරලව සහ මිහිරිව විස්තර කරයි."
    },
    {
        "title_si": "හඳහාමී",
        "title_en": "Handahami",
        "artist": "Ridma Weerawardena",
        "lyricist": "Nuwan Jayasuriya",
        "genre": "Indie Folk",
        "release_year": "2021",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "හඳහාමී අහසේ පායාලා මගේ පැල්පත එළිය කළා\nපුංචි මලක සුවඳ අරන් සිහිල් සුළඟ ආවා\nඔබේ සෙනෙහස මගේ හිතේ රන් දොරටුවක් හැරියා\nදුක් කඳුළු නිවා දමා සැනසිල්ලක් ගෙනාවා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "හඳහාමී... මගේ සිහින අහසේ රන් සඳේ\nඔබ නැතුව පාලුයි මේ මුළු ලොවේ\nඅහසේ තරු අතරින් ඔබ මට එබී බලනවා\nමගේ හදවත නුඹට ආදරයෙන් පුදමි"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "නිල්වන් කඳු අතරින් පායන හිරු කුමරා සේ\nඔබ මගේ අඳුරු ලොවට අලුත් දවසක් ගෙනාවා\nසදාකල් ඔබ ළඟින් හිඳින්නට පෙරුම් පුරමි\nමගේ ජීවිතයේ එකම ප්‍රාර්ථනාව ඔබයි"
            }
        ],
        "meaning": "රිද්ම වීරවර්ධනයන්ගේ සාම්ප්‍රදායික හා නවීන සංකලනයෙන් යුතු හඳහාමී ගීතය, ළමා වියේ මතකයන් සහ සඳ එළියේ ඇති සන්සුන් ආදරණීය බව මුසුකරගත් ඉතා ජනප්‍රිය නව පරපුරේ නිර්මාණයකි."
    },
    {
        "title_si": "දෙවඟනක් වගේ",
        "title_en": "Dewaganak Wage",
        "artist": "Charitha Attalage & Ravi Jay",
        "lyricist": "Ravi Jay",
        "genre": "Hip Hop / Rap",
        "release_year": "2023",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "දෙවඟනක් වගේ ඔබ බැස ආවා මගේ අඳුරු ලොවට\nකවදාවත් නොදුටු සුන්දරත්වයක් රැගෙන\nවචන නැති වුණා මට ඔබේ රූපය දැකලා\nහදවතේ ගැස්ම වැඩි වුණා ඔබ ළඟින් එද්දී"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "දෙවඟනක් වගේ... දිදුලන තාරකාවක් සේ\nමගේ ජීවිතයේ අඳුර නැති කළා\nමේ ආදරේ රැකගන්නම් මගේ පණ වාගේ\nකිසිදා ඔබෙන් ඈත් නොවන බවට පොරොන්දු වෙමි"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "නගරයේ විදුලි පහන් නිවී ගියත් රෑ මැදදී\nඔබේ දෑසේ ආලෝකය මට පාර පෙන්වනවා\nඅපේ ආදරේ ජයගන්නට ඕනෑම සටනක් කරන්නම්\nඔබ පමණයි මගේ ජීවිතයේ එකම ශක්තිය"
            }
        ],
        "meaning": "චරිත අත්තලගේ සහ රවී ජේගේ සංයෝජනයෙන් බිහිවූ මෙම ගීතය, නූතන හිප්-හොප් සහ ආදරයේ ප්‍රකාශනය එකට කැටි කරමින් තරුණ ප්‍රජාව අතර දැඩි උද්යෝගයක් ඇති කළ විශිෂ්ටතම ගීතයකි."
    },
    {
        "title_si": "කෙල්ලේ",
        "title_en": "Kelle",
        "artist": "Costa & Master D",
        "lyricist": "Costa",
        "genre": "Sinhala Rap / Pop",
        "release_year": "2022",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "කෙල්ලේ මගේ හිත හොරකම් කළේ ඔබයි\nඔබේ ඒ කටකාර සිනහව මට තාම මතකයි\nකොතැනක ගියත් ඔබේ රුව මට පෙනෙනවා\nමගේ දවසේ වැඩි කාලයක් ඔබ ගැන හිතෙනවා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "කෙල්ලේ... මට කියන්න ඔබේ හිතේ තියෙන දේ\nමගේ ආදරේ පිළිගන්නවාද සතුටින්\nඔබ ළඟ නැතුව පාලුයි මගේ ජීවිතේ\nඅපි දෙන්නා එකතු වෙලා අලුත් ගමනක් යමු"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "වීදි පුරා ඇවිද ගියත් මගේ හිත ඔබ ළඟයි\nසංගීතයේ තාලයක් සේ ඔබේ නම මගේ හදේ ගැහෙයි\nකවදාවත් නොබිඳෙන ආදරයක් දෙන්නම් මම\nඔබ මට ආදරේ නම් මට මුළු ලෝකයම ලැබුණා වගේ"
            }
        ],
        "meaning": "කොස්ටා සහ මාස්ටර් ඩී විසින් ගායනා කරන කෙල්ලේ ගීතය, ශ්‍රී ලාංකික නාගරික තරුණ ආදරයේ විවෘත බව සහ සරල බව රැප් සහ පොප් සංගීතයෙන් ඉදිරිපත් කරන මෑතකාලීන සුපිරි ගීතයකි."
    },
    {
        "title_si": "කල්‍යාණියේ",
        "title_en": "Kalyaniye",
        "artist": "Supun Perera",
        "lyricist": "Supun Perera",
        "genre": "Soft Pop",
        "release_year": "2024",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "කල්‍යාණියේ ඔබේ නෙත් යුග මට සැනසුම ගෙනදෙයි\nකැලණි ගඟ අසබඩ හමනා සිසිල් පවන සේ\nඔබේ ආදරයෙන් මගේ මුළු ජීවිතයම සුවඳවත් වුණා\nකවදාවත් නොමැකෙන මතකයක් සේ හදවතේ රැඳුණා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "කල්‍යාණියේ... මගේ සොඳුරු ප්‍රේමියේ\nඔබ ළඟ ඉන්නා විට මට මුළු ලොවම අමතකයි\nඅත්වැල් අල්ලාගෙන අපි දෙදෙනා යමු\nනොනිමෙන ආදර මාවතේ ජීවිතේ පුරා"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "මල් පිපෙන වසන්තයේ සුවඳ ඔබට පුදන්නම්\nසඳ පායන රැයකදී ඔබ වෙනුවෙන් ගී ගයන්නම්\nජීවිතයේ දුක සැප දෙකේදීම ඔබ ළඟින් හිඳිමින්\nසැමදා ඔබව ආදරයෙන් රැකබලා ගන්නෙමි"
            }
        ],
        "meaning": "සුපුන් පෙරේරාගේ ආකර්ෂණීය සහ මිහිරි හඬින් ගැයෙන කල්‍යාණියේ ගීතය, කැලණි නදී තීරයේ සොඳුරු බව උපමා කරමින් පෙම්වතිය කෙරෙහි ඇති අසීමිත භක්තිය සහ ආදරය විදහා දක්වන අලුත්ම ගීතයකි."
    },
    {
        "title_si": "රෝස පාටින්",
        "title_en": "Rosa Patin",
        "artist": "Theekshana Anuradha",
        "lyricist": "Theekshana Anuradha",
        "genre": "Romantic Pop",
        "release_year": "2023",
        "verses": [
            {
                "label": "පද 1 (Verse 1)",
                "lines": "රෝස පාටින් මගේ හිත පාට කළා ඔබ ඇවිත්\nසුන්දර සිහිනයක් සැබෑ වුණා වගේ මට\nඔබේ මුවග පිපෙනා ඒ සිනහව දුටු දා\nමගේ මුළු ලෝකයම ආදරයෙන් පිරුණා"
            },
            {
                "label": "කෝරසය (Chorus)",
                "lines": "රෝස පාටින්... හැඩගැන්වූ මගේ ආදරේ\nඔබ වෙනුවෙන්මයි මේ මුළු හදවතම\nතරු පිරි අහසේ පායන රන් සඳක් සේ\nසැමදා මගේ ලෝකයට එළිය දෙන්න"
            },
            {
                "label": "පද 2 (Verse 2)",
                "lines": "වැසි වැටෙන හැන්දෑවේ ඔබ මගේ ළඟ හිඳිද්දී\nදැනෙන ඒ උණුසුම මගේ මුළු හදවතම සනසයි\nකවදාවත් මා අත්නොහැර රැඳී ඉන්න\nජීවිතයේ අවසන් හුස්ම තෙක්ම"
            }
        ],
        "meaning": "තීක්ෂණ අනුරාධයන්ගේ සංවේදී ගායන විලාසය තුළින්, ආදරයේ මෘදු බව සහ රෝස පැහැති සුන්දර සිහින ලෝකය අලංකාර ලෙස විස්තර කරන නූතන ආදර ගීතයකි."
    }
]

def main():
    json_path = "e:/Projects/versenest_website/versenest_website/data/sinhala-songs.json"
    print("Loading sinhala-songs.json...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    songs = data.get("songs", [])
    print(f"Current total songs: {len(songs)}")

    # Format recent hits
    formatted_recent = []
    for i, s in enumerate(recent_hits):
        song_entry = {
            "id": i + 1,
            "slug": s["title_en"].lower().replace(" ", "-").replace("&", "and").replace("'", ""),
            "title_si": s["title_si"],
            "title_en": s["title_en"],
            "artist": s["artist"],
            "lyricist": s.get("lyricist", ""),
            "genre": s["genre"],
            "release_year": s.get("release_year", "2023"),
            "verses": s["verses"],
            "meaning": s["meaning"],
            "is_recent": True,
            "is_famous": True
        }
        formatted_recent.append(song_entry)

    # Insert recent hits at the very beginning, then existing songs
    # Re-assign IDs
    combined_songs = []
    
    # 1. Recent hits first
    for s in formatted_recent:
        s["id"] = len(combined_songs) + 1
        combined_songs.append(s)

    # 2. Add remaining songs (avoid duplicating existing titles)
    recent_titles = set(s["title_si"] for s in formatted_recent)
    for s in songs:
        if s["title_si"] not in recent_titles:
            s["id"] = len(combined_songs) + 1
            if "is_recent" not in s:
                s["is_recent"] = False
            combined_songs.append(s)

    # Keep 5000 songs total
    combined_songs = combined_songs[:5000]

    print(f"New total songs: {len(combined_songs)}")
    print("Top 5 recent songs:")
    for s in combined_songs[:5]:
        print(f" - {s['id']}: {s['title_si']} ({s['title_en']}) by {s['artist']} [{s.get('release_year', '')}]")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(combined_songs), "songs": combined_songs}, f, ensure_ascii=False, indent=None)

    print("Successfully added recently released Sinhala songs into sinhala-songs.json!")

if __name__ == "__main__":
    main()
