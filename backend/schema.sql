/* Drop Tables */

-- Disable foreign key checks
SET foreign_key_checks = 0;

-- Drop tables
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Follow;
DROP TABLE IF EXISTS Article;
DROP TABLE IF EXISTS Source;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS Sector;

-- Enable foreign key checks
SET foreign_key_checks = 1;


/* Create Tables */

CREATE TABLE User (
    id integer NOT NULL AUTO_INCREMENT,
    verified integer DEFAULT 0,
    name varchar(35) NOT NULL,
    email varchar(30) NOT NULL,
    password_hash varchar(255) NOT NULL,
    salt varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (email)
);

CREATE TABLE Notification (
    id integer NOT NULL AUTO_INCREMENT,
    userID integer NOT NULL,
    notfi_read integer DEFAULT 0,
    notif_message text NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (userID) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Follow (
    id integer NOT NULL AUTO_INCREMENT,
    userID integer NOT NULL,
    stock_ticker varchar(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (userID) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Sector (
    id integer NOT NULL AUTO_INCREMENT,
    sector_name varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (sector_name)
);

CREATE TABLE Source (
    id integer NOT NULL AUTO_INCREMENT,
    source_name varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (source_name)
);

CREATE TABLE Company (
    stock_ticker varchar(255) NOT NULL,
    company_name varchar(255) NOT NULL,
    sectorID integer NOT NULL,
    PRIMARY KEY (stock_ticker),
    FOREIGN KEY (sectorID) REFERENCES Sector(id) ON DELETE CASCADE,
    UNIQUE (company_name)
);

CREATE TABLE Article (
    id integer NOT NULL AUTO_INCREMENT,
    sourceID integer NOT NULL,
    stock_ticker varchar(255) NOT NULL,
    rating integer NOT NULL,
    probability float NOT NULL,
    link text NOT NULL,
    summary text NOT NULL,
    published date NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (sourceID) REFERENCES Source(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_ticker) REFERENCES Company(stock_ticker) ON DELETE CASCADE
);
