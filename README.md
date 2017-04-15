# CloudBot-plugins
My additional CloudBot plugins. Many of the plugins output data in Finnish, as many of these plugins are tied to Finland.

In addition to CloudBot's requirements, many of the plugins also require Beautiful Soup 4,
which can be installed via pip: `pip install beautifulsoup4`. If you don't have root access, you can pass the `--user` flag to
pip.

Every plugin is licensed with GPLv3.

### almanakka (Finnish)
Outputs name day information (Finnish, Swedish, Orthodox and Sami) for the current day. If the current day is also a flag day,
it will also output which flag day is it.

### ask (warning, conflicts with CloudBot's `chatbot.py`)
Answers yes or no questions. It can also pick an item from a list, by separating different options with `or` e.g.
`.ask pancakes or waffles or something healthy`. You can also ask multiple questions at a time by separating questions with `&&`
e.g. `.ask a question && 1 or 2 or 3 or 4 && another question`.

This plugin conflicts with `chatbot.py` as both plugins hook the command `ask`. To circumvent this, you can either remove the
hook from the code in either `chatbot.py` or in `ask.py`.

### bmi
Simple body mass index calculator. Suppors metric measures only. Usage: the first parametre is (obviously) weight in kilogrammes
and the second parametre is height in centimetres or metres e.g. `.bmi 79 190` and `.bmi 82 1.85`.

### distance (requires an api key)
Calculates the total trip distance. Locations are separated with `;`. For example, `.dist helsinki; turku; tampere; helsinki`
outputs the total trip distance when going from Helsinki to Turku to Tampere and back to Helsinki.

This plugin requires an api key which you can get from [here](https://business.mapquest.com/developer-apis-sdks/). Once you
have the api key, modify line 19 in `distance.py`.

### episodate
Finds information on tv-series, including the next air date. Usage: `.ed Mr. Robot`. If multiple shows are found with a search
query, you can include `, <number>` to your search query to scroll through the results. For example `.ed rick, 2` will output 
the second search result.

### fmi (Finnish, requires an api key)
Outputs current weather data fetched from the Finnish Meteorological Institute's api. You can set a default location with
`.setlocation <location>`. Usage: `.sää turku`, or just plain `.sää` if you've set a default location.

This plugin requires an api key which you can get from [here](https://ilmatieteenlaitos.fi/avoin-data). Once you have the api key,
modify line 24 in `fmi.py`.

### kesko (Finnish)
Outputs the opening and closing times of Kesko grocery stores. Usage: `.kesko <search terms()>`. If multiple results are found,
you can include `, <number>` to your query (similarly as with episodate).

### kuha (Finnish)
Fetches a random quote from Lannistajakuha. Usage: `.kuha [number]`.

### s-ryhma (Finnish)
Similar to kesko.py. Outputs the opening and closing times of S Group grocery stores. Usage: `.X <search term(s)>`,
where X is sryhmä, alepa, sale, smarket or prisma. If multiple results are found,
you can include `, <number>` to your query (similarly as with episodate).

### urbaanisanakirja (Finnish)
The Finnish equivalent to Urban Dictionary. Usage: `.us <search term(s)>`. If multiple results are found,
you can include `, <number>` to your query (similarly as with episodate).
