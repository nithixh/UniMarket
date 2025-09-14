# UniMarket 

A Flask-based web application for college students to buy and sell items within their campus community.

## Features

- **User Authentication**: College email-based registration and login
- **Product Listings**: Create, view, and manage product listings
- **Messaging System**: In-app chat between buyers and sellers
- **Rating System**: Rate and review sellers
- **Search & Filter**: Find items by keywords and categories
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: HTML, CSS, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: Werkzeug Security

## Installation & Setup

### Prerequisites

1. Python 3.7 or higher
2. MySQL 8.0 or higher
3. pip (Python package manager)

### Step 1: Clone/Extract the Project

```bash
# If you have the project files, navigate to the project directory
cd unimarket
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup MySQL Database

1. Start your MySQL server
2. Open MySQL command line or MySQL Workbench
3. Run the database setup script:

```sql
-- Create database and tables
source database_setup.sql
-- OR copy and paste the contents of database_setup.sql
```

### Step 5: Configure Database Connection

1. Open `config.py`
2. Update the MySQL connection details if needed:

```python
MYSQL_HOST = 'localhost'        # Your MySQL host
MYSQL_USER = 'root'             # Your MySQL username  
MYSQL_PASSWORD = 'yourpassword' # Your MySQL password
MYSQL_DATABASE = 'unimarket'    # Database name
```

### Step 6: Create Uploads Directory

```bash
# Create uploads directory for product images
mkdir uploads
```

### Step 7: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
unimarket/
│
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── database_setup.sql     # Database schema
├── README.md             # This file
│
├── static/               # Static files
│   └── style.css         # Custom CSS styles
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   ├── add_listing.html  # Add new listing
│   ├── listing_detail.html # View listing details
│   ├── chat.html         # Messaging interface
│   ├── profile.html      # User profile
│   └── rate_seller.html  # Rating interface
│
└── uploads/              # User uploaded images
```

## Usage

### For Sellers
1. Register with your college email (@kongu.edu)
2. Login to your account
3. Click "Add Listing" to create a new product listing
4. Upload product images and fill in details
5. Manage your listings from your profile page
6. Respond to buyer messages
7. Mark items as sold when transaction is complete

### For Buyers
1. Browse available items on the homepage
2. Use search and category filters to find specific items
3. Click "View Details" to see full product information
4. Contact sellers through the messaging system
5. Meet in person for cash-on-delivery transactions
6. Rate sellers after successful purchases

## API Routes

- `/` - Homepage (listings feed)
- `/signup` - User registration
- `/login` - User login
- `/logout` - User logout
- `/add_listing` - Add new product listing
- `/listing/<id>` - View product details
- `/messages/<user_id>` - Chat interface
- `/send_message` - Send message (AJAX)
- `/mark_sold/<listing_id>` - Mark item as sold
- `/rate/<seller_id>` - Rate a seller
- `/profile` - User profile page

## Database Schema

### Users Table
- `id` (Primary Key)
- `name` - Full name
- `email` - College email (must end with kongu.edu)
- `password` - Hashed password
- `college_name` - College name
- `verified` - Email verification status

### Listings Table
- `id` (Primary Key)
- `title` - Product title
- `description` - Product description
- `price` - Product price
- `category` - Product category
- `image_path` - Uploaded image filename
- `seller_id` - Foreign key to users table
- `status` - Available/Sold

### Messages Table
- `id` (Primary Key)
- `sender_id` - Message sender
- `receiver_id` - Message receiver
- `listing_id` - Related listing (optional)
- `message_text` - Message content
- `timestamp` - When message was sent

### Ratings Table
- `id` (Primary Key)
- `reviewer_id` - User giving the rating
- `seller_id` - User being rated
- `rating` - Rating value (1-5)
- `review_text` - Optional review text

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- College email validation
- File upload validation
- SQL injection prevention
- XSS protection through template escaping

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in config.py
   - Ensure database exists and tables are created

2. **File Upload Issues**
   - Check uploads/ directory exists and is writable
   - Verify file size limits

3. **Email Validation Error**
   - Ensure email ends with @kongu.edu
   - Check for typos in email address

4. **Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

## Future Enhancements

- Real-time messaging with WebSockets
- Email notifications
- Image optimization
- Advanced search filters
- Mobile app version
- Payment integration
- Admin panel

## Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is created for educational purposes at Kongu Engineering College By Nithish Kumar T S.

---

**Note**: This is a demo application. For production use, additional security measures and optimizations should be implemented.
