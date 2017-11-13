PostgreSQL account: drs2176
URL: http://localhost:8111/
Description:
We implemented our initial design concept, that users would be able to query the database on information of a particular incident. In our part 1.3 submission, users can select any incident by date. Once basic incident information is displayed, users can then choose to query on further details pertaining to that incident. We were not able to add any data visualization, as this required a significant effort with additional APIs. This functionality was replaced with specific queries of interest.

The page http://localhost:8111/query, which is accessed by selecting a date and clicking submit brings the user to introductory details to that incident. The introductory details are a collection of the most relevant data from each table for each incident, giving the user a concise overview of the incident.

From the query page, users can access more specific incident details. The page http://localhost:8111/lookup gives users the ability to look at specific details for each attack such as location, weapons used, and property damage. This allows the user to explore each incident with great flexibility and detail.