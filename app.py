import random
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import Session
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import joblib
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from werkzeug.security import generate_password_hash
from recommendation_model import RecommendationEngine




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '619619'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # <-- Ensure this is added


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'get_login'  # Redirect to login page if not authenticated

# ==================================
# Load the trained model
model = joblib.load("trained_model.pkl")
print("Model loaded successfully!")
# ====================================

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # e.g., 'pending', 'accepted', 'rejected'
    terms = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    influencer = db.relationship('User', foreign_keys=[influencer_id], back_populates='ad_requests')
    campaign = db.relationship('Campaign', back_populates='ad_requests')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Role can be 'admin', 'sponsor', or 'influencer'
    campaigns = db.relationship('Campaign', back_populates='sponsor', lazy=True)
    ad_requests = db.relationship('AdRequest', foreign_keys=[AdRequest.influencer_id], back_populates='influencer', lazy=True)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(200), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Sponsor(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100))
    company_name = db.Column(db.String(200), nullable=True)
    individual_name = db.Column(db.String(200), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    budget = db.Column(db.Float, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    company = db.Column(db.String(100), nullable=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.relationship('User', backref=db.backref('sponsor', uselist=False))
    campaign_goals = db.Column(db.Text, nullable=True)
    
    

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    platform = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(200), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('influencer', uselist=False))
    followers = db.Column(db.Integer, nullable=False)
    engagement_rate = db.Column(db.Float, nullable=False)



class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_private = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', back_populates='campaign', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sponsor = db.relationship('User', back_populates='campaigns')
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(200), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('INDEX1.html')

@app.route('/', methods=['GET'])
@login_required
def get_home():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def get_login():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']  # Get the role from the form

    user = User.query.filter_by(email=email, role=role).first()  # Check user by email and role

    if user and check_password_hash(user.password, password):
        login_user(user)
        flash('Login successful!', 'success')

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'sponsor':
            return redirect(url_for('sponsor_dashboard'))
        elif user.role == 'influencer':
            return redirect(url_for('influencer_dashboard'))

    flash('Invalid credentials or role, please try again.', 'danger')
    return redirect(url_for('get_login'))

# @app.route('/signup', methods=['POST'])
# def signup_post():
#     username = request.form['username']
#     email = request.form['email']
#     password = request.form['password']
#     role = request.form.get('role', 'influencer')  # Default to 'influencer' if not provided

#     if User.query.filter_by(email=email).first():
#         flash('Email address already in use.', 'warning')
#         return redirect(url_for('get_signup'))

#     if User.query.filter_by(username=username).first():
#         flash('Username already in use.', 'warning')
#         return redirect(url_for('get_signup'))

#     hashed_password = generate_password_hash(password)
#     user = User(username=username, email=email, password=hashed_password, role=role)
#     db.session.add(user)
#     db.session.commit()

#     if role == 'sponsor':
#         company_name = request.form.get('company_name')
#         individual_name = request.form.get('individual_name')
#         industry = request.form.get('industry')
#         budget = request.form.get('budget')
#         sponsor = Sponsor(user_id=user.id, company_name=company_name, individual_name=individual_name, industry=industry, budget=budget)
#         db.session.add(sponsor)
#         db.session.commit()
#     elif role == 'influencer':
#         name = request.form['name']
#         category = request.form['category']
#         niche = request.form['niche']
#         reach = int(request.form['reach'])
#         influencer = Influencer(user_id=user.id, name=name, category=category, niche=niche, reach=reach)
#         db.session.add(influencer)
#         db.session.commit()

#     login_user(user)
#     flash('Signup successful! You are now logged in.', 'success')
#     # Redirect based on role
#     if role == 'admin':
#         return redirect(url_for('admin_dashboard'))
#     elif role == 'sponsor':
#         return redirect(url_for('sponsor_dashboard'))
#     elif role == 'influencer':
#         return redirect(url_for('influencer_dashboard'))

@app.route('/signup', methods=['POST'])
def signup_post():
    # Common user fields
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'influencer')  # Default to influencer
    name = request.form.get('full_name', username)

    # Check if user exists
    if User.query.filter_by(email=email).first():
        flash('Email address already in use.', 'warning')
        return redirect(url_for('get_signup'))
    if User.query.filter_by(username=username).first():
        flash('Username already in use.', 'warning')
        return redirect(url_for('get_signup'))

    # Create and save user
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    print("---- Form Data Received ----")
    for key, value in request.form.items():
        print(f"{key}: {value}")
    print("----------------------------")

    # Role-specific logic
    if role == 'sponsor':
        try:
            brand_name = request.form.get('brand_name')
            company_type = request.form.get('company_type')
            campaign_goals = request.form.get('campaign_goals', '')
            # Optional: budget, company_name, etc.
            sponsor = Sponsor(
                user_id=user.id,
                name=brand_name or name,
                email=email,
                company_name=brand_name,
                industry=company_type,
                category=company_type,
                budget=None,  # Add budget if you collect it in the form
                company=brand_name or company_type or "N/A",
                campaign_goals=campaign_goals
            )
            print("---- Form Data Received ----")
            for key, value in request.form.items():
                print(f"{key}: {value}")
            print("----------------------------")

            db.session.add(sponsor)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating sponsor: {str(e)}")
            flash('Sponsor registration failed. Please try again.', 'danger')
            return redirect(url_for('get_signup'))

    elif role == 'influencer':
        category = request.form.get('category') or request.form.get('influencer_category')
        niche = request.form.get('niche')
        platform = request.form.get('platform')
        audience_size = request.form.get('audience_size', '0')
        try:
            audience_size_int = int(audience_size)
        except ValueError:
            audience_size_int = 0
        influencer = Influencer(
            user_id=user.id,
            name=name,
            email=email,
            category=category,
            niche=niche,
            platform=platform,
            reach=audience_size_int,
            followers=audience_size_int,
            engagement_rate=round(random.uniform(2.5, 10.0), 2)
        )
        print("---- Form Data Received ----")
        for key, value in request.form.items():
            print(f"{key}: {value}")
        print("----------------------------")
        db.session.add(influencer)
        db.session.commit()

    # Auto login after signup
    login_user(user)
    flash('Signup successful! You are now logged in.', 'success')

    # Redirect to appropriate dashboard
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'sponsor':
        return redirect(url_for('sponsor_dashboard'))
    else:
        return redirect(url_for('influencer_dashboard'))


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('get_login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))
    
    # Querying the database for statistics
    active_users = User.query.count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(is_private=False).count()  # Corrected line
    private_campaigns = Campaign.query.filter_by(is_private=True).count()  # Corrected line
    ad_requests = AdRequest.query.all()
    users = User.query.all()
    campaigns = Campaign.query.all()

    return render_template('admin_dashboard.html',
                           active_users=active_users,
                           total_campaigns=total_campaigns,
                           public_campaigns=public_campaigns,
                           private_campaigns=private_campaigns,
                           ad_requests=ad_requests,
                           users=users,
                           campaigns=campaigns)


@app.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))
    
    campaigns = current_user.campaigns
    # Enrich ad requests with influencer profiles
    for campaign in campaigns:
        for ad_request in campaign.ad_requests:
            # Attach the Influencer profile to each ad_request
            influencer_profile = Influencer.query.filter_by(user_id=ad_request.influencer_id).first()
            ad_request.influencer_profile = influencer_profile  # Add as a dynamic attribute

    return render_template('sponsor_dashboard.html', campaigns=campaigns)

