import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "photography.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking", backref="package", lazy=True)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_image = db.Column(db.String(500), nullable=False, default="https://i.pravatar.cc/150?img=12")
    rating = db.Column(db.Integer, default=5)
    review = db.Column(db.Text, nullable=False)
    service = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("package.id"))
    event_type = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    event_type = db.Column(db.String(100))
    preferred_date = db.Column(db.Date)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please log in as administrator.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def seed_database():
    if not Admin.query.first():
        db.session.add(Admin(
            username="admin",
            password_hash=generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))
        ))
    if Package.query.count() == 0:
        db.session.add_all([
            Package(name="Basic", price=5000, description="Perfect for intimate portrait and small events.",
                    features="2 Hours Photography\n50 Edited Photos\nOnline Gallery"),
            Package(name="Premium", price=12000, description="A complete package for weddings and special occasions.",
                    features="5 Hours Photography\n150 Edited Photos\nPhoto Album\nOnline Gallery"),
            Package(name="Luxury", price=25000, description="Full-day premium coverage for unforgettable celebrations.",
                    features="Full Day Photography\n300+ Edited Photos\nPremium Album\nPre-Wedding Session\nOnline Gallery")
        ])
    if Testimonial.query.count() == 0:
        db.session.add_all([
            Testimonial(client_name="Aarav & Meera", client_image="https://i.pravatar.cc/150?img=32",
                        rating=5, review="The photographs captured every emotion beautifully. We loved the entire experience!", service="Wedding"),
            Testimonial(client_name="Riya Sharma", client_image="https://i.pravatar.cc/150?img=47",
                        rating=5, review="Professional, creative and very comfortable to work with. The portraits were amazing.", service="Portrait"),
            Testimonial(client_name="Kabir Events", client_image="https://i.pravatar.cc/150?img=12",
                        rating=5, review="Excellent event coverage and quick delivery. Highly recommended for professional events.", service="Events")
        ])
    if Gallery.query.count() == 0:
        samples = [
            ("Golden Hour Couple", "Wedding", "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80"),
            ("Bride Details", "Wedding", "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?auto=format&fit=crop&w=1200&q=80"),
            ("Studio Portrait", "Portrait", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=1200&q=80"),
            ("Editorial Look", "Fashion", "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=80"),
            ("Mountain Escape", "Nature", "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80"),
            ("City Celebration", "Events", "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=80"),
            ("Travel Story", "Travel", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"),
            ("Pre-Wedding Walk", "Pre-Wedding", "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=80")
        ]
        db.session.add_all([Gallery(title=t, category=c, image=i, description=t) for t, c, i in samples])
    db.session.commit()

@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}

@app.route("/")
def home():
    return render_template("index.html",
                           featured=Gallery.query.order_by(Gallery.id.desc()).limit(6).all(),
                           packages=Package.query.limit(3).all(),
                           testimonials=Testimonial.query.order_by(Testimonial.id.desc()).limit(3).all())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/portfolio")
def portfolio():
    category = request.args.get("category", "All")
    query = Gallery.query.order_by(Gallery.id.desc())
    photos = query.all() if category == "All" else query.filter_by(category=category).all()
    return render_template("portfolio.html", photos=photos, active_category=category)

@app.route("/services")
def services():
    return render_template("services.html", packages=Package.query.all())

@app.route("/testimonials")
def testimonials():
    return render_template("testimonials.html", testimonials=Testimonial.query.order_by(Testimonial.id.desc()).all())

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete all required fields.", "danger")
            return render_template("contact.html")
        preferred = request.form.get("preferred_date")
        date_value = datetime.strptime(preferred, "%Y-%m-%d").date() if preferred else None
        db.session.add(ContactMessage(name=name, email=email, phone=request.form.get("phone"),
                                      event_type=request.form.get("event_type"),
                                      preferred_date=date_value, message=message))
        db.session.commit()
        flash("Thanks! Your message has been received.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    packages = Package.query.all()
    if request.method == "POST":
        required = ["customer_name", "email", "phone", "event_type", "event_date", "location"]
        if not all(request.form.get(k, "").strip() for k in required):
            flash("Please complete all required booking fields.", "danger")
            return render_template("booking.html", packages=packages)
        try:
            event_date = datetime.strptime(request.form["event_date"], "%Y-%m-%d").date()
            package_id = int(request.form["package_id"]) if request.form.get("package_id") else None
        except ValueError:
            flash("Please enter valid booking details.", "danger")
            return render_template("booking.html", packages=packages)
        db.session.add(Booking(
            customer_name=request.form["customer_name"].strip(),
            email=request.form["email"].strip(),
            phone=request.form["phone"].strip(),
            package_id=package_id,
            event_type=request.form["event_type"].strip(),
            event_date=event_date,
            location=request.form["location"].strip(),
            message=request.form.get("message", "").strip()
        ))
        db.session.commit()
        flash("Booking request submitted successfully.", "success")
        return redirect(url_for("booking"))
    return render_template("booking.html", packages=packages)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = Admin.query.filter_by(username=request.form.get("username", "").strip()).first()
        if admin and check_password_hash(admin.password_hash, request.form.get("password", "")):
            session["admin_id"] = admin.id
            session["admin_username"] = admin.username
            flash("Welcome back, admin.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html",
        gallery_count=Gallery.query.count(),
        package_count=Package.query.count(),
        testimonial_count=Testimonial.query.count(),
        booking_count=Booking.query.count(),
        pending_count=Booking.query.filter_by(status="Pending").count(),
        confirmed_count=Booking.query.filter_by(status="Confirmed").count())

@app.route("/admin/gallery", methods=["GET", "POST"])
@admin_required
def admin_gallery():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        image = request.files.get("image")
        image_url = request.form.get("image_url", "").strip()
        if not title or not category or (not image and not image_url):
            flash("Title, category and an image or image URL are required.", "danger")
        else:
            path = image_url
            if image and image.filename:
                if not allowed_file(image.filename):
                    flash("Unsupported image format.", "danger")
                    return redirect(url_for("admin_gallery"))
                filename = secure_filename(image.filename)
                filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                path = url_for("static", filename=f"uploads/{filename}")
            db.session.add(Gallery(title=title, category=category, image=path,
                                   description=request.form.get("description", "")))
            db.session.commit()
            flash("Gallery photo added.", "success")
        return redirect(url_for("admin_gallery"))
    return render_template("admin/gallery.html", photos=Gallery.query.order_by(Gallery.id.desc()).all())

@app.route("/admin/gallery/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_gallery(item_id):
    item = db.get_or_404(Gallery, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Gallery photo deleted.", "success")
    return redirect(url_for("admin_gallery"))

@app.route("/admin/packages", methods=["GET", "POST"])
@admin_required
def admin_packages():
    if request.method == "POST":
        try:
            price = float(request.form.get("price", "0"))
        except ValueError:
            price = 0
        db.session.add(Package(name=request.form.get("name", "").strip(), price=price,
                               description=request.form.get("description", "").strip(),
                               features=request.form.get("features", "").strip()))
        db.session.commit()
        flash("Package added.", "success")
        return redirect(url_for("admin_packages"))
    return render_template("admin/packages.html", packages=Package.query.order_by(Package.id.desc()).all())

@app.route("/admin/packages/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_package(item_id):
    item = db.get_or_404(Package, item_id)
    if item.bookings:
        flash("Cannot delete a package that has bookings.", "warning")
    else:
        db.session.delete(item)
        db.session.commit()
        flash("Package deleted.", "success")
    return redirect(url_for("admin_packages"))

@app.route("/admin/testimonials", methods=["GET", "POST"])
@admin_required
def admin_testimonials():
    if request.method == "POST":
        db.session.add(Testimonial(
            client_name=request.form.get("client_name", "").strip(),
            client_image=request.form.get("client_image", "").strip() or "https://i.pravatar.cc/150?img=12",
            rating=max(1, min(5, int(request.form.get("rating", "5")))),
            review=request.form.get("review", "").strip(),
            service=request.form.get("service", "").strip()
        ))
        db.session.commit()
        flash("Testimonial added.", "success")
        return redirect(url_for("admin_testimonials"))
    return render_template("admin/testimonials.html",
                           testimonials=Testimonial.query.order_by(Testimonial.id.desc()).all())

@app.route("/admin/testimonials/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_testimonial(item_id):
    item = db.get_or_404(Testimonial, item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Testimonial deleted.", "success")
    return redirect(url_for("admin_testimonials"))

@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    return render_template("admin/bookings.html", bookings=Booking.query.order_by(Booking.id.desc()).all())

@app.route("/admin/bookings/<int:item_id>/status", methods=["POST"])
@admin_required
def update_booking(item_id):
    booking = db.get_or_404(Booking, item_id)
    status = request.form.get("status")
    if status in {"Pending", "Confirmed", "Completed", "Cancelled"}:
        booking.status = status
        db.session.commit()
        flash("Booking status updated.", "success")
    return redirect(url_for("admin_bookings"))

@app.route("/admin/bookings/<int:item_id>/delete", methods=["POST"])
@admin_required
def delete_booking(item_id):
    booking = db.get_or_404(Booking, item_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking deleted.", "success")
    return redirect(url_for("admin_bookings"))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

@app.errorhandler(413)
def too_large(_):
    flash("Uploaded image is too large. Maximum size is 5 MB.", "danger")
    return redirect(request.referrer or url_for("home"))

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    app.run(debug=True)
