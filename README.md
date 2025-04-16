## Movie Recommender

Syftet med denna applikation är att rekommendera filmer för användaren. Användaren ska kunna skriva in en filmtitel, och få tillbaka titlarna på fem andra filmer som hen troligen kommer att tycka om.

Grundtanken var att göra ett dataset med filmtitlar som index, och kolumner med så mycket (kvantitativ) information som möjligt för varje film, för att därefter kunna använda cosinus-likhet för att ta reda på vilka filmer som har mest gemensamt. Den information som användes var: *Betyg från andra användare*, *Genre*, *Tag* och *Årtal*.

#### Dataset som används
Tre datafiler lästes in som dataframe:
- movies.csv med kolumnerna *movieId*, *titles*, *genres*
- ratings.csv med kolumnerna *userId*, *movieId*, *ratings*, *timestamp*
- tags.csv med kolumnerna *userId*, *movieId*, *tag*, *timestamp*

Av dessa slogs *movies* och *ratings* ihop till ett gemensamt dataframe, kallat **movies_with_ratings**, med *movieId* som index. Detta låg sedan till grund för den pivottabell som senare skapades. (*Movies* sparades också som enskilt dataset, för att kunna para ihop titlar med movieId.)

#### Genres
Varje film kan tillhöra en eller flera *genres*. Till skillnad från *tags*, som enskilda användare fått ange, är *genres* inte subjektiva utan förbestämda, kanske av filmbolaget. Sammanlagt finns ca 20 olika genres. Eftersom de var listade i en och samma kolumn åtskiljda endast av '|', gjordes först en extrahering av dessa, och därefter skapades (m.h.a. funktionen *create_set_of_genres*) ett *set* med alla 20 genres (utan dubletter.) Varje genre gjordes därefter till en kolumn i *movies*-dataframet, och *one-hot-encoding* tillämpades; varje film fick alltså en 1:a för varje genre den tillhörde, annars en 0:a. Detta gjordes med funktionen *genres_one_hot_encoding*.

#### Tags
Varje användare har haft möjlighet att sätta en eller flera fritext-*tags* på filmer som hen betygsatt. Varje film kan alltså ha fått många olika tags, men även flera av *samma* tag. Ett stort antal användare har exempelvis satt tagen *Kate Winslet* på filmen *Titanic*. Sammanlagt fanns över 150 000 olika tags, vilket var för mycket att hantera. Med hjälp av funktionen *make_shorter_taglist* sorterades alla tags som använts mindre än 1000 gånger bort, vilket resulterade i en *short_taglist*. Det skapades även en kolumn med 1:or, för att lättare kunna summera antalet gånger varje tag använts för en film, och senare lägga in detta i pivottabellen. 

#### Nedbantning av dataset
Innan en pivottabell kunde skapas av det sammanslagna dataframet *movies_with_titles*, konstaterades det att det var mycket stort och "tungarbetat". Därför gjordes flera avgränsningar med hjälp av funktionen *narrowing_the_field*:
- Hela dataframet halverades genom att bara använda betyg med jämna *timestamps*, alla udda timestamps sorterades alltså bort. (Detta betydde naturligtvis inte att hälten av alla filmer sorterades bort, bara hälften av alla satta betyg.) Enstaka filmer kan ha försvunnit i denna rensning, men det rör sig i så fall om mycket "okända" filmer, med bara ett eller ett fåtal satta betyg.
- Det gjordes en rejäl bantning av det stora antalet användare, vilket inte bedömdes ha någon avgörande effekt på betygsättningen; det fanns tillräckligt många kvar ändå. Det beslöts att endast behålla betygen från användare som satt mellan 80 och 120 betyg, alltså en förhållandevis liten andel av samtliga användare. Förutom den redan nämnda önskan om en räjäl nedskärning, önskades dessutom att både "nybörjar-användare" med mycket få betyg, och "proffs-tyckare" med extremt många betyg, skulle rensas bort. De som fanns kvar fick representera något slags "vardags-användare" (*everyday_users*), vilket är den typ av användare som applikationen i första hand vänder sig till.
- Även antalet filmer bantades ned. De filmer som hade färre än 100 betyg valdes bort, vilket naturligtvis innebar att många mindre, "smalare" filmer försvann. (Men det är ju trots allt bättre att applikationen rekommenderar populära filmer än impopulära filmer.)
- Det nya smalare datasetet sparades under namnet *short_movie_list*. Här fanns alltså filmtitlar och tillhörande betyg från ett (fortfarande ganska stort) antal användare.

