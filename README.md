# CodingBat Grade Pull

Generate a CSV from the CodingBat teacher share report, printing changes to the terminal. This makes checking student 
progress much easier.

The BeautifulSoup code used to log in to the website and retrieve the report was written entirely by Thomas Kiesel. I 
added some modifications to the way the most recent report is compared to the second most recent, preventing possible 
errors when students are added or removed from the report.

I plan to add additional features, such as improving the readability of the printed data. Suggestions and contributions
welcome! 