@app.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))
    
    ad_requests = current_user.ad_requests
    return render_template('influencer_dashboard.html', ad_requests=ad_requests)


@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        if not request.form.get('agree_terms'):
            flash('You must agree to the Terms & Conditions to create a campaign.', 'danger')
            return redirect(url_for('create_campaign'))
        title = request.form['title']
        description = request.form.get('description')
        budget = float(request.form['budget'])
        category = request.form['category']
        sponsor_id = current_user.id
        
        
        campaign = Campaign(title=title, description=description, budget=budget, category=category, sponsor_id=sponsor_id)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('my_campaigns'))
    return render_template('create_campaign.html')

@app.route('/search_influencers', methods=['GET'])
@login_required
def search_influencers():
    budget_str = request.args.get('budget')
    category = request.args.get('category')
    campaign_id = request.args.get('campaign_id')  # Get campaign_id from query parameters
    budget = None
    print(f"Budget String: {budget_str}")
    print(f"Category: {category}")
    print(f"Campaign ID: {campaign_id}")
    
    if budget_str:
        try:
            budget = float(budget_str)
        except ValueError:
            flash('Invalid budget value.', 'danger')
            return redirect(url_for('search_influencers', campaign_id=campaign_id))

    # Adjust query to handle budget and category
    if budget is not None and category:
        influencers = Influencer.query.filter(Influencer.reach <= budget, Influencer.category.like(f'%{category}%')).all()
    elif category:
        influencers = Influencer.query.filter(Influencer.category.like(f'%{category}%')).all()
    elif budget is not None:
        influencers = Influencer.query.filter(Influencer.reach <= budget).all()
    else:
        influencers = Influencer.query.all()

    return render_template('search_influencers.html', influencers=influencers, campaign_id=campaign_id)