#### Pivottabell
Därefter skapades en pivottabell (den som kom att användas som *designmatris*) av *short_movie_list*, med filmtitlar som index och en kolumn för varje användare som satt betyg. Betygen var på en 10-gradig skala, 0.5 - 5. Om en användare inte satt betyg på respektive film, står det en 0:a. Tiill denna pivottabell lades sedan fler kolumner, se nedan:

#### Lägga till tags till pivottabellen
Förutom betygen på filmerna så önskades även kolumner med filmernas tags i pivottabellen. Med hjälp av funktionen *merge_movie_pivot_with_tags* skapades först en pivottabell för alla tags, med *movieId* som index och varje enskild tag som kolumnrubrik, och där värdet i kolumnen var lika med antalet användare som angett just den tagen för just den filmen. Detta gjordes med hjälp av *aggfunc="sum"*-funktionen, där alla 1:or (se *Tags*-avsnittet) summerades. Denna pivottabell slogs först samman med *movies*-datasetet, för att para ihop rätt id med rätt titel, och därefter med den huvudsakliga pivottabellen (även känd som *designmatrisen*). Eftersom *merge*-funktionen användes, blev eventuella filmer som har fått tags, men däremot inte fanns med i designmatrisen, helt enkelt utlämnade vid sammanslagningen.

#### Lägga till genres i pivottabellen
Det kan tyckas onödigt att ange både genres och tags för en film, då dessa i flera fall överlappar. Men som tidigare nämnts är genres "förbestämda", och inte subjektiva som tags. Dessutom kan många filmer sakna tags, medan alla filmer har en genre (med undantag för ett litet fåtal). Genres angavs, som tidigare nämnts, med one-hot-encoding, så med hjälp av funktionen *merge_movies_pivot_with_genres* lades 20 genre-kolumner till designmatrisen, där en film fick en 1:a för varje genre den ansågs tillhöra.

#### Extrahera år
En sista kolumn lades till designmatrisen, närmare bestämt filmernas årtal. Med hjälp av funktionen *extract_year* hämtades årtalet för varje film, tack vare att alla filmtitlar avslutades med årtalet inom parentes. Tecken nummer 2, 3, 4 och 5 räknat från slutet av strängen extraherades och lades till en egen kolumn, där de omvandlades till heltalsformat.

#### Skalering
Värdena i designmatrisen var av många olika slag; betyg upp till 5 (där de högre betygen är mycket vanligare än de lägre), tags som kan gå upp till flera hundra, genres som är 0 eller 1, och slutligen årtal ända från 1920-talet upp mot 2010-talet. Det var tydligt att en skalering behövde göras, närmare bestämt en standardisering, så att varje kolumn fick medelvärdet 0 och standardavvikelsen 1 (detta var extra viktigt för betygskolumnerna, de höga betygen blev nu mer utspridda, så att ett "medelbetyg" snarast hamnade i närheten av 4). Det hade varit önskvärt att göra en MinMax-skalering också, eftersom flera av värdena är av typen "0 ska betyda 0", men eftersom en principalkomponentanalys gjordes i nästa steg, så var det olämpligt med en MinMax-skalering.

#### Principalkomponentanalys
Med tanke på att många av kolumnerna i designmatrisen innehåller samma eller liknande information (användare har betygsatt lika; genres och tags överensstämmer, etc.) så beslöts att minska dimensionaliteten genom att göra en *principalkomponentanalys* (PCA). Efter att ha analyserat kolumnerna med hjälp av *pca.explained_variance_ratio_* beslöts att antalet kolumner kunde minskas från drygt 1900 till 1000, utan alltför stora informationsförluster (ca 0.85 på *explained variance ratio*).

#### Likhet mellan filmer
För att jämföra filmerna på ett inte alltför tidskrävande sätt, och hitta de filmer som mest liknar varje given film, valdes att använda *cosine_similarity*. Resultatet blev alltså en kvadratisk matris där varje film fick ett värde mellan 0 och 1 som mått på hur lik den är varje annan film. I funktionen *five_films* valdes de fem filmer ut som fått mest poäng (med undantag för den egna filmen, som förstås fick det maximala likhetsvärdet 1). 

Det är endast denna sista funktion som anropas varje gång användaren vill testa en "ny" film.


*Observera att filerna med dataseten är för stora för att ladda upp till github. För att köra applikationen behöver därför sökvägarna till filerna ändras från de nuvarande "lokala" sökvägarna.*
