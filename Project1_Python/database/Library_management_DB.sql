CREATE DATABASE library_management;
use library_management;

show tables;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL
);

-- Dummy data
INSERT INTO users (username, password) VALUES
('siva', 'siva@123'),
('saiteja', 'saiteja@123'),
('sadhika', 'sadhika@123'),
('sahithi', 'sahithi@123');

INSERT INTO users (username, password) VALUES('sai', 'teja@123');
INSERT INTO users (username, password) VALUES('hello', 'hello@123');
INSERT INTO users (username, password) VALUES('surya', 'surya@1');

update users set password='teja@123' where username = 'saiteja';
update users set password='sahi@1' where username = 'sahithi'; 
update users set password='hello@1' where username = 'hello'; 


SELECT * FROM users;

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL
);

-- Dummy data
INSERT INTO books (title, category) VALUES
('Book 1', 'Fiction'),
('Book 2', 'Horror'),
('Book 3', 'Science Fiction'),
('Book 4', 'Fantasy');

INSERT INTO books (title, category) VALUES
('The Great Gatsby', 'Fiction'),
('To Kill a Mockingbird', 'Fiction'),
('1984', 'Science Fiction'),
('The Catcher in the Rye', 'Fiction'),
('Pride and Prejudice', 'Romance'),
('The Hobbit', 'Fantasy'),
('The Da Vinci Code', 'Mystery'),
('Sapiens: A Brief History of Humankind', 'Non-fiction'),
('Harry Potter and the Philosopher''s Stone', 'Fantasy'),
('The Lord of the Rings', 'Fantasy');



update books set title='Harry Potter and the Philosopher' where category = 'Fiction'; 
update books set title='The Catcher in the Rye' where category = 'Horror'; 
update books set title='To Kill a Mockingbird' where category = 'Science Fiction'; 
update books set title='The Hobbit' where category = 'Fantasy';


SELECT * FROM books;

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    book_id INT NOT NULL,
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    CONSTRAINT fk_cart_users FOREIGN KEY (username) REFERENCES users(username),
    CONSTRAINT fk_cart_books FOREIGN KEY (book_id) REFERENCES books(id)
);

SELECT * FROM cart;


