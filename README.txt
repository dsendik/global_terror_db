PostgreSQL account: drs2176
URL: http://35.196.23.41:8111/
Description:
We implemented our initial design concept, 
that users would be able to query the database 
on information of a particular incident. In our 
part 1.3 submission, users can select any incident 
by date the incident occurred from a dropdown 
selection box. Once basic incident information is displayed, 
users can then choose to query on one of five collections of
details pertaining to the selected incident. We were not able to add 
any data visualization, as this required a significant 
effort with additional APIs. This functionality was 
replaced with specific queries showing interesting attacks and a
keyword search.

http://localhost:8111/lookup
After initially querying on a date on the homepage,
The user has the option to learn further about their chosen incident.
From the query page, users can select from a list of 5 collections
of further details. These collections are directly related to the 
tables that will be queryed. The 5 collections are location, 
weapons used, government report, related events, and property damage. 
Depending on what collection the user selected, a different sql
query is executed. For the location collection, the user enters their
desired event_id and a query is executed to match that event with the
coinciding database entry. From the location table, a table is generated
showing the date, latitude and longitude points, country, and city pertaining
to the selected event. The 4 remaining selection options execute similar
queries on their respective tables. (weapons table is queryed for selection
'What weapons did they use', investigated_by_govt table is queryed for selection
'Government Report' etc.)

http://localhost:8111/search
On the homepage, the user enters their search word 
into the text box labeled 'Search the database:' 
and clicks submit. This triggers server.py to run a
sql query using the search word in numerous WHERE clauses.
Through a complex sql query, many key tables are joined
together. The tables joined together are weapons, utilized, 
perpetrators, attacked, incident, located_in, targets, and location.
The user's search word is entered as a variable into a series of 
WHERE clauses. All rows in any table listed above that contains 
the user's search text is returned in a table on the search page.
This is primarily achieved through using the sql keyword LIKE to
match any text in the tables similar to the user's search word.
