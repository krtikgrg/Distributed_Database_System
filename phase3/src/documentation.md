1. Assuming that only one sql query will be entered at a moment.
1. Assuming that each sql query will be terminated with a semi-colon(;).
1. The command "exit" or "quit" followed with a semi-colon can be used to exit the system.
1. We do not expect keywords to be used as variables/relation names.
1. We can run in debug mode, in which we can see additional debug statements which will appear in the terminal.
1. Run server.py file to run the system.
1. Only supports natural join.
1. Supports only INNER JOIN.
1. Does not support "JOIN" keyword.
1. To specify a join in the system, the following command has to be given
    1. SELECT * FROM A,B WHERE A.col1 = B.col2
    1. Here A,B are the tables between which we want to perform the join.
    1. col1 and col2 are the respective columns in A,B on which we want to perform the join.
1. General Query Structure that is assumed while writing the code is
    1. SELECT col1, col2 , col3 ,col4,col5

        FROM t1,t2 , t3 , t4

        WHERE (a = b) or (a!=b) oR (a<b) Or (a>b) 
 
        GROUP BY c2, c3, c4 , c5 
 
        HAVING count(c2)>0, Sum(c3) = 5
    1. kindly ignore the names given to columns /tables , they are used only to represent a general structure.
    1. HAVING clause will always have some aggregate operator on some column.
    1. One can specify an aggregate operator in the columns mentioned after SELECT keyword.
1. Aggregate Operators supported are MIN,MAX,AVG,SUM,COUNT
1. Mathematical Operators supported are =,!=,<,>,<=,>=
1. Assuming that the conditions given in where and having clause are in CNF
    1. Further in CNF we assume each condition in conjunction will come in parenthesis like (cond1) AND (cond2)
    1. Where cond1 will be a union of smaller conditions which will occur without parenthesis like (cond11 OR cond12)
    1. Above cond11 for where clause is of the form attribute_operator_attribute or attribute_operator_value.
    1. Since we support having clause to only come with aggregate operators therfore each cond11 in having clause will follow the format AGGREGATE_OPERATOR(attribute)_operator_value
    1. There should not be any spaces in cond11.
    1. Example for where clause can be
        1. (a>b) AND (c=5 OR d=10) AND (e=f)
    1. Example for having clause can be
        1. (count(a)>10 OR count(b)>5) AND (sum(c)=5 OR max(d)<10)
1. For general optimization of the initial query tree without localization
    1. The select conditions will be like C1 AND C2, where C1 and C2 can themselves be a combination of certain OR conditions.
    1. If all the conditions involved in OR are only using attributes from only one of the tables/childeren nodes only then it will be moved down the line. Otherwise that select condition will stay where it is.
1. Numeric Data-Types are only supposed to be of INT type, float data type is not handled.
1. Assuming no relation with a composite key will be fragmented.
1. Assuming that VFs will have no column common in them except the key column
1. Assuming that the number of joins in a query will be less than or equal to 9
1. Assuming that the horizontal fragments condition will be of the type attribute OPER value and it cannot be value1 OPER attribute OPER value2 that is 'col1 < 5' is acceptable but '5 < col1 < 10' is not acceptable.
1. 2 relations can not have multiple joins on different attribute pairs, they are supposed to only have one join on one pair of attributes (one from each relation).
1. This distribution supports only int, float and varchar data types in sql
1. Assuming that all the column names of all the relations are unique, no pair of attribute names match with each other.
1. In the last commit, the above required is removed. Now the only requirement is that the names of columns inside a relation must be unique