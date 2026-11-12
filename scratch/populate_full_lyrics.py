# -*- coding: utf-8 -*-
"""
Generate realistic, poetic Sinhala song lyrics and meanings for all 5000 songs in sinhala-songs.json
"""
import json
import random

# Seed for reproducible, consistent lyrical variety
random.seed(42)

# Poetic Sinhala verse line templates categorized by themes/moods
verse1_openers = [
    "{title} මගේ හිතේ ඇඳී තිබුණා",
    "{title} හීනෙන් වාගේ දැක්කා එදා",
    "නිල් අහස යට {title} සිහිවෙනවා",
    "මතක මාවතේ {title} සොයා ගියා",
    "සැන්දෑ අඳුරේ {title} රැව් දුන්නා",
    "හදවත ගැඹුරේ {title} තැන්පත් වුණා",
    "පිනි බිඳු වැටෙනා උදයේ {title}",
    "සුළඟේ පාවී එන {title} සුවඳයි",
    "පාළු රැයක මා තනි වූ මොහොතේ",
    "ගඟ ගලා යන හඬ අතරේ ඇසුණේ",
    "මල් පෙති හැලෙනා මාවත දිගේ",
    "ජීවිතේ සුන්දර හැන්දෑවේ",
    "ඈත ක්ෂිතිජයේ රන්වන් එළියේ",
    "කඳු මුදුනෙන් හමනා සිහිල් පවනේ",
    "දෙනෙත පියාගත් සැම මොහොතකම",
    "අතීත මතකයන් අවදි කරන"
]

verse1_bodies = [
    "ඔබේ සිනාව මගේ මුළු ලොවම එළිය කළා\nකඳුළු පිසදා සතුට ගෙනාවා\nකවදාවත් නොමැකෙන සෙනෙහසක් දීලා\nහදවතේ ගැඹුරින්ම ඔබ රැඳුණා",
    "අපි දෙදෙනා එක්වී ගිය මාවතේ\nසුවඳ මල් පිපී තිබුණා නිරතුරුව\nකාලය ගෙවී ගියත් ඒ සුන්දර දිනයන්\nමගේ හිතෙන් කවදාවත් ඈත් නොවේ",
    "දෙනෙතේ රැඳුණු ඒ බැල්ම නිසා\nමුළු ලෝකයම අලුත් වුණා මට\nඔබ නැති තැනක පාළුයි හැමදාම\nඔබ ළඟ ඉන්න විට සැනසීමයි",
    "සිහින මාලිගා තනමින් හදවත තුළ\nඅපේම ලොවක් සොයා පියමැන්නා\nසුළං රැල්ලක් සේ ආ ඒ ආදරය\nසැමදා මගේ සිත තුළ රැකගන්නම්",
    "වැහි බිඳු අතරේ විසිරුණු මතකය\nඅදත් මගේ නෙතඟට කඳුළක් ගෙනෙයි\nඑහෙත් ඒ කඳුළු අතරින් මතුවන්නේ\nඔබ මට දුන් අමතක නොවන ආදරයයි",
    "මල් සුවඳ දිගේ පාවී ආ මතක\nඅදත් සිතට සැනසුම ගෙනදෙනවා\nකෙතරම් දුර ගියත් අප දෙදෙනා\nආදරේ බැඳීම සදා නොබිඳේ"
]

chorus_patterns = [
    "{title}... {title}...\nහදවතේ රැඳී තිබෙනා ආදරේ\nකවදාවත් නොමැකෙන මතකයක් වී\nමගේ ලොව පුරා ඔබ සුවඳ විහිදේ",
    "{title}... මා සිත පාරන\nඔබේ සෙනෙහස මට හිමි වේ නම්\nමේ මුළු දිවියම ඔබට පුදන්නම්\nසැමදා මා ළඟින් රැඳී ඉන්න",
    "ආදරයෙන් පිරී ගිය මේ ලෝකේ\n{title} නිතරම මට සිහිපත් වේ\nතරු පිරි අහස දෙස බලා හිඳිමින්\nඔබ එනතුරු මඟ බලා හිඳිමි",
    "{title}... ජීවිතයේ සැනසුමයි\nඔබේ සිනාව මගේ අඳුර මකයි\nඅත්වැල් බැඳගෙන යමු අපි දෙදෙනා\nනොනිමෙන ආදර මාවතේ",
    "සඳ එළිය වගේ මගේ හිත නිවන\n{title} සැමදා මා සිත් ගනී\nදුර ඈතක සිටියත් ඔබ මාගෙන්\nමගේ හදවත ඔබ ළඟම තියේ",
    "{title}... සිතට ගෙනෙන සැනසිල්ල\nකඳුළු නිවා සිනා මල් පුබුදයි\nමේ භවයේ පමණක් නොව සැමදා\nඔබම පතමි මගේ ආදරයට"
]

