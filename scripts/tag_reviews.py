# Tag script: assigns tags to each review based on the words in its review_text.
#
# How it works:
#   1. Each tag in the Tag Guide has a list of keywords (TAG_KEYWORDS below).
#   2. For every review, the script looks for those keywords in the review text.
#   3. A tag is given only if one of its keywords appears in that review.
#   4. Tags are ordered by where their keyword first appears, and capped at 3.
#   A review that mentions none of the keywords (e.g. "just horrible") gets no tags.
#
# Run from the repository root:
#   python -m scripts.tag_reviews data/first_100_movies_with_reviews.csv
# The file is updated in place: the "tags" column is replaced with the script's tags.

import csv
import re
import sys

MAX_TAGS = 3

# Tag Guide: tag -> keywords that must appear in the review text
TAG_KEYWORDS = {
    "acting": ["acting", "actor", "actress", "performance", "performances", "cast"],
    "story": ["story", "stories", "plot", "premise", "idea", "concept", "predictable", "generic",
              "narrative", "narratively", "screenplay", "flashbacks", "lost me", "twist",
              "mystery", "sequel", "topic", "satire", "nothing new", "same old", "typical"],
    "ending": ["ending", "the end", "third act"],
    "pacing": ["slow", "slowly", "draggy", "drags", "drag", "pacing", "boring", "tense",
               "tension", "forgettable", "rhythm", "momentum", "a bit long", "deliberate",
               "unhurried", "halfway"],
    "visuals": ["visual", "visuals", "animation", "cinematography", "look good", "look a bit", "looks", "looking",
                "setting", "views", "design", "palette", "beautiful", "budget"],
    "music": ["music", "singing", "song", "songs", "soundtrack", "27 club"],
    "funny": ["funny", "fun", "comedy", "comedies", "comic", "hilarious", "laughed", "lol",
              "humour", "romcom", "silly", "jokes", "satirical", "absurdist", "😂"],
    "scary": ["scary", "creepy", "horror", "jump scares", "gory", "haunted", "disturbing",
              "zombie", "dread", "claustrophobia", "ghost", "spirit", "possessed", "exorcism", "👻"],
    "emotional": ["emotional", "sad", "touching", "heartbreaking", "inspiring", "moving",
                  "tear", "tissues", "heartwarming", "hit hard", "hits hard", "hard to watch",
                  "painful", "poignancy", "trauma", "tragedy", "grief", "depressing", "devastating", "broke me",
                  "wholesome", "bleak", "sweet"],
    "action": ["action", "fight", "fights", "chase", "chases", "explosions", "violent",
               "sword", "siege", "war film", "stunts"],
    "family": ["family movie", "for the family", "for kids", "kids", "children"],
    "characters": ["characters", "character study", "friendship", "friends", "couple",
                   "brothers", "grandma", "leads", "teacher", "patient", "father-son",
                   "dynamic", "heroine", "protagonist", "girls", "relationship"],
    "realistic": ["feels real", "feel real", "feel more real", "very real", "too real",
                  "so real", "real look", "true story", "relatable", "history", "surreal",
                  "authenticity", "verisimilitude", "covid", "docudrama"],
    "rewatchable": ["rewatch", "rewatchable", "rewatched", "watch again", "classic"],
    "overrated": ["overrated", "hype", "worse than"],
}


# Returns the position of the first keyword match in the text, or -1 if none
def first_match_position(text, keywords):
    best = -1
    for keyword in keywords:
        # \b = word boundary, so "act" does not match inside "fact"
        pattern = r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])"
        match = re.search(pattern, text)
        if match:
            if best == -1 or match.start() < best:
                best = match.start()
    return best


def tags_for_review(review_text):
    text = review_text.lower()
    found = []
    for tag in TAG_KEYWORDS:
        position = first_match_position(text, TAG_KEYWORDS[tag])
        if position != -1:
            found.append((position, tag))

    found.sort()
    tags = []
    for position, tag in found:
        if len(tags) < MAX_TAGS:
            tags.append(tag)
    return tags


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = []
        for row in reader:
            rows.append(row)

    changed = 0
    untagged = 0
    for row in rows:
        if row["review_text"].strip() == "":
            continue
        new_tags = ";".join(tags_for_review(row["review_text"]))
        if new_tags != row["tags"]:
            changed = changed + 1
        if new_tags == "":
            untagged = untagged + 1
        row["tags"] = new_tags

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Tagged {len(rows)} rows | tags changed: {changed} | reviews with no tags: {untagged}")


if __name__ == "__main__":
    main()
