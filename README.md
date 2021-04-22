# trust_game
Senior Research Project
Socket io has been a real issue so far the packages that worked were as follows.
Flask-SocketIO==4.3.1
python-engineio==3.13.2 
python-socketio==4.6.0
Use pip-freeze to check the dependencies
Used this code to create a wave effect with css animations
https://www.instagram.com/p/CBBPQ01ge7J/
Little bit of trouble with the progress bar on chat.html
Resolved by putting it in the chatbox div
Glitch Text: https://www.youtube.com/watch?v=7Xyg8Ja7dyY
Neon Button: https://www.youtube.com/watch?v=ex7jGbyFgpA&t=0s
Page Transitions: https://www.youtube.com/watch?v=ckJ7gdIeebc
Had an issue with chrome not updating changes in the actual code, if this issue occurs again just clear the cache in chrome. 
Speech Bubbles for Narrator: https://www.youtube.com/results?search_query=javascript+speech+bubble
To avoid having a huge text bubble when I got a lot of text, I tried many different methods to get rid of the spans, get rid of the divs, everything. What ended up working was “hiding” the spans that were created in the ‘revealOneCharacter’ method. Hiding them let the other spans go on top of them so there isn’t just blank text lying around which is what I thought would happen. Also utilized a proxy so functions wouldnt overlap each other due to the delay that I was using between spans. 
Javascript Timer
Something that did not work initially was the timer. This is because the countdown element was not loading in and was coming in as null.
To fix this, you have to only access the timer element only when the element loads in. 
However, this implementation did not include a server-side implementation. 
Gained full functionality of timer from client side on to server side.
Had an issue where timer would send 2 different times to the two different users if one of them refreshed the browser. Fixed this issue by only letting the timer start when someone pushes a button. I can better this functionality by only having it start when both players “ready up”.
Voting for each of the 5 games.
Couple of conditions that have to be satisfied behind the scenes.
Each player can only vote once, so they have 2 buttons, but only one click can be registered.
Only two total votes can be registered for the room.
These conditions were met server side by recording the number of entries in the database, if the entries was greater than the amount mentioned above
Temp Scoring System: 3/3 , 5/0, 0/5, 1/1. The goal is to get the highest score after x games, right now x is going to be 3. 
All scoring will be kept track of in the server.
#game_num == 1: only cheat
#game_num == 2: only cooperate
#game_num == 3: random
#game_num == 4: tit for tat, start with cooperate
#game_num == 5: sus tit for tat, start with cheat
How the server should behave when time runs out.
If only one person votes, their votes is to be the sole vote.
If no one votes, vote is randomly chosen.
Game_number is to be incremented.
Game_number client side is continually increasing. 
So it should end 5 x (number of rounds per game)
Game_number server side will probably have to be divided to get 1-5 which create the type of players as denoted above.
Now I need to create some sort of pause message when 13 rounds have been played.
Then proceed to play the other 4 strategies ( which also need to be coded up)
Probably will have to create an emit server-side that says you have reached 13, so I release some text onto the screen client-side. Once that is over, emit client-side to restart and the cycle begins again.
Do not create more timer objects, just restart if need be. 
Timer is creating many issues. Will definitely rework how the timer works, because right now there are too many variables and the code is far too unstable. Might just use break statements to get out of while loop and if the while ends just create a new timer. This way we can create a new timer for each individual machine game.
-Creating multiple ‘timers’ seems to have worked, eventually will have to only start when both users click start but that shouldn't take too much time and we can do that in the final front end design.
- Logic behind the PvP: 
- 30 second timer for each round, then it chooses random
- 3 rounds of 13
- For an extension, save this data of the average player, the data that would be most interesting to save would be:
- First move
- ratio : to copy or not to copy (would add to 1)
- In database: games 100 - 139
- Player 1 and Player 2 need to be determined
- Currently having troubles with restarting the timers in the PVP
- I believe I found a fix, I just create a new timer once the old timer is completely reset, not recursion, but the function is called inside the function, but it is at the end, to guarantee that it is reset.
- Now must work on creating the 3 rounds of 13, 
- The rounds of 13 appear to work pretty well, need to of course add some sort of animation/break in between but that will be worked on during front end time. 
- Across all timers, once the timer resets, it counts the next second as well, so if the timer is at 9 when both players cast their choice, it will go to 8, and then reset to 11. This may not pose such a big problem in a real world application, however I don’t know what will happen if two players were to cast their next choices in that 1 second interval.
- Work on a way of saving the data in either a mysql database or perhaps just a python array. 	
- Need to determine the goal of this game, the options are:
- To simply defeat the opponent
- To gain the most amount of points
- To create the largest point differential
- After determining this, I can create the situation, then have the characters drawn, whether they need to be prisoners or not. 
- One possible situation could be that you are a businessman and you are trying to maximize profits over a rival businessman. You guys make consequential business moves. 
- I am currently able to store the data in a python array.
- The first move tally is going to be stored with room=room, user=user, game_num=1000, vote=move(1 or 2)
- Query with game_num = 1000


