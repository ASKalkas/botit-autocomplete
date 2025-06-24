from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
load_dotenv(override=True)
import os, time, uvicorn, json, pickle

UNIQUE_DIR = os.getenv("UNIQUE_DIR")
JSON_DIR = os.getenv("JSON_DIR")
PKL_PATH = os.getenv("PKL_PATH")

lexicon: list[str] = []
freq: dict[str, int] = {}
last_deleted_item: dict | None = None

class ItemModel(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    shopping_category: str
    shopping_subcategory: str
    item_category: str
    item_subcategory: str
    tags_dsw: List[str]
    tags_gsw: List[str]


    class Config:
        extra = "forbid"                     # reject unknown fields
        validate_by_name = True

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

def get_autocomplete(prefix):
    left, right = prefix_range(lexicon, prefix)
    return lexicon[left:right]

def _load_json() -> list: 
    """Return the current list of items (empty if file missing).""" 
    if os.path.exists(JSON_DIR): 
        with open(JSON_DIR, "r", encoding="utf-8") as f: 
            return json.load(f)
        
def _save_json(data: list) -> None: 
    """Pretty-print the list back to JSON.""" 
    with open(JSON_DIR, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

def _repickle(data: list) -> None: 
    """Overwrite the .pkl version using highest protocol.""" 
    with open(PKL_PATH, "wb") as f: 
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL) # [[5]]

def flatten_item(item: dict) -> list:
    item_list = []

    for key in item.keys():
        if isinstance(item[key], str): item_list.append(item[key])
        elif isinstance(item[key], list): 
            for s in item[key]:
                if isinstance(s, str): item_list.append(s)

    return item_list

app = FastAPI(title="Autocomplete")

@app.get("/autocomplete")
async def autocomplete(prefix: str, top: int = 10):
    if not prefix:
        raise HTTPException(status_code=400, detail="prefix required")
    words = get_autocomplete(prefix)
    words.sort(key=freq.get, reverse=True)
    if not words:
        raise HTTPException(status_code=404, detail="no matches")
    return words[:top]

@app.post("/add_item")
async def add_item(item:ItemModel):
    for s in flatten_item(item.model_dump(by_alias=True)):
        if s in freq:
            freq[s] += 1
        else:
            lexicon.append(s)
            freq[s] = 1

    items = _load_json()
    items.append(item.model_dump(by_alias=True))
    _save_json(items)
    _repickle(items)


@app.delete("/delete/{item_id}", status_code=204)
async def delete_item(item_id: str):
    """
    Remove the item whose *id* field equals `item_id`.
    Re-write both store.json and store.pkl.
    """
    items = _load_json()

    deleted = next((it for it in items if it.get("_id") == item_id), None)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for s in flatten_item(deleted):
        if s in freq:
            freq[s] -= 0
            if freq[s] == 0:
                lexicon.remove(s)
                freq.pop(s)

    # assume every item is a dict that contains an integer field called "id"
    remaining = [it for it in items if it.get("_id") != item_id]


    if len(remaining) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")


    _save_json(remaining)
    _repickle(remaining)

    return Response(status_code=200)


if __name__ == "__main__":
    print(freq["fashion"])
    uvicorn.run("autocomplete:app", host="0.0.0.0", port=8000, reload=True)