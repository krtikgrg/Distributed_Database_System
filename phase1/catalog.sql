DROP DATABASE IF EXISTS zomato_catalog_outlaws;

CREATE SCHEMA zomato_catalog_outlaws;

USE zomato_catalog_outlaws;

DROP TABLE IF EXISTS Tables;

CREATE TABLE Tables (
    Name VARCHAR(100) NOT NULL,
    Fragmentation_Type VARCHAR(12),
    Number_Of_Fragments INT,
    PRIMARY KEY(Name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Tables WRITE;

/*insert data to table here that is write insert querries here*/
;

INSERT INTO
    Tables
VALUES
    ("Users", "VF",2),
    ("Restaurants", "VF",2),
    ("Food_Item", "HF",3),
    ("Orders", "DHF",3),
    ("Order_Items", "DHF",3);

UNLOCK TABLES;

DROP TABLE IF EXISTS Columns;

CREATE TABLE Columns (
    Table_Name VARCHAR(20) NOT NULL,
    Column_Name VARCHAR(100) NOT NULL,
    PRIMARY KEY (Table_Name, Column_Name)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Columns WRITE;

/*Insert data*/
INSERT INTO
    Columns
VALUES
    ("Users", "Name"),
    ("Users", "Email"),
    ("Users", "Address"),
    ("Users", "Phone_Number"),
    ("Users", "PK_Custom"),
    ("Restaurants", "Name"),
    ("Restaurants", "Address"),
    ("Restaurants", "Email"),
    ("Restaurants", "Rating"),
    ("Restaurants", "Specialty"),
    ("Restaurants", "Num_Reviews"),
    ("Restaurants", "PK_Custom"),
    ("Food_Item", "Name"),
    ("Food_Item", "Item_Type"),
    ("Food_Item", "Price"),
    ("Food_Item", "Item_Category"),
    ("Food_Item", "FK_Restaurant"),
    ("Food_Item", "PK_Custom"),
    ("Orders", "User_ID"),
    ("Orders", "Restaurant_ID"),
    ("Orders", "Amount"),
    ("Orders", "PK_Custom"),
    ("Order_Items", "Order_ID"),
    ("Order_Items", "Item_ID"),
    ("Order_Items", "Quantity");

UNLOCK TABLES;

DROP TABLE IF EXISTS Horizontal_Fragments;

CREATE TABLE Horizontal_Fragments (
    Fragment_Name VARCHAR(100) NOT NULL,
    Table_Name VARCHAR(20) NOT NULL,
    Attribute VARCHAR(200) NOT NULL,
    Operator VARCHAR(200) NOT NULL,
    Val VARCHAR(200) NOT NULL,
    PRIMARY KEY (Fragment_Name),
    FOREIGN KEY (Table_Name) REFERENCES Tables(Name) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Horizontal_Fragments WRITE;

/*Insert data*/
INSERT INTO
    Horizontal_Fragments
VALUES
    (
        "Food_Item_Chinese",
        "Food_Item",
        "Item_Type",
        "=",
        "Chinese"
    ),
    (
        "Food_Item_Indian",
        "Food_Item",
        "Item_Type",
        "=",
        "Indian"
    ),
    (
        "Food_Item_Italian",
        "Food_Item",
        "Item_Type",
        "=",
        "Italian"
    );

UNLOCK TABLES;

DROP TABLE IF EXISTS Vertical_Fragments;

CREATE TABLE Vertical_Fragments (
    Fragment_Name VARCHAR(100) NOT NULL,
    Table_Name VARCHAR(20) NOT NULL,
    PRIMARY KEY (Fragment_Name),
    FOREIGN KEY (Table_Name) REFERENCES Tables(Name) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Vertical_Fragments WRITE;

/*Insert Data*/
INSERT INTO
    Vertical_Fragments
VALUES
    ("Restaurants_Minimal", "Restaurants"),
    ("Restaurants_Remaining", "Restaurants"),
    ("User_Minimal", "Users"),
    ("User_Remaining", "Users");

UNLOCK TABLES;

DROP TABLE IF EXISTS VF_Columns;

CREATE TABLE VF_Columns (
    Fragment_Name VARCHAR(100) NOT NULL,
    Column_Name VARCHAR(100) NOT NULL,
    PRIMARY KEY(Fragment_Name, Column_Name),
    FOREIGN KEY(Fragment_Name) REFERENCES Vertical_Fragments(Fragment_Name) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES VF_Columns WRITE;

/*Insert data*/
INSERT INTO
    VF_Columns
VALUES
    ("Restaurants_Minimal", "Name"),
    ("Restaurants_Minimal", "Rating"),
    ("Restaurants_Minimal", "Specialty"),
    ("Restaurants_Minimal", "PK_Custom"),
    ("Restaurants_Remaining", "PK_Custom"),
    ("Restaurants_Remaining", "Address"),
    ("Restaurants_Remaining", "Email"),
    ("Restaurants_Remaining", "Num_Reviews"),
    ("User_Minimal", "Name"),
    ("User_Minimal", "Email"),
    ("User_Minimal", "PK_Custom"),
    ("User_Remaining", "Address"),
    ("User_Remaining", "Phone_Number"),
    ("User_Remaining", "PK_Custom");

UNLOCK TABLES;

DROP TABLE IF EXISTS Derived_Horizontal_Fragments;

CREATE TABLE Derived_Horizontal_Fragments (
    Table_Name VARCHAR(20) NOT NULL,
    Fragment_Name VARCHAR(100) NOT NULL,
    Horizontal_Fragment_Name VARCHAR(100) NOT NULL,
    Direct_Fragment INT,
    PRIMARY KEY(Fragment_Name)
    -- FOREIGN KEY (Horizontal_Fragment_Name) REFERENCES Horizontal_Fragments(Fragment_Name) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Derived_Horizontal_Fragments WRITE;

/*Insert Data*/
INSERT INTO
    Derived_Horizontal_Fragments
VALUES
    (
        "Order_Items",
        "Order_Items_Chinese",
        "Food_Items_Chinese",
        1
    ),
    (
        "Order_Items",
        "Order_Items_Indian",
        "Food_Items_Indian",
        1
    ),
    (
        "Order_Items",
        "Order_Items_Italian",
        "Food_Items_Italian",
        1
    ),
    (
        "Orders",
        "User_Restaurant_Order_Amount_Chinese",
        "Order_Items_Chinese",
        0
    ),
    (
        "Orders",
        "User_Restaurant_Order_Amount_Indian",
        "Order_Items_Indian",
        0
    ),
    (
        "Orders",
        "User_Restaurant_Order_Amount_Italian",
        "Order_Items_Italian",
        0
    );

UNLOCK TABLES;

DROP TABLE IF EXISTS Sites;

CREATE TABLE Sites (
    Site INT NOT NULL,
    User_Name VARCHAR(20) NOT NULL,
    Password VARCHAR(12) NOT NULL,
    IP_Address VARCHAR(50) NOT NULL,
    PRIMARY KEY (Site)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Sites WRITE;

/*Insert data*/
INSERT INTO
    Sites
VALUES
    (1, "user", "iiit123", "10.3.5.215"),
    (2, "user", "iiit123", "10.3.5.214"),
    (3, "user", "iiit123", "10.3.5.213"),
    (4, "user", "iiit123", "10.3.5.212");

UNLOCK TABLES;

DROP TABLE IF EXISTS Allocation;

CREATE TABLE Allocation (
    Fragment_Name VARCHAR(100) NOT NULL,
    Site INT NOT NULL,
    PRIMARY KEY(Fragment_Name),
    FOREIGN KEY(Site) REFERENCES Sites(Site) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8;

LOCK TABLES Allocation WRITE;

/*Insert Data*/
INSERT INTO
    Allocation
VALUES
    ("Food_Item_Chinese", 1),
    ("Food_Item_Indian", 2),
    ("Food_Item_Italian", 3),
    ("Restaurants_Minimal", 4),
    ("Restaurants_Remaining", 4),
    ("User_Minimal", 4),
    ("User_Remaining", 2),
    ("Order_Items_Chinese", 1),
    ("Order_Items_Indian", 2),
    ("Order_Items_Italian", 3),
    ("User_Restaurant_Order_Amount_Chinese", 1),
    ("User_Restaurant_Order_Amount_Indian", 2),
    ("User_Restaurant_Order_Amount_Italian", 3);

UNLOCK TABLES;