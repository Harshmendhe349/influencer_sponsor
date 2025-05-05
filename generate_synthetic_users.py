import random
from faker import Faker
from app import db, app
from app import Sponsor, Influencer, User

fake = Faker()

category_niche_map = {
    "Fashion": ["Streetwear", "Formalwear", "Sustainable Fashion", "Casual Wear", "Vintage", "Athleisure", "Accessories"],
    "Beauty": ["Makeup", "Skincare", "Haircare", "Nail Art", "Fragrance", "Beauty Tutorials"],
    "Fitness": ["Gym", "Yoga", "Home Workouts", "Bodybuilding", "CrossFit", "Pilates", "HIIT"],
    "Health": ["Nutrition", "Mental Health", "Wellness", "Holistic Health", "Supplements", "Chronic Illness Support"],
    "Lifestyle": ["Minimalism", "Home Decor", "Self Improvement", "Daily Vlogs", "Routines", "Life Hacks"],
    "Food": ["Baking", "Vegan", "BBQ", "Healthy Eating", "Street Food", "Fine Dining", "Meal Prep"],
    "Travel": ["Luxury Travel", "Budget Travel", "Adventure", "Cultural Travel", "Road Trips", "Travel Vlogs"],
    "Tech": ["Gadgets", "Coding", "Reviews", "Tech News", "AI & ML", "Cybersecurity", "Startups"],
    "Gaming": ["Console", "PC", "Mobile", "Streaming", "Esports", "Game Reviews", "Walkthroughs"],
    "Photography": ["Portraits", "Nature", "Urban", "Weddings", "Aerial", "Photography Tips"],
    "Parenting": ["Toddler Tips", "Teen Parenting", "Mom Hacks", "Single Parenting", "Educational Activities"],
    "Education": ["STEM", "Language Learning", "Productivity", "Study Tips", "E-Learning", "Career Guidance"],
    "Finance": ["Investing", "Saving", "Crypto", "Budgeting", "Real Estate", "Personal Finance"],
    "Music": ["Singing", "Instruments", "Production", "Music Reviews", "Covers", "Behind the Scenes"],
    "Art": ["Painting", "Digital Art", "Crafts", "Calligraphy", "Sculpture", "Art Vlogs"],
    "Comedy": ["Skits", "Stand-Up", "Memes", "Funny Reactions", "Parody", "Impressions"],
    "Books": ["Reviews", "Recommendations", "Book Clubs", "Reading Challenges", "Author Interviews"],
    "Movies": ["Reviews", "Analysis", "Behind the Scenes", "Fan Theories", "Movie News"],
    "Cars": ["Luxury", "Modding", "Electric Vehicles", "Car Reviews", "Test Drives"],
    "Sports": ["Football", "Basketball", "Running", "Cricket", "Martial Arts", "Extreme Sports"],
    "DIY": ["Home Projects", "Upcycling", "Crafting", "Decor Projects", "Tool Reviews"],
    "Spirituality": ["Meditation", "Astrology", "Mindfulness", "Healing Crystals", "Manifestation"],
    "Animals": ["Pet Training", "Exotic Pets", "Pet Care", "Funny Animals"],
    "Nature": ["Hiking", "Wildlife", "Conservation", "Eco-Friendly Living"],
    "Real Estate": ["House Tours", "Real Estate Tips", "Interior Design", "Investment Properties"],
    "Automotive": ["Motorcycles", "Racing", "Repairs & DIY", "Off-Roading"],
    "Interior Design": ["Home Makeovers", "Tiny Houses", "Space Optimization", "Furniture Hacks"],
    "History": ["Historical Facts", "Ancient Civilizations", "War History", "Timeline Series"],
    "Science": ["Physics", "Biology", "Space", "Experiments", "Science News"],
    "News & Politics": ["Current Events", "Commentary", "Debates", "Activism"],
    "Technology Education": ["How-to Guides", "Coding Tutorials", "Data Science", "Tech Reviews"],
    "Anime": ["Reviews", "Fan Art", "Cosplay", "Top Lists"],
    "Fashion Design": ["Sewing", "Behind the Scenes", "Design Tutorials"],
    "Esports": ["Tournaments", "Player Profiles", "Strategy Guides"],
    "Languages": ["Spanish", "French", "Mandarin", "Language Hacks"],
    "Weddings": ["Planning Tips", "Dresses", "Photography", "Event Decor"],
    "Interior Plants": ["Plant Care", "Indoor Gardening", "Terrariums"],
    "Sustainability": ["Zero Waste", "Eco Hacks", "Plastic-Free Living"],
    "Craft Beverages": ["Coffee Brewing", "Tea Culture", "Mixology", "Craft Beer"],
    "Luxury Lifestyle": ["Watches", "Cars", "Jets", "Yachts"],
    "Culture": ["Traditions", "Languages", "Travel Stories", "Festivals"],
    "Adventure": ["Rock Climbing", "Scuba Diving", "Paragliding", "Skydiving"],
    "Home Improvement": ["DIY Renovations", "Tool Reviews", "Smart Home"],
    "Interior Architecture": ["Layouts", "Space Planning", "Mood Boards"],
    "Green Living": ["Solar Power", "Composting", "Green Tech"]
}


platforms = [
    "Instagram", "YouTube", "TikTok", "Twitter", "Facebook", 
    "LinkedIn", "Pinterest", "Snapchat", "Twitch", "Reddit"
]

industries = [
    "Tech", "Fashion", "Food", "Fitness", "Beauty", "Finance", "Travel", 
    "Health", "Education", "Entertainment", "Gaming", "Real Estate", 
    "Automotive", "Media", "E-commerce", "Publishing"
]


def create_sponsors(n=1000):
    """Generate synthetic sponsors with valid user_id."""
    users = User.query.all()
    if not users:
        print("No users found! Please create users first.")
        return

    for _ in range(n):
        user = random.choice(users)
        sponsor = Sponsor(
            user_id=user.id,
            name=fake.name(),
            email=fake.email(),
            company=fake.company(),
            company_name=fake.company(),
            industry=random.choice(industries),
            budget=random.randint(5000, 50000),
            campaign_goals=fake.sentence(nb_words=6)
        )
        db.session.add(sponsor)

    try:
        db.session.commit()
        print(f"{n} sponsors added successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sponsors: {str(e)}")


def create_influencers(n=5000):
    """Generate synthetic influencers with valid user_id."""
    users = User.query.all()
    if not users:
        print("No users found! Please create users first.")
        return

    for _ in range(n):
        user = random.choice(users)
        category = random.choice(list(category_niche_map.keys()))
        niche = random.choice(category_niche_map[category])
        platform = random.choice(platforms)
        influencer = Influencer(
            user_id=user.id,
            name=fake.name(),
            email=fake.email(),
            category=category,
            platform=platform,
            niche=niche,
            reach=random.randint(5000, 1000000),
            followers=random.randint(5000, 1500000),
            engagement_rate=round(random.uniform(1.0, 10.0), 2)
        )
        db.session.add(influencer)

    try:
        db.session.commit()
        print(f"{n} influencers added successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding influencers: {str(e)}")


if __name__ == "__main__":
    with app.app_context():
        create_sponsors(100)
        create_influencers(500)
