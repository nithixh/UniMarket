-- UniMarket Database Setup Script
-- Run this script in MySQL to set up the database

CREATE DATABASE IF NOT EXISTS unimarket;
USE unimarket;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    college_name VARCHAR(150) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listings Table
CREATE TABLE IF NOT EXISTS listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    image_path VARCHAR(255),
    seller_id INT NOT NULL,
    status ENUM('Available','Sold') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    listing_id INT,
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE SET NULL
);

-- Ratings Table
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reviewer_id INT NOT NULL,
    seller_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_review (reviewer_id, seller_id)
);

-- Create indexes for better performance
CREATE INDEX idx_listings_seller ON listings(seller_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_category ON listings(category);
CREATE INDEX idx_messages_conversation ON messages(sender_id, receiver_id);
CREATE INDEX idx_ratings_seller ON ratings(seller_id);

-- Insert sample data (optional - for testing)
-- You can uncomment these lines to add sample data

/*
INSERT INTO users (name, email, password, college_name, verified) VALUES
('John Doe', 'john.doe@kongu.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewDIjBzwLLdIzj.K', 'Kongu Engineering College', TRUE),
('Jane Smith', 'jane.smith@kongu.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewDIjBzwLLdIzj.K', 'Kongu Engineering College', TRUE);

INSERT INTO listings (title, description, price, category, seller_id) VALUES
('iPhone 12', 'Good condition iPhone 12 with charger', 45000.00, 'Electronics', 1),
('Engineering Textbooks', 'Complete set of mechanical engineering books', 2500.00, 'Books', 2);
*/

SHOW TABLES;
SELECT 'Database setup completed successfully!' as Status;
