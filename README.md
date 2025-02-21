# find turnaments on FITP
A python program that navigate on the site of the FITP to find tennis tournaments in Italy

At the site site: https://www.fitp.it/Tornei/Ricerca-tornei are displayed all tennis tournaments in Italy so using the python's library Selium.
Using this python program it is possibile to see all tournamnets in program, it is possible to applay some basics filter like:
- region (from the ones avaible in the site)
- type (mes, womens and duoble)

### Extra features
There is also some features that using the site is not possible to use.
Adding inside the file '[personal information](/find_turnaments_FITP/main_code/personal_info.json)' the informations required that are:
- ranking -> your person ranking
- adress -> the place where you start from to go and play
- google maps api-key -> you have to create your personal google maps api [link](https://developers.google.com/maps?hl=it)

in this way it is possible to display in [file](/find_turnaments_FITP/main_code/turnaments.csv) only the tournaments that you can partecipate with your ranking and filter the tournaments that are too far away (max 1h by car)
**the program will work also without this informations**