@app.route('/send_ad_request/<int:campaign_id>', methods=['POST'])
@login_required
def send_ad_request(campaign_id):
    influencer_id = request.form.get('influencer_id')
    if not influencer_id:
        flash('Influencer ID is missing from the request.', 'danger')
        return redirect(url_for('search_influencers', campaign_id=campaign_id))
    try:
        influencer_id = int(influencer_id)
    except ValueError:
        flash('Invalid influencer ID.', 'danger')
        return redirect(url_for('search_influencers', campaign_id=campaign_id))
    
    # Create a new ad request with status 'pending'
    ad_request = AdRequest(influencer_id=influencer_id, campaign_id=campaign_id, status='pending')
    db.session.add(ad_request)
    db.session.commit()
    flash('Ad request sent successfully.', 'success')
    return redirect(url_for('view_campaign', campaign_id=campaign_id))



@app.route('/view_campaign/<int:campaign_id>', methods=['GET'])
@login_required
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if current_user.role != 'sponsor' or campaign.sponsor_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))
    
    # Pass the campaign ID to the template
    return render_template('view_campaign.html', campaign=campaign)


@app.route('/my_campaigns')
@login_required
def my_campaigns():
    if current_user.role != 'sponsor':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    return render_template('my_campaigns.html', campaigns=campaigns)

@app.route('/ad_requests', methods=['GET'])
@login_required
def ad_requests():
    if current_user.role != 'influencer':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))

    requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('ad_requests.html', requests=requests)


