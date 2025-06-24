# Overview

This autocomplete feature, utilizes a series of binary searches on an alphabetically sorted list of strings, representing the items. The purpose of the binary searches is to find the upper and lower bounds of the position of a prefix input, a slice of the list is then returned carrying all the strings that carry this input as a prefix.

# Project Setup and Usage Guide

## 📂 Directory Setup

Ensure `service.json` and `.env` files are present.

**Purpose**:
- `service.json`: holds the service account used for the dvc
- `.env`: holds the environmental variables needed

## 🐳 Run the Container
Start the service with:
```bash
docker compose up autocomplete --build
```
**This will**:
1. Build the autocomplete service
3. Expose port 8000

---

## 🌐 APIs
### 1- Auto-complete Inference
**Endpoint**: 
```plaintext
http://0.0.0.0:8000/autocomplete
```

#### Parameters
- `prefix`: the autocomplete query
- `top`: number that represents the top n results needed

#### Response (JSON):
```plaintext
Just a list of the top n autocomplete results
```

### 2- Add Item
**Endpoint**:
```plaintext
http://0.0.0.0:8000/add_item
```

#### Body
```plaintext
{
    "_id": str, MongoID of the item,
    "name": str,
    "shopping_category": str,
    "shopping_subcategory": str,
    "item_category": str,
    "item_subcategory": str,
    "tags_dsw": [str],
    "tags_gsw": [str]
}
```

### 3- Delete Item
**Endpoint**:
```plaintext
http://0.0.0.0:8000/delete/{itemID}
```
---

## 🔍 Test Connection with Postman
1. **Create a new WebSocket request**:
   - Open Postman > File > New > http GET Request

2. **Enter URL**:
```plaintext
http://0.0.0.0:8000/autocomplete?prefix=ca
```

3. **Send messages**:
   - Type your query after `prefix=`
   - Click "Send"

4. **View responses**:
   - JSON responses will appear in the "Messages" panel
