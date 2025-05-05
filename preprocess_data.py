# import pandas as pd
# import random

# # Generate a sample dataset with 500 influencers
# categories = ['Tech', 'Fashion', 'Gaming', 'Fitness', 'Travel', 'Food']
# niches = ['Smartphones', 'Luxury Wear', 'PC Gaming', 'Weight Loss', 'Backpacking', 'Vegan Recipes']

# data = []
# for i in range(500):
#     category = random.choice(categories)
#     niche = random.choice(niches)
#     reach = random.randint(5000, 500000)  # Between 5K and 500K followers
#     engagement_rate = round(random.uniform(0.5, 10.0), 2)  # Between 0.5% and 10%
#     data.append([category, niche, reach, engagement_rate])

# df = pd.DataFrame(data, columns=['category', 'niche', 'reach', 'engagement_rate'])

# # Save to CSV
# df.to_csv("synthetic_influencer_data.csv", index=False)

# print("Synthetic dataset created successfully!")








import pandas as pd
import random
from faker import Faker

fake = Faker()

# Category-Niche mapping
category_niche_map = {
    "Tech": ["Smartphones", "Gadgets", "AI", "Reviews"],
    "Fashion": ["Luxury Wear", "Streetwear", "Sustainable Fashion"],
    "Gaming": ["PC Gaming", "Console Gaming", "Mobile Games"],
    "Fitness": ["Weight Loss", "Yoga", "Bodybuilding"],
    "Travel": ["Backpacking", "Luxury Travel", "Solo Travel"],
    "Food": ["Vegan Recipes", "BBQ", "Healthy Eating"]
}

platforms = ["Instagram", "YouTube", "TikTok", "Twitter", "Facebook"]

# Generate synthetic influencer data
data = []
for _ in range(500):
    category = random.choice(list(category_niche_map.keys()))
    niche = random.choice(category_niche_map[category])
    name = fake.name()
    email = fake.unique.email()
    platform = random.choice(platforms)
    followers = random.randint(5000, 1000000)
    reach = int(followers * random.uniform(0.2, 0.9))  # Reach as a % of followers
    engagement_rate = round(random.uniform(1.0, 10.0), 2)

    data.append([
        name,
        email,
        platform,
        category,
        niche,
        followers,
        reach,
        engagement_rate
    ])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "name",
    "email",
    "platform",
    "category",
    "niche",
    "followers",
    "reach",
    "engagement_rate"
])

# Save to CSV
df.to_csv("synthetic_influencer_data.csv", index=False)
print("✅ Enhanced synthetic influencer dataset created successfully!")
