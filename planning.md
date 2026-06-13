# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches listings dataset and returns matching items. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->


**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Tell user we were not able to find good listing matches. Ask user to try a new prompt.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes a new item and the user's wardrobe and suggests one or more outfit combinations.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): map of item with keys into different features of the item. What we will be suggesting an outfit against.
- `wardrobe` (dict): the users current wardrobe (full of items with descriptions)

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Gives a short description of a full outfit that is shareable. Must be different 
each time for different inputs. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
``` mermaid
flowchart TD
    User([User query:<br/>description, size, max_price])
    User --> PL[Planning Loop]

    PL -->|"description, size, max_price"| Search["search_listings(description, size, max_price)<br/>Searches mock listings dataset"]

    Search --> CheckEmpty{results empty?}

    CheckEmpty -->|"results = [ ]"| Err["[ERROR] session.error =<br/>No listings found. Try a higher<br/>price or different size."]

    CheckEmpty -->|"results = [item, ...]"| S1[["Session state:<br/>selected_item = results[0]"]]
    S1 -->|"selected_item, wardrobe"| Suggest["suggest_outfit(new_item, wardrobe)"]

    Suggest --> WardrobeCheck{wardrobe empty?}
    WardrobeCheck -->|"yes"| GeneralAdvice["General styling advice"]
    WardrobeCheck -->|"no"| FullOutfit["Full outfit combos"]
    GeneralAdvice --> S2[["Session state:<br/>outfit_suggestion = '...'"]]
    FullOutfit --> S2

    S2 -->|"outfit_suggestion, selected_item"| FitCard["create_fit_card(outfit, new_item)"]
    FitCard --> S3[["Session state:<br/>fit_card = '...'"]]

    Err --> Continue{Continue<br/>conversation?}
    S3 --> Continue
    Continue -.->|"Yes: new query"| User
    Continue -->|No| End([Return session / End])
```
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---


## Design
## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I am size M. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent calls search_listing with the params. It loads up the listings from the dataset and filters by description, size, and price. 

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
Agent returns the top k listings by relevance. We select the top result. If results of search are empty: agent will tell the user to try a different description or change other requirements. Agent stops if results are empty.

We call suggest_outfit(new_item=selected_item, wardrobe=wardrobe) using the item stored in session and the wardrobe loaded at startup. 

Agent stores result as outfit_suggestion in session. 

If wardrobe is empty we offer general styling advice. 

If suggest_outfit fails or returns nothing we tell the user we couldn't generate a suggestion and then asks user if they would like to try to find a new outfit. This is not in the diagram (will be listed under error-handling).

Store outfit suggestion. 
**Step 3:**
<!-- Continue until the full interaction is complete -->
Agent calls create_fit_card with outfit_suggestion and new_item which are stored in the session. Agent stores result as fit_card in the session and displays it to user: "thrifted this faded band tee off of depop for $22 and it looks amazing with levi's."

**Final output to user:**
<!-- What does the user actually see at the end? -->
User receives matched listing from step 1, outfit suggestion from step 2 and the shareable fit card from step 3. If search listing fails, user will be prompted to try again with different parameters. If wardrobe is empty, general styling advice will be offered. If suggest outfit fails, prompt the user to try searching for something different.