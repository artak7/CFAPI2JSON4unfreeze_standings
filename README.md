# CodeForces API to JSON for ICPC Standings Resolvers

The code of this repository contains python script that can be used to get JSON in special format to simulate what happens in the frozen time during a competitive programming competition with the ICPC standard rules.
Script takes information about contest from codeforces.com via API and convert it to JSON in format [S4RIS](https://github.com/OStrekalovsky/S4RiS-StanD) or [neoSaris](https://github.com/equetzal/neoSaris) and then you can use it in these apps.

Recently I was the organizer of the ICPC Olympiad and at the closing I wanted to show the unfreezing of the table, but unfortunately, `neoSaris` was unable to download data from the private Codeforces contest and I decided to write my own script.

## How to Use

fill in the contest data in `settings.txt`

Two formats are supported: `neoSaris` and `S4RIS`

If the contest was held in a private group, you need to generate an api key on the page https://codeforces.com/settings/api

more details https://codeforces.com/apiHelp

Run python script and you will get one JSON file in requested format and two JSON files with pure data from requests to Codeforces API

Then you can use it in https://neosaris.huronos.org or http://ostrekalovsky.github.io/S4RiS-StanD/

