from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv(override=True)
import os, time, uvicorn

UNIQUE_DIR = os.getenv("UNIQUE_DIR")

lexicon: list[str] = []
freq: dict[str, int] = {}

with open(UNIQUE_DIR, encoding="utf-8") as fh:
    for raw in fh:
        if not raw.strip():
            continue
        word, *rest = raw.split(",")
        word = word.strip().lower()
        count = int(rest[0]) if rest else 0
        lexicon.append(word)
        freq[word] = count


lexicon.sort()   

def prefix_range(words, prefix):
    # Find range of words matching the prefix
    import bisect
    
    left = bisect.bisect_left(words, prefix)
    def next_prefix(s):
        if not s: return s
        s_list = list(s)
        for i in range(len(s_list)-1, -1, -1):
            if s_list[i] != 'z':
                s_list[i] = chr(ord(s_list[i]) + 1)
                return ''.join(s_list[:i+1])
        return s + 'a'
    right = bisect.bisect_left(words, next_prefix(prefix))
    return left, right

# Function to get autocomplete suggestions
def get_autocomplete(prefix):
    left, right = prefix_range(lexicon, prefix)
    return lexicon[left:right]

app = FastAPI(title="Autocomplete")


@app.get("/autocomplete")
def autocomplete(prefix: str, top: int = 10):
    if not prefix:
        raise HTTPException(status_code=400, detail="prefix required")
    words = get_autocomplete(prefix)
    words.sort(key=freq.get, reverse=True)
    if not words:
        raise HTTPException(status_code=404, detail="no matches")
    return words[:top]


if __name__ == "__main__":
    # quick test when run as script
    print(autocomplete("was"))
    uvicorn.run("autocomplete:app", host="0.0.0.0", port=8000, reload=True)