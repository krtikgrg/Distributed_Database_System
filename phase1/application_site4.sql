USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Restaurants_Minimal;

CREATE TABLE Restaurants_Minimal (
    Name VARCHAR(100) NOT NULL,
    Rating INT NOT NULL,
    Specialty VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

DROP TABLE IF EXISTS Restaurants_Remaining;

CREATE TABLE Restaurants_Remaining (
    Address VARCHAR(200) NOT NULL,
    Num_Reviews INT NOT NULL,
    Email VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

DROP TABLE IF EXISTS User_Minimal;

CREATE TABLE User_Minimal (
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;
