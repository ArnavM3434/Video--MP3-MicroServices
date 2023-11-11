CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'Aauth123';
/*user to access this auth database*/

CREATE DATABASE auth;

GRANT ALL PRIVILEGES ON auth.* to 'auth_user'@'localhost';
 /*grant privileges to auth database and all its tables to auth_user*/

USE auth;
 /*use auth database when we create the table*/

CREATE TABLE user(
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user (email, password) VALUES ('arnavnmehta1@gmail.com', 'Admin123');





