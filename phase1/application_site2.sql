USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Food_Item_Indian;

CREATE TABLE Food_Item_Indian (
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(100) NOT NULL,
    Price INT NOT NULL,
    Category VARCHAR(100) NOT NULL,
    FK_Restaurant VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Food_Item_Indian
VALUES
    ("Special_Shawarma", "Indian", 100, "Non-Veg", "AAI", "AAP"), 
    ("Cheese_Shawarma", "Indian", 90, "Veg", "AAI", "AAQ"),
    ("Honey_Chilli", "Indian", 120, "Veg", "AAK", "AAV") ;
UNLOCK TABLES;


DROP TABLE IF EXISTS User_Restaurant_Order_Amount_Indian;

CREATE TABLE User_Restaurant_Order_Amount_Indian (
    User_ID VARCHAR(100) NOT NULL,
    Restaurant_ID VARCHAR(100) NOT NULL,
    Amount INT NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    User_Restaurant_Order_Amount_Indian
VALUES
    ("AAG", "AAK", 120, "AAW");
UNLOCK TABLES;

DROP TABLE IF EXISTS Order_Items_Indian;

CREATE TABLE Order_Items_Indian (
    Order_ID VARCHAR(100) NOT NULL,
    Item_ID VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY(Order_ID,Item_ID)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Order_Items_Indian
VALUES
    ("AAW","AAV",1) ;
UNLOCK TABLES;

DROP TABLE IF EXISTS User_Remaining;

CREATE TABLE User_Remaining (
    Address VARCHAR(200) NOT NULL,
    Phone_Number VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    User_Remaining
VALUES
    ("Sunam", "9478077895", "AAA"),
    ("Delhi", "9971352631", "AAB"),
    ("Delhi", "9876543210", "AAC"),
    ("Amritsar", "1234567890", "AAD"),
    ("Jaipur", "4561237890", "AAE"), 
    ("Delhi", "6543219870", "AAF"), 
    ("Jaipur", "7896541230", "AAG") ;
UNLOCK TABLES;

