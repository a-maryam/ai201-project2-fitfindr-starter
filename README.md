# FitFindr 

## Tool Inventory 

|Tool name | Inputs  | Outputs | Purpose |
|--|--| -- | -- |
| parse_query | query (str) - this is user input | dict which contains the description (query), string that is the user size, float max_price which is the max they are willing to pay | Parses the query into desired parameters of description, size, and max_price if mentioned |
| search_listings | description (str), size (str), max_price (float) | list[dict] - list of listings of type dict| Returns top 8 listing matches for the query |
| suggest_outfit | new_item which was found by search_listings for their request (dict), the user's wardrobe (dict) | str - outfit | Returns a suggested outfit string or just general styling tips if wardrobe is empty |
|create_fit_card | outfit that was suggest by suggest_outfit (str), new_item which was found in listings (dict)| str - caption | Produces a caption which can be used on social media for the generated outfit. If a caption could not be generated, the listing and outfit suggestions are still given. |

## Planning Loop Explanation
The loop continues until session is returned. First, we parse the query. If at any time an error occurs and is stored in session, we exit the loop. We search results for the parsed fields. If there is an error in the search we direct the user to try again with new details. We select the top result, then we go to suggest_outfit with the top item and wardrobe in session. Then we create the fit card with our suggestion and the selected item. When all steps are complete, we return session. 

## State Management Approach: what is stored, when, and how it's passed between tools
1. session['parsed']: dict of size, description, max_price. This is stored when the query is parsed. The values of parsed are passed into searc_listings. 
2. session['query']: original user query. This is stored at the start of a new session. The query is passed to parse_query. 
3. session['search_results']: list of matching listing dicts. This stores the result of search_listings. The search results are saved in session and then top item is selected to be saved.
4. session['selected_items']: top result. This is stored after we select the top item from search results. This is passed to suggest_outfit.
5. session['wardrobe']: user's wardrobe dict. This is stored at session startup. Passed to suggest_outfit.
6. session['outfit_suggestion']: string returned by suggest_outfit. This is stored after we call suggest_outfit. Outfit suggestion is passed to create_fit_card.
7. session['fit_card']: string returned by create_fit_card. This is stored after we call create_fit_card. This is saved in session to be shown to user. 
8. session['error']: set if the interaction ended early. This is set when an error occurs at any point during the loop. This is saved in session and we end and ask the user if they want to query again.

## Error handling strategy for each tool with at least one concrete example
|Tool name | Error Handling  | Example (minimum of one) | 
|--|--| -- |
| parse_query  | If size and price are not found in the string we make them None | |
| search_listings | we check if price and/or size are None before checking against listing price and size. | |
| suggest_outfit  | if wardrobe empty we give general styling advice | |
| create_fit_card | if outfit is None or empty we give style suggestions instead | >> from tools import search_listings, suggest_outfit 
>> from utils.data_loader import get_example_wardrobe, get_empty_wardrobe   
>> results = search_listings('vintage graphic tee', size=None, max_price=50)
>> print(suggest_outfit(results[0], get_empty_wardrobe()))
>> "
This Y2K Baby Tee is perfect for creating a nostalgic, cottagecore-inspired look. To style it, pair with:

* High-waisted jeans or a flowy skirt for a feminine touch
* Distressed denim shorts for a casual, summery vibe
* A flowy cardigan or crochet top for a layered, whimsical look

The tee's fitted crop length makes it ideal for high-waisted bottoms. Consider adding neutral-colored shoes, like sneakers or sandals, to balance the playful butterfly graphic. This piece suits a soft, romantic aesthetic, making it great for everyday wear or a music festival-inspired look. Start building your wardrobe with this tee, then add complementary pieces like a denim jacket, a floppy hat, or layered necklaces to enhance the overall cottagecore vibe.|
## Spec Reflection
### How the spec helped you?
My spec was written very thoroughly so Claude was able to implement it accurately. I think my prompting the user to try again on failure was a little different from what the project expected so at times when Claude was looking at my spec and the todos it was getting confused. At those times, I had to push the AI to follow my spec. 
### How the implementation diverged? 
I was planning on having the outfit returned as a dict with all of the items, but the way the project was setup it made more sense to have it return as a string and be ready to return directly to the user. A dict would be more useful for a grander scale project. 

## AI Usage 
### Instance 1
#### What I gave it
Gave Claude the AI tool specifications and the guidelines in the function docstring to write create_outfit_card().

#### What it produced
It mostly implemented create_outfit_card() to spec but it was not writing the style suggestions we want if we only have new_item

#### What I adjusted**
Told Claude to adjust so that it gives style suggestions about the new item in the format of a string if there are problems with outfit passed to the function. 

### Instance 2
#### What I gave it
Implement run agent with planning loop and architecture diagram from planning.md. 

#### What it produced
First the agent misinterpreted and implemented the planning loop in agent.py linearly without the loop. 

#### What I adjusted
I told it to stick to the architecture diagram and write it as a loop. 

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
