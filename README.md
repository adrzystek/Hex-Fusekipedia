# Hex Fusekipedia

## Overview

<p align="justify">
Hex is a strategy board game for two players invented independently by a Danish mathematician Piet Hein and a Nobel laureate John Nash. In spite of having very simple rules, the game has deep strategy, sharp tactics and a profound mathematical underpinning related to the Brouwer fixed point theorem.
</p>
<p align="justify">
Rules of the game are straightforward - players alternate placing pieces on unoccupied spaces in an attempt to link opposite sides of the board in an unbroken chain. One player must win; there are no draws.
</p>
<p align="justify">
Surprisingly, apart from a few rules of thumb, there is very little information about how the game should be played. The project Hex Fusekipedia aims to at least partially fill the gap of human unawareness in this matter. This simple application written in Python collects games from all championship tournaments played on Little Golem server which gathers top hex players. Based on these pieces of data, the application shows a variety of opening moves with their follow-ups played by the best players. Additional information (e.g., concerning the win ratio for a particular move) is also provided. Everything is wrapped in an user-friendly GUI (made with tkinter package).
</p>


## Features

* Browse opening moves for every board size (11x11, 13x13, and 19x19), choosing from championship or individual players' games
* See frequency of a particular move, its win ratio and follow-up moves
* Review games based on the chosen opening sequence
* Download your own (or any player's) games and get surprised by always(or never)-win-moves
* The non-static database - at any time with just a few clicks update the game collection


## Usage

<p align="justify">
Simply download the two listed files (Python script and SQLite database), place them in the same directory and run the script with Python 3.x. The app navigation should be intuitive but additionally there is a help section in the "Info" --> "About Hex Fusekipedia" menu.
</p>


## Details

* The application has been made in Python 3.5 with the use of standard libraries so the issue of a not installed module should not occur. Nevertheless, in case of problems, check whether following packages are installed and can be imported in your Python 3.x (the application should run with any Python 3, however, not all the versions has been tested): time, urllib, re, sqlite3, webbrowser, bs4, tkinter.
* The application has not (but probably should) been written in the model–view–controller pattern what resulted in a bit messy code because of which the author feels sorry for a potential code explorer.


## Contributing

This is my first project so contributions are even more than welcome!
* [Use issue tracker for feedback and bug reports](https://github.com/adrzystek/Hex-Fusekipedia/issues)
* [Send pull requests](https://github.com/adrzystek/Hex-Fusekipedia)
* [Star it on the Github page](https://github.com/adrzystek/Hex-Fusekipedia)
* [Contact me](mailto:andrzej.drzystek@gmail.com)


## Additional information

About the game:
* https://en.wikipedia.org/wiki/Hex_(board_game)
* http://maarup.net/thomas/hex/

About the tkinter package:
* https://docs.python.org/3/library/tk.html
* http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html


## Screenshots

![sc1](https://cloud.githubusercontent.com/assets/26262275/25361195/36a7cea8-294d-11e7-94ba-86364d5c12f6.png)

![sc2](https://cloud.githubusercontent.com/assets/26262275/25361244/6d1e0d1c-294d-11e7-8733-2743f2b896f8.png)

![sc3](https://cloud.githubusercontent.com/assets/26262275/25361308/c6fcf37a-294d-11e7-9abe-808f806ae0d1.png)

![sc4](https://user-images.githubusercontent.com/26262275/29744136-219a4e38-8a9f-11e7-8493-fbc301ab99c8.png)

![sc5](https://cloud.githubusercontent.com/assets/26262275/25361349/04440890-294e-11e7-9494-0b454310ca45.png)


## Further work

The project is considered to be (successfully) completed and is not about to be further developed - at least by the author. However, naturally, there are areas in which the application could be enhanced:
* "free play mode", i.e., a mode which would allow a user to make own moves (for example, in case he or she was curious about a possible alternate sequence and would like to check it on their own) with a possibility to get back to the actual position;
* easier (previous) move browsing - e.g., with a slider;
* making the application in a web technology so that it could be uploaded on a web page and thus made available to a wider audience.
Anyone willing to take up any of abovementioned tasks is warmly encouraged to do so! (And of course to contact me for any advice).


## License

See the [LICENSE](https://github.com/adrzystek/Hex-Fusekipedia/blob/master/LICENSE) file for license rights and limitations.