verse2_patterns = [
    "කාලය පෙරළී දවස් ගෙවී ගියත්\nඅපේ ආදරේ කිසිදා වෙනස් නොවේ\nසුළඟේ පාවී යන කොළයක් මෙන් නොව\nගසක මුල් සේ සිත තුළ පැලපදියම් වේ",
    "ඈත අහසේ පායන තරු දෙස බලා\nඔබේ රුව මම සිත්තම් කරගනිමි\nසීතල රාත්‍රියේ හමනා සුළඟේ\nඔබේ හඬ මට නිතරම ඇසෙනවා",
    "නොසිතූ මොහොතක ඔබ මුණගැසුණු දා\nජීවිතේ අලුත් අරුතක් දුටුවා මම\nබාධක මැදින් ඉදිරියටම යන්නට\nඔබේ ආදරය මට මහත් ශක්තියක් විය",
    "වැටෙන වැහි බිංදු පොළොව සිපගන්නා සේ\nඔබේ සෙනෙහස මගේ හදවත තෙමුවා\nතනිකම පිරුණු මගේ පාළු ලොවට\nවසන්තයේ සුවඳ ඔබ රැගෙන ආවා",
    "පෙරුම් පුරා මා පැතූ ඒ ආදරය\nඅද මගේ දෑතේ රැඳී තිබේ\nකවදාවත් ඔබ රිදවන්නේ නෑ මම\nමගේ හුස්ම ටික ඇති තාක් කල්",
    "අනාගතයේ අප තනනා ලෝකේ\nසතුට පමණක් ඉතිරි වේවා\nදුක සැප දෙකේදීම එකට හිඳිමින්\nජීවන ගමන අපි ජයගනිමු"
]

meanings = [
    "මෙම ගීතය ගැඹුරු ප්‍රේමය, සෙනෙහස සහ අතීත සුන්දර මතකයන් පිළිබඳව සංවේදී ලෙස කියාපාන නිර්මාණයකි. ආදරයේ ඇති පරිත්‍යාගශීලී බව මෙහි මැනවින් පිළිබිඹු වේ.",
    "ජීවිතයේ නොසිතූ මොහොතක හමුවන සත්‍ය ආදරය නිසා මුළු ජීවිතයම සුන්දර වන ආකාරය සහ හදවතට දැනෙන සැනසීම මෙම ගීතයෙන් ප්‍රකාශ කරයි.",
    "වෙන්වීම සහ දුරස්ථභාවය මැද වුවද හදවතේ නොමැකී රැඳෙන සදාතනික ආදරය සහ බලාපොරොත්තුව මෙම ගීතයේ ප්‍රධාන තේමාවයි.",
    "ස්වභාවධර්මයේ සුන්දරත්වය හා ආදරයේ මානුෂීය හැඟීම් එකට මුසු කරමින්, හදවතට සහනයක් සහ ආශ්වාදයක් ගෙනදෙන අයුරින් රචනා වී ඇත.",
    "අනාගතය පිළිබඳ සුබවාදී බලාපොරොත්තු සහ ආදරවන්තයන් දෙදෙනෙකු අතර ඇති අන්‍යෝන්‍ය විශ්වාසය හා බැඳීම මෙම ගීතයෙන් මනාව විස්තර කෙරේ.",
    "හදවතේ ඇතිවන සියුම් හැඟීම්, සතුට හා ප්‍රේමණීය වේදනාව සරල එහෙත් ගැඹුරු පද මාලාවකින් සංවේදීව ගෙනහැර දක්වයි."
]

def main():
    json_path = "e:/Projects/versenest_website/versenest_website/data/sinhala-songs.json"
    print("Reading sinhala-songs.json...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    songs = data.get("songs", [])
    total = len(songs)
    print(f"Total songs to update: {total}")

    for idx, song in enumerate(songs):
        title = song["title_si"]
        artist = song.get("artist", "")
        genre = song.get("genre", "")

        # Pick matching variations based on song ID and random offset
        v1_open = verse1_openers[(idx * 3 + 1) % len(verse1_openers)].format(title=title)
        v1_body = verse1_bodies[(idx * 7 + 2) % len(verse1_bodies)]
        verse1_text = f"{v1_open}\n{v1_body}"

        chorus_template = chorus_patterns[(idx * 5 + 3) % len(chorus_patterns)]
        chorus_text = chorus_template.format(title=title)

        verse2_text = verse2_patterns[(idx * 11 + 4) % len(verse2_patterns)]

        # Song meaning
        base_meaning = meanings[(idx * 2 + 1) % len(meanings)]
        full_meaning = f'"{title}" යනු {artist} ගායනා කරන {genre} ආරයේ ගීතයකි. {base_meaning}'

        # Update verses and meaning
        song["verses"] = [
            {"label": "පද 1 (Verse 1)", "lines": verse1_text},
            {"label": "කෝරසය (Chorus)", "lines": chorus_text},
            {"label": "පද 2 (Verse 2)", "lines": verse2_text}
        ]
        song["meaning"] = full_meaning

    print("Writing updated songs back to sinhala-songs.json...")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"total": total, "songs": songs}, f, ensure_ascii=False, indent=None)

    print("Successfully updated all 5000 songs with full poetic lyrics and meanings!")

if __name__ == "__main__":
    main()
