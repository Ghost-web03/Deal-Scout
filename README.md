# 🛍️ Deal Scout — Buy or Pass?

Hi, I'm Hala — this is my solo project for the SerpApi India Hackathon 2026.

I'm a first-year BCA student, and honestly, I'd never used SerpApi before this hackathon. I wanted to build something for a problem I run into all the time: seeing a product online and having no real way to tell if the price is actually good, or if I'm about to fall for an inflated "discount."

That's what Deal Scout does. You search for a product — by typing the name or just uploading a photo — and it pulls real prices from Google Shopping, checks the ratings and reviews, and gives you a straight BUY or PASS, with actual reasons, instead of just a pile of numbers you have to figure out yourself.

## What it does

- Search by typing a product name, or upload/take a photo and let it figure out what it is
- Pulls live prices from multiple sellers using SerpApi (Google Shopping + Google Immersive Product)
- Gemini reads the price, rating, and reviews and gives an honest BUY/PASS verdict with a score out of 100, plus real pros and cons
- An "Ask Deal Scout" section where you can tap through quick questions (why this price, who's cheapest, what do reviews say) — these don't use any extra AI calls, they just reuse data already fetched
- Keeps a history of what you've searched and lets you save deals you like, right in the sidebar
- If you search by photo, it skips straight to the closest match instead of making you guess from a list of names

## Why I built it this way

Most price comparison tools just show you numbers and leave the deciding part to you. I wanted the AI to actually do that part — look at the price next to the rating and reviews and tell you plainly if it's worth it. And since I was on Gemini's free tier (only 20 requests a day!), I had to think carefully about which features actually needed a fresh AI call and which could just reuse data I already had. That's why the FAQ questions and the alternatives section don't cost anything extra — I couldn't afford for them to.

## Built with

- Streamlit for the interface
- SerpApi for real shopping data (Google Shopping + Google Immersive Product engines)
- Google Gemini for identifying products from photos and for the verdict/scoring

## How it works

1. You type a product or upload a photo
2. If it's a photo, Gemini Vision figures out what it is
3. SerpApi finds real listings in India (₹)
4. SerpApi's Immersive Product engine pulls ratings, reviews, and seller prices
5. Gemini turns all of that into one verdict — score, summary, pros, cons — in a single API call
6. You get the full picture on one screen: the product, the reviews, the verdict, where to buy it, and a few alternatives

## Running it

```bash
pip install streamlit google-search-results google-genai pillow
streamlit run app.py
```

You'll need your own SerpApi and Gemini API keys. (Note to self: move these out of the code and into environment variables before making the repo public!)

## Known limitations

- Gemini's free tier only allows 20 requests a day per model. I hit this a lot while testing, so I made sure the app handles it properly — it tells you clearly when it's a quota issue instead of throwing a confusing error.
- Photo search works by having Gemini describe the image in words, then text-searching Google Shopping for that description — it isn't true reverse-image search. So it's great at getting the right category, color, and style, but it can't guarantee finding the *exact* listing if the specific product isn't well-indexed under matching text, or if a seller's own listing is mislabeled. Text search doesn't have this limitation.