@app.route('/handle_influencer_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def handle_influencer_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.form['action'] == 'accept':
        ad_request.status = 'accepted'
    elif request.form['action'] == 'reject':
        ad_request.status = 'rejected'
    elif request.form['action'] == 'negotiate':
        ad_request.terms = request.form['terms']
        ad_request.status = 'pending'
    db.session.commit()
    flash('Ad request updated successfully.', 'success')
    return redirect(url_for('ad_requests'))


@app.route('/search_campaigns', methods=['GET'])
@login_required
def search_campaigns():
    category = request.args.get('category')
    budget_str = request.args.get('budget')
    budget = None
    if budget_str:
        try:
            budget = float(budget_str)
        except ValueError:
            flash('Invalid budget value.', 'danger')
            return redirect(url_for('search_campaigns'))
    query = Campaign.query
    if category:
        query = query.filter(Campaign.category.like(f'%{category}%'))
    if budget is not None:
        query = query.filter(Campaign.budget <= budget)
    campaigns = query.all()
    return render_template('search_campaigns.html', campaigns=campaigns)


# @app.route('/update_profile', methods=['GET', 'POST'])
# @login_required
# def update_profile():
#     if request.method == 'POST':
#         if current_user.role == 'sponsor':
#             sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
#             sponsor.company_name = request.form['company_name']
#             sponsor.individual_name = request.form['individual_name']
#             sponsor.industry = request.form['industry']
#             sponsor.budget = float(request.form['budget'])
#             db.session.commit()
#         elif current_user.role == 'influencer':
#             influencer = Influencer.query.filter_by(user_id=current_user.id).first()
#             influencer.name = request.form['name']
#             influencer.category = request.form['category']
#             influencer.niche = request.form['niche']
#             influencer.reach = int(request.form['reach'])
#             db.session.commit()
#         flash('Profile updated successfully!', 'success')
#         return redirect(url_for('update_profile'))
#     return render_template('update_profile.html')

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        if current_user.role == 'sponsor':
            sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
            if sponsor:
                sponsor.company_name = request.form.get('company_name', sponsor.company_name)
                sponsor.individual_name = request.form.get('individual_name', sponsor.individual_name)
                sponsor.industry = request.form.get('industry', sponsor.industry)
                sponsor.budget = float(request.form.get('budget', sponsor.budget or 0))
                sponsor.bio = request.form.get('bio', sponsor.bio)
                # TODO: Handle file upload for company_logo if you want to store it
                db.session.commit()
                flash('Sponsor profile updated!', 'success')
            else:
                flash("Sponsor profile not found!", "danger")
                return redirect(url_for('update_profile'))

        elif current_user.role == 'influencer':
            influencer = Influencer.query.filter_by(user_id=current_user.id).first()
            if influencer:
                influencer.name = request.form.get('name', influencer.name)
                influencer.category = request.form.get('category', influencer.category)
                influencer.niche = request.form.get('niche', influencer.niche)
                influencer.reach = int(request.form.get('reach', influencer.reach or 0))
                influencer.engagement_rate = float(request.form.get('engagement_rate', influencer.engagement_rate or 0))
                # Optional fields (add these columns to your model if not present)
                influencer.location = request.form.get('location', getattr(influencer, 'location', ''))
                influencer.instagram = request.form.get('instagram', getattr(influencer, 'instagram', ''))
                influencer.youtube = request.form.get('youtube', getattr(influencer, 'youtube', ''))
                # Content types: store as comma-separated string or a JSON field in your model
                content_types = request.form.getlist('content_types')
                influencer.content_types = ','.join(content_types) if content_types else getattr(influencer, 'content_types', '')
                # TODO: Handle file upload for profile_picture if you want to store it
                db.session.commit()
                flash('Influencer profile updated!', 'success')
            else:
                flash("Influencer profile not found!", "danger")
                return redirect(url_for('update_profile'))

        return redirect(url_for('update_profile'))

    # GET request: render with user-specific profile object
    if current_user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
        return render_template('update_profile.html', sponsor=sponsor)
    elif current_user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=current_user.id).first()
        return render_template('update_profile.html', influencer=influencer)
    return redirect(url_for('index'))


@app.route('/campaign/<int:campaign_id>/ad_requests', methods=['GET'])
@login_required
def view_ad_requests(campaign_id):
    if current_user.role != 'sponsor':
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))

    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()

    # Attach full influencer profile to each request
    enriched_requests = []
    for req in ad_requests:
        influencer_profile = Influencer.query.filter_by(user_id=req.influencer_id).first()
        print(f"AdRequest {req.id}: influencer_id={req.influencer_id}, influencer_profile={influencer_profile}")
        enriched_requests.append({
            "ad_request": req,
            "user": req.influencer,
            "influencer": influencer_profile
        })


    if influencer_profile is None:
        print(f"Influencer not found for user_id={req.influencer_id}")

    print(enriched_requests)
    return render_template(
        'view_ad_requests.html',
        ad_requests=enriched_requests,
        campaign=campaign
    )

   
