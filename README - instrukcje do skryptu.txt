1. Upewnić się, że poniższe funkcje/programy są zainstalowane:
	-Visual Studio Code
	-Node.js
	-Pip
	-Python
	-Playwright
2. Pobrać plik 'Cookies Analityczne Playwright.py' i uruchomić w Visual Studio Code.
3. Uruchomić skrypt przyciskiem 'Play' w prawym, górnym rogu.
4. Skrypt sprawdza 3 przeglądarki jednocześnie (Chrome, Edge, Firefox).
5. Schemat działania kodu:
	-Wejście na stronę 'ing.pl'
	-Kliknięcie przycisku 'Dostosuj' w menu wyboru ciasteczek bądź 'Ustawienia plików cookie', jeśli to kolejna wizyta na stronie
	-Usuniecie cookies z pamięci, jeśli oba powyższe przyciski nie zostaną znalezione i powrót do wejścia na stronę
	-Sprawdzenie czy opcja 'Cookies analityczne' jest włączona i czy opcja 'Cookies marketingowe' jest wyłączona
	-Kliknięcie przycisku 'Zaakceptuj wybrane'
	-Zamknięcie przeglądarki i zapisanie wyników w terminalu oraz w pliku tekstowym o nazwie 'results.txt'
	-Jeśli w zapisanych cookies znajduje się fragment (name='cookiePolicyGDPR', value='3), wyświetlona zostanie informacja, że cookies analityczne zapisywane są prawidłowo
	-Legenda do powyższego pliku cookie, zmiana parametru 'value' zmienia rodzaj zapisywanych plików:
		Tylko konieczne - 1
		Marketing - 2	
		Analityczne - 3
		Wszystkie - 4