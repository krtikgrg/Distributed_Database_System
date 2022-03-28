USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Restaurants_Minimal;

CREATE TABLE Restaurants_Minimal (
    Name VARCHAR(100) NOT NULL,
    Rating INT NOT NULL,
    Specialty VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Restaurants_Minimal WRITE;

/*Insert data*/
INSERT INTO
    Restaurants_Minimal
VALUES
    ("Dominos", 4, "pizza", "AAH"), 
    ("SKShawarma", 3, "shawarma", "AAI"), 
    ("WOWMomos", 5, "momos", "AAJ"), 
    ("h9", 4, "manchurian", "AAK");
UNLOCK TABLES;



DROP TABLE IF EXISTS Restaurants_Remaining;

CREATE TABLE Restaurants_Remaining (
    Address VARCHAR(200) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Num_Reviews INT NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Restaurants_Remaining
VALUES
    ("Gachibowli", "domi@gmail.com", 45, "AAH"), 
    ("DLF", "sks@gmail.com", 38, "AAI"), 
    ("Indira_Nagar", "wm@gmail.com", 43, "AAJ"), 
    ("Garden_Road", "h9@gmail.com", 50, "AAK");
UNLOCK TABLES;


DROP TABLE IF EXISTS User_Minimal;

CREATE TABLE User_Minimal (
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    User_Minimal
VALUES
    ("Kartik", "krtikgrg@gmail.com", "AAA"),
    ("Aaradhya", "aardg@gmail.com", "AAB"),
    ("Priyansh", "p@gmail.com", "AAC"),
    ("Harshit", "h@gmail.com", "AAD"),
    ("Aaditya", "a@gmail.com", "AAE"), 
    ("Shreyash", "s@gmail.com", "AAF"), 
    ("Ayush", "ag@gmail.com", "AAG") ;
UNLOCK TABLES;
