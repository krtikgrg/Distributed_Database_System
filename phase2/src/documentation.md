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

        WHERE (a == b) or (a!=b) oR (a<b) Or (a>b) 
 
        GROUP BY c2, c3, c4 , c5 
 
        HAVING count(c2)>0, Sum(c3) == 5
    1. kindly ignore the names given to columns /tables , they are used only to represent a general structure.
    1. HAVING clause will always have some aggregate operator on some column.
    1. One can specify an aggregate operator in the columns mentioned after SELECT keyword.
1. Aggregate Operators supported are MIN,MAX,AVG,SUM,COUNT
1. Mathematical Operators supported are =,!=,<,>,<=,>=