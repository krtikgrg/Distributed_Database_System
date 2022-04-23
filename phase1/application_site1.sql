USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Food_Item_Chinese;

CREATE TABLE Food_Item_Chinese (
    Name VARCHAR(100) NOT NULL,
    Item_Type VARCHAR(100) NOT NULL,
    Price INT NOT NULL,
    Item_Category VARCHAR(100) NOT NULL,
    FK_Restaurant VARCHAR(100) NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Food_Item_Chinese
VALUES
    ("Momos", "Chinese", 40, "Veg", "AAJ", "AAL"), 
    ("Manchurian", "Chinese", 50, "Veg", "AAK", "AAM"), 
    ("Noodles", "Chinese", 45, "Veg", "AAK", "AAN"), 
    ("Chowmein", "Chinese", 70, "Veg", "AAK", "AAO") ;
UNLOCK TABLES;

DROP TABLE IF EXISTS User_Restaurant_Order_Amount_Chinese;

CREATE TABLE User_Restaurant_Order_Amount_Chinese (
    User_ID VARCHAR(100) NOT NULL,
    Restaurant_ID VARCHAR(100) NOT NULL,
    Amount INT NOT NULL,
    PK_Custom VARCHAR(100) NOT NULL,
    PRIMARY KEY(PK_Custom)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    User_Restaurant_Order_Amount_Chinese
VALUES
    ("AAF","AAK",70,"AAX");
UNLOCK TABLES;

DROP TABLE IF EXISTS Order_Items_Chinese;

CREATE TABLE Order_Items_Chinese (
    Order_ID VARCHAR(100) NOT NULL,
    Item_ID VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY(Order_ID,Item_ID)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

INSERT INTO
    Order_Items_Chinese
VALUES
    ("AAX","AAO",1);
UNLOCK TABLES;