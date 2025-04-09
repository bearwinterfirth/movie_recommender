## Movie Recommender

Syftet med denna applikation är att rekommendera filmer för användaren. Användaren ska kunna skriva in en filmtitel, och få tillbaka titlarna på fem andra filmer som hen troligen kommer att tycka om.

#### Abstract
Grundtanken var att göra ett dataset med filmtitlar som index, och kolumner med så mycket (kvantitativ) information som möjligt för varje film, för att därefter kunna använda cosinus-likhet för att ta reda på vilka filmer som har mest gemensamt. Den information som användes var: *Betyg från andra användare*, *Genre*, *Tag* och *Årtal*.

#### Dataset som används
Tre datafiler lästes in som dataframe:
- movies.csv med kolumnerna *movieId*, *titles*, *genres*
- ratings.csv med kolumnerna *userId*, *movieId*, *ratings*, *timestamp*
- tags.csv med kolumnerna *userId*, *movieId*, *tag*, *timestamp*
Av dessa slogs *movies* och *ratings* ihop till ett gemensamt dataframe, kallat **merge**, med *movieId* som index. Detta låg sedan till grund för den pivottabell som senare skapades. (*Movies* sparades också som enskilt dataset, för att kunna para ihop titlar med movieId.)

#### Genrer
Varje film kan tillhöra en eller flera *genrer*. Till skillnad från *tags*, som enskilda användare fått ange, är *genrer* inte subjektiva utan förbestämda, kanske av filmbolaget. Sammanlagt finns ca 20 olika genrer. Eftersom de var listade i en och samma kolumn åtskiljda endast av '|', gjordes först en extrahering av dessa, och därefter skapades (m.h.a. funktionen *create_set_of_genres*) ett *set* med alla 20 genrer (utan dubletter.) Varje genre gjordes därefter till en kolumn i *movies*-dataframet, och *one-hot-encoding* tillämpades; varje film fick alltså en 1:a för varje genre den tillhörde, annars en 0:a. Detta gjordes med funktionen *genres_one_hot_encoding*.

#### Tags
Varje användare har haft möjlighet att sätta en eller flera fritext-*tags* på filmer som hen betygsatt. Varje film kan alltså ha fått många olika tags, men även flera av *samma* tag. Ett stort antal användare har exempelvis satt tagen *Kate Winslet* på filmen *Titanic*. Sammanlagt fanns över 150 000 olika tags, vilket var för mycket att hantera. Med hjälp av funktionen *make_shorter_taglist* sorterades alla tags som använts mindre än 1000 gånger bort, vilket resulterade i en *shorter_taglist*. Det skapades även en kolumn med 1:or, för att lättare kunna summera antalet gånger varje tag använts för en film, och senare lägga in detta i pivottabellen. 

#### Nedbantning av dataset
Innan en pivottabell kunde skapas av det sammanslagna dataframet *merged*, konstaterades det att det var mycket stort och "tungarbetat". Därför gjordes flera avgränsningar med hjälp av funktionen *narrowing_the_field*:
- Hela dataframet halverades genom att bara använda betyg med jämna *timestamps*, alla udda timestamps sorterades alltså bort. (Detta betydde naturligtvis inte att hälten av alla filmer sorterades bort, bara hälften av alla satta betyg.) Enstaka filmer kan ha försvunnit i denna rensning, men det rör sig i så fall om mycket "okända" filmer, med bara ett eller ett fåtal satta betyg.
- Det gjordes en rejäl bantning av det stora antalet användare, vilket inte bedömdes ha någon avgörande effekt på betygsättningen; det fanns tillräckligt många kvar ändå. Det beslöts att endast behålla betygen från användare som satt mellan 80 och 120 betyg, alltså en förhållandevis liten andel av samtliga användare. Förutom den redan nämnda önskan om en räjäl nedskärning, önskades dessutom att både "nybörjar-användare" med mycket få betyg, och "proffs-tyckare" med extremt många betyg, skulle rensas bort. De som fanns kvar fick representera något slags "vardags-användare" (*everyday_users*), vilket är den typ av användare som applikationen i första hand vänder sig till.
- Även antalet filmer bantades ned. De filmer som hade färre än 100 betyg valdes bort, vilket naturligtvis innebar att många mindre, "smalare" filmer försvann. (Men det är ju trots allt bättre att applikationen rekommenderar populära filmer än impopulära filmer.)
- Det nya smalare datasetet sparades under namnet *short_movie_list*. Här fanns alltså filmtitlar och tillhörande betyg från ett (fortfarande ganska stort) antal användare.

#### Pivottabell
Därefter skapades en pivottabell av *short_movie_list*, med filmtitlar som index och en kolumn för varje användare som satt betyg. Betygen är på en 10-gradig skala, 0.5 - 5. Om en användare inte satt betyg på respektive film, står det en 0:a.