@app.route('/handle_sponsor_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def handle_sponsor_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('get_home'))

    action = request.form['action']
    if action == 'accept':
        ad_request.status = 'accepted'
    elif action == 'reject':
        ad_request.status = 'rejected'
    elif action == 'negotiate':
        ad_request.terms = request.form['terms']
        ad_request.status = 'pending'  # Keep as 'pending' if negotiation is ongoing
    db.session.commit()
    flash('Ad request updated successfully.', 'success')
    return redirect(url_for('view_ad_requests', campaign_id=ad_request.campaign_id))

@app.route('/flag_users')
def flag_users():
    users = User.query.all()
    return render_template('flag_users.html', users=users)

@app.route('/flag_campaigns')
def flag_campaigns():
    campaigns = Campaign.query.all()
    return render_template('flag_campaigns.html', campaigns=campaigns)

@app.route('/flag_user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_flagged = True
        user.flag_reason = request.form['reason']
        db.session.commit()
    return redirect(url_for('flag_users'))

@app.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign:
        campaign.is_flagged = True
        campaign.flag_reason = request.form['reason']
        db.session.commit()
    return redirect(url_for('flag_campaigns'))

# ================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    print("Received data:", data)
    category = (data.get("category") or "").strip().lower()
    niche = (data.get("niche") or "").strip().lower()
    sponsor_id = data.get("sponsor_id")
    print(f"Category: {category}, Niche: {niche}, Sponsor ID: {sponsor_id}")

    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        return jsonify({"error": "Sponsor not found"}), 404

    influencers = Influencer.query.filter(
        Influencer.category.ilike(f"%{category}%"),
        Influencer.niche.ilike(f"%{niche}%")
    ).all()

    if not influencers:
        # Fallback: recommend top influencers by followers
        influencers = Influencer.query.order_by(Influencer.followers.desc()).limit(5).all()
        if not influencers:
            return jsonify({"error": "No influencers available."}), 404

    recommendations = [{
        "id": inf.id,
        "name": inf.name,
        "category": inf.category,
        "niche": inf.niche,
        "followers": inf.followers,
        "engagement_rate": inf.engagement_rate
    } for inf in influencers]

    return jsonify({"recommendations": recommendations})



# =========================================

@app.route("/recommend_campaigns", methods=["POST"])
def recommend_campaigns():
    try:
        data = request.json  
        category = data.get("category", "").strip().lower()
        niche = data.get("niche", "").strip().lower()

        # If niche is not provided, use the influencer's profile niche
        if not niche:
            # Option 1: Use current_user (if influencer is logged in)
            if current_user.is_authenticated and current_user.role == "influencer":
                influencer = Influencer.query.filter_by(user_id=current_user.id).first()
                if influencer:
                    niche = (influencer.niche or "").strip().lower()
            # Option 2: Use influencer_id from request
            elif "influencer_id" in data:
                influencer = Influencer.query.filter_by(id=data["influencer_id"]).first()
                if influencer:
                    niche = (influencer.niche or "").strip().lower()

        if not category:
            return jsonify({"error": "Category is required"}), 400

        campaigns = Campaign.query.all()
        if not campaigns:
            return jsonify({"message": "No campaigns found"}), 404

        campaign_data = []
        texts = []

        for camp in campaigns:
            cat = (camp.category or "").strip().lower()
            niche_ = getattr(camp, "niche", "") or niche
            combined_text = f"{cat} {niche_}"

            campaign_data.append({
                "id": camp.id,
                "name": camp.title,
                "category": cat,
                "niche": niche_,
                "budget": camp.budget,
                "text": combined_text
            })
            texts.append(combined_text)

        influencer_text = f"{category} {niche}"
        texts.append(influencer_text)

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

        for i, camp in enumerate(campaign_data):
            campaign_data[i]["score"] = round(float(similarity_scores[i]), 4)

        sorted_campaigns = sorted(campaign_data, key=lambda x: x["score"], reverse=True)

        if all(score == 0.0 for score in similarity_scores):
            sorted_campaigns = sorted(campaign_data, key=lambda x: x["budget"], reverse=True)

        return jsonify(sorted_campaigns[:5])

    except Exception as e:
        logging.error(f"Error in recommend_campaigns: {str(e)}")
        return jsonify({"error": "Something went wrong"}), 500




@app.route("/recommend_influencers", methods=["POST"])
def recommend_influencers():
    try:
        data = request.json  
        category = data.get("category", "").strip().lower()
        niche = data.get("niche", "").strip().lower()

        if not category:
            return jsonify({"error": "Category is required."}), 400

        influencers = Influencer.query.all()
        if not influencers:
            return jsonify({"error": "No influencers found."}), 404

        influencer_data = []
        texts = []

        for inf in influencers:
            inf_category = (inf.category or "").strip().lower()
            inf_niche = (inf.niche or "").strip().lower()
            combined_text = f"{inf_category} {inf_niche}"

            influencer_data.append({
                "id": inf.id,
                "name": inf.name,
                "category": inf_category,
                "niche": inf_niche,
                "followers": inf.followers,
                "engagement_rate": inf.engagement_rate,
                "text": combined_text
            })
            texts.append(combined_text)

        sponsor_text = f"{category} {niche}"
        texts.append(sponsor_text)

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

        for i, inf in enumerate(influencer_data):
            inf["score"] = round(float(similarity_scores[i]), 4)

        top_recommendations = sorted(influencer_data, key=lambda x: x["score"], reverse=True)

        if all(score == 0.0 for score in similarity_scores):
            top_recommendations = sorted(influencer_data, key=lambda x: x["followers"], reverse=True)

        return jsonify({"recommendations": top_recommendations[:5]})

    except Exception as e:
        logging.exception("Error in recommend_influencers")
        return jsonify({"error": "Something went wrong while processing recommendations."}), 500


    
# =========================================================================

@app.route("/influencers", methods=["GET"])
def get_influencers():
    influencers = Influencer.query.all()
    return jsonify([{
        "id": inf.id,
        "name": inf.name,
        "category": inf.category,
        "niche": inf.niche,
        "followers": inf.followers,
        "engagement_rate": inf.engagement_rate
    } for inf in influencers])


@app.route('/invite_influencer', methods=['POST'])
def invite_influencer():
    data = request.get_json()
    influencer_id = data.get("influencer_id")
    sponsor_id = data.get("sponsor_id")

    if not influencer_id or not sponsor_id:
        return jsonify({"status": "error", "message": "Missing influencer or sponsor ID"}), 400

    # 🧠 TODO: Save this invitation to your DB
    print(f"[INVITE] Sponsor {sponsor_id} invited Influencer {influencer_id}")

    # ✅ Optionally store it in a database or send a notification

    return jsonify({"status": "success", "message": "Invite sent"})


@app.route('/my_profile')
@login_required
def my_profile():
    if current_user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
        return render_template('my_profile.html', sponsor=sponsor)
    elif current_user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=current_user.id).first()
        return render_template('my_profile.html', influencer=influencer)
    return redirect(url_for('index'))


# =========================================================================

if __name__ == '__main__':
    app.run(debug=True)











# from flask import Flask, redirect, render_template, request, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
# app.config['SECRET_KEY'] = '619619'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(200), unique=True, nullable=False)
#     email = db.Column(db.String(200), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     role = db.Column(db.String(50), nullable=False)  # 'admin', 'sponsor', 'influencer'
#     accepted_terms = db.Column(db.Boolean, default=False, nullable=False)

#     campaigns = db.relationship('Campaign', back_populates='sponsor', lazy=True)
#     ad_requests = db.relationship('AdRequest', back_populates='influencer', lazy=True)


# class Campaign(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     budget = db.Column(db.Float, nullable=False)
#     sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     sponsor = db.relationship('User', back_populates='campaigns')
#     transparency_policy_accepted = db.Column(db.Boolean, default=False, nullable=False)


# class AdRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
#     status = db.Column(db.String(20), default='pending')
#     accepted_terms = db.Column(db.Boolean, default=False, nullable=False)
#     influencer = db.relationship('User', foreign_keys=[influencer_id], back_populates='ad_requests')


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


# @app.route('/')
# @login_required
# def home():
#     return render_template('home.html')


# @app.route('/signup', methods=['POST'])
# def signup_post():
#     username = request.form['username']
#     email = request.form['email']
#     password = request.form['password']
#     role = request.form.get('role', 'influencer')
#     accepted_terms = request.form.get('accepted_terms') == 'on'

#     if not accepted_terms:
#         flash('You must accept the Terms & Conditions to sign up.', 'danger')
#         return redirect(url_for('signup'))

#     hashed_password = generate_password_hash(password)
#     user = User(username=username, email=email, password=hashed_password, role=role, accepted_terms=True)
#     db.session.add(user)
#     db.session.commit()

#     login_user(user)
#     return redirect(url_for('home'))


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first()

#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('home'))
#         else:
#             flash('Invalid credentials, please try again.', 'danger')

#     return render_template('login.html')


# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('login'))


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Ensure the database is created properly
#     app.run(debug=True)














































