USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Food_Item_Italian;

CREATE TABLE Food_Item_Italian (
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(100) NOT NULL,
    Price INT NOT NULL,
    Category VARCHAR(100) NOT NULL,
    FK_Restaurant VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Food_Item_Italian
VALUES
    ("Marghrita", "Italian", 100, "Veg", "AAH", "AAR"), 
    ("Non_Veg_Loaded", "Italian", 150, "Non-Veg", "AAH", "AAS"), 
    ("Veg_Loaded", "Italian", 125, "Veg", "AAH", "AAT"),
    ("Pasta", "Italian", 95, "Veg", "AAH", "AAU");
UNLOCK TABLES;

DROP TABLE IF EXISTS User_Restaurant_Order_Amount_Italian;

CREATE TABLE User_Restaurant_Order_Amount_Italian (
    User_ID VARCHAR(100) NOT NULL,
    Restaurant_ID VARCHAR(100) NOT NULL,
    Amount INT NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    User_Restaurant_Order_Amount_Italian
VALUES
    ("AAE","AAH",100,"AAY");
UNLOCK TABLES;

DROP TABLE IF EXISTS Order_Items_Italian;

CREATE TABLE Order_Items_Italian (
    Order_ID VARCHAR(100) NOT NULL,
    Item_ID VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY(Order_ID,Item_ID)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Order_Items_Italian
VALUES
    ("AAY", "AAR", 1);
UNLOCK TABLES;