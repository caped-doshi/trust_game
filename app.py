from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import random

from datetime import datetime

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/ballot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Votes(db.Model):
    __tablename__ = 'votes'
    id = db.Column('id', db.Integer, primary_key=True)

    user = db.Column('user', db.String(50))
    room = db.Column('room', db.String(50))
    game_num = db.Column('game_num', db.Integer)#integer that will be 0-4 or 1-5
    vote = db.Column('vote', db.Integer)
    date_created = db.Column('date_created', db.DateTime, default=datetime.now)

Session(app)

socketio = SocketIO(app,cors_allowed_origins="*")

@app.route('/')
def home():
    return render_template('intro.html')

@app.route('/login', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/game1', methods=['GET', 'POST'])
def game1():
    return render_template('game1.html')

@app.route('/game1vote', methods=['GET', 'POST'])
def game1vote():
    return render_template('game1vote.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        username = request.form['username']
        room = request.form['room']
        #Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session = session)
    else:
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

@socketio.on('vote', namespace='/chat')
def handleVote(ballot):
    room = session.get('room')
    user = session.get('username')
    vote = Votes(user=user, room=room, vote=ballot)
    db.session.add(vote)
    db.session.commit()

    #Acquire the latest entry, results1.vote is the most recent vote
    results1 = Votes.query.filter_by(room=room,vote=1).count()
    results2 = Votes.query.filter_by(room=room,vote=2).count()

    emit('vote_results', {'results1': results1, 'results2': results2}, room=room)

numClients = dict()

def toString(lst):
    stringLst = []
    for i in lst:
        stringLst.append(str(i))
    return " | ".join(stringLst)

        ####        MACHINE GAME VARS       ####

machine_scores = dict() #actual scores of player and machine
machine_game = dict()  #moves of playre and machine
game_number = 1 #goes to 65, 5x13
cpu_number = dict() #goes 1 to 5
machine_game_started = False #cannot go back to False
machine_game_ended = False # turns to true when timer runs out
timer_restart = False
gamePause = False #after the first 13 rounds, pause, unpause


    ####        MACHINE GAME VARS       ####

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)

    if room not in numClients:
        numClients[room] = 1
    else:
        numClients[room] += 1

    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)

    emit('message', {'msg': 'There are currently ' + str(numClients[room]) + ' users in this room.'}, room=room)

    if numClients[room] > 0: #change later
        emit('next_room', room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')

    numClients[room] -= 1

    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@app.route('/vs_machine', methods=['GET', 'POST'])
def vs_machine():
    if (request.method == 'POST'):
        username = request.form['username']
        room = request.form['room']
        # Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('vs_machine.html', session=session)
    else:
        if (session.get('username') is not None):
            return render_template('vs_machine.html', session=session)
        else:
            return redirect(url_for('index'))

@socketio.on('join1', namespace='/vs_machine')
def join(message):
    room = session.get('room')
    join_room(room)

    if room not in numClients:
        numClients[room] = 1
    else:
        numClients[room] += 1

    emit('status1', {'msg':  session.get('username') + ' has entered the room.'}, room=room)

    emit('message1', {'msg': 'There are currently ' + str(numClients[room]) + ' users in this room.'}, room=room)

@socketio.on('text1', namespace='/vs_machine')
def text(message):
    room = session.get('room')
    emit('message1', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)


@socketio.on('left1', namespace='/vs_machine')
def left(message):
    room = session.get('room')

    numClients[room] -= 1

    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status1', {'msg': username + ' has left the room.'}, room=room)


@socketio.on('test_timer', namespace='/vs_machine')
def timer(time):
    global machine_game_started
    machine_game_started = True
    global machine_game_ended
    global timer_restart
    global gamePause

    machine_game_ended = False
    room = session.get('room')

    emit('message1', {'msg': "timer connected with " + str(time['seconds'])}, room=room)

    t = time['seconds']
    if timer_restart:
        timer_restart = False
    if gamePause:
        gamePause = False
    while t > -1:
        if timer_restart:
            t = -1
            timer_restart = False
        else:
            emit('test_timer_reply', {'msg': t}, room=room)
            #emit('message1', {'msg': "time finished"}, room=room)
            socketio.sleep(1)
            t -= 1
    if t == -1 or t == 0:
        machine_game_ended = True
        # timer({'seconds': 15})
        emit('timer_over',{},room=room)

# @socketio.on("startNextGame", namespace=

# @socketio.on('test_timer_start', namespace='/vs_machine') #use when in middle of timer and want to continue
# def timer_start(data):
#     global pause
#     global machine_game_started
#     machine_game_started = True

@socketio.on('test_timer_restart', namespace='/vs_machine')
def timer_restart(data):
    global timer_restart
    timer_restart = True


def score(gameNum, player, room): #returns (machine score, player score) ex. (5, 0), (3,3)
    emit('message2', {'msg': toString(machine_game[(room, gameNum)])}, room=room)
    if gameNum == 1: #always cheats
        if player == 1: # player cooperates
            return (5,0)
        else:
            return (1,1)
    elif gameNum == 2:
        if player == 1:
            return (3,3)
        else:
            return (5,0)
    elif gameNum == 3:
        r = random.choice([1,2])
        if player == 1:
            if r == 1:
                return (3,3)
            else:
                return(5, 0)
        else:#player cheats
            if r == 1:
                return (0, 5)
            else:
                return (1, 1)
    elif gameNum == 4:
        arr = machine_game[(room, gameNum)]
        length = len(arr)
        playCheat = True
        if length == 1:
            playCheat = False
        else:
            prevMove = arr[length-2]
            if prevMove == 1:
                playCheat = False
        if playCheat:
            if player == 1:
                return (5,0)
            else:
                return (1,1)
        else: #machine cooperates
            if player == 1:
                return (3,3)
            else:
                return (0,5)
    else:
        arr = machine_game[(room, gameNum)]
        length = len(arr)
        playCheat = True
        if length == 1:
            playCheat = True
        else:
            prevMove = arr[length - 2]
            if prevMove == 1:
                playCheat = False
        if playCheat:
            if player == 1:
                return (5, 0)
            else:
                return (1, 1)
        else:  # machine cooperates
            if player == 1:
                return (3, 3)
            else:
                return (0, 5)


@socketio.on('vote1', namespace='/vs_machine')
def handleVote1(ballot):
    global timer_restart
    room = session.get('room')
    global game_number
    global machine_game_ended
    global cpu_number
    global gamePause
    global timer_restart
    global pause

    if room not in cpu_number:
        cpu_number[room] = 1

    if game_number > 3 * cpu_number[room]:
        gamePause = True
        emit('game_paused', {'msg': "click start to begin the next round"}, room=room)
        emit('message1', {'msg': "click start to begin the next round"}, room=room)
        #emit('message1', {'msg': "GAME NUMBER: " + str(game_number)}, room=room)
        cpu_number[room] += 1
        #emit('message1', {'msg': "CPU NUMBER: " + str(cpu_number[room])}, room=room)
        timer_restart = True
    else:
        emit('message1', {'msg': "GAME NUMBER: " + str(game_number)}, room=room)
        emit('message1', {'msg': "CPU NUMBER: " + str(cpu_number[room])}, room=room)
        #emit('message1', {'msg': "Machine game started: " + str(machine_game_started)}, room=room)
        #emit('message1', {'msg': "Machine game ended: " + str(machine_game_ended)}, room=room)
        if machine_game_started:
            if not machine_game_ended:

                user = session.get('username')

                # game_number = ballot['gn']

                # Acquire the latest entry, results1.vote is the most recent vote
                results1 = Votes.query.filter_by(room=room, game_num=ballot['gn'], vote=1).count()
                results2 = Votes.query.filter_by(room=room, game_num=ballot['gn'], vote=2).count()

                results3 = Votes.query.filter_by(room=room, game_num=ballot['gn'], user=user).count()

                total = results1 + results2
                if total < 2 and results3 == 0:
                    vote = Votes(user=user, room=room, game_num=ballot['gn'], vote=ballot['vote'])
                    db.session.add(vote)
                    db.session.commit()

                    #must be updated after the vote was committed
                    results1 = Votes.query.filter_by(room=room, game_num=ballot['gn'], vote=1).count()
                    results2 = Votes.query.filter_by(room=room, game_num=ballot['gn'], vote=2).count()

                    emit('vote_results1', {'results1': results1, 'results2': results2}, room=room)
                result = 0
                if results1 + results2 == 2:
                    if (room, cpu_number[room]) not in machine_game:
                        machine_game[(room,cpu_number[room])] = []
                    if (room, cpu_number[room]) not in machine_scores:
                        machine_scores[(room, cpu_number[room])] = [0,0]
                    if results1 == 0:
                        result = 0
                        machine_game[(room, cpu_number[room])].append(1)
                    elif results2 == 0:
                        result = 1
                        machine_game[(room, cpu_number[room])].append(1)
                    else:
                        r = random.choice([1,2])
                        machine_game[(room, cpu_number[room])].append(r)
                        result = r

                    s = score(cpu_number[room], result, room)
                    m_score = s[0]
                    player_score = s[1]

                    machine_scores[(room, cpu_number[room])][0] += m_score
                    machine_scores[(room, cpu_number[room])][1] += player_score

                    emit('vote_finished1', {'m_score': machine_scores[(room, cpu_number[room])][0], 'player_score': machine_scores[(room, cpu_number[room])][1]}, room=room)
                    emit('vote_finished', {'results1': results1, 'results2': results2}, room=room)
                    timer_restart = True
                    game_number += 1
            else:
                room = session.get('room')
                user = session.get('username')
                emit('message1', {'msg': 'timer over'}, room=room)

                emit('message1', {'msg': "game_number: " + str(game_number)}, room=room)

                results1 = Votes.query.filter_by(room=room, game_num=game_number, vote=1).count()
                results2 = Votes.query.filter_by(room=room, game_num=game_number, vote=2).count()

                result = 0

                if (room, cpu_number[room]) not in machine_game:
                    machine_game[(room, cpu_number[room])] = []
                if (room, cpu_number[room]) not in machine_scores:
                    machine_scores[(room, cpu_number[room])] = [0, 0]

                if results1 == 1:
                    result = 1
                elif results2 == 1:
                    result = 2
                else:
                    result = random.choice([1,2])

                machine_game[(room, cpu_number[room])].append(result)

                s = score(cpu_number[room], result, room)

                m_score = s[0]
                player_score = s[1]

                machine_scores[(room, cpu_number[room])][0] += m_score
                machine_scores[(room, cpu_number[room])][1] += player_score

                emit('vote_finished1', {'m_score': machine_scores[(room, cpu_number[room])][0], 'player_score': machine_scores[(room, cpu_number[room])][1]}, room=room)
                machine_game_ended = False
                #timer_restart = True
                game_number += 1
                timer_restart = True
                if not gamePause:
                    timer({'seconds': 10})


@app.route('/pvp', methods=['GET', 'POST'])
def pvp():
    if (request.method == 'POST'):
        username = request.form['username']
        room = request.form['room']
        # Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('pvp.html', session=session)
    else:
        if (session.get('username') is not None):
            return render_template('pvp.html', session=session)
        else:
            return redirect(url_for('index'))

pvpStarts = dict()
player1 = dict()
player2 = dict()


@socketio.on('join2', namespace='/pvp')
def join2(message):
    room = session.get('room')
    join_room(room)

    if room not in numClients:
        numClients[room] = 1
    else:
        numClients[room] += 1

    emit('status1', {'msg':  session.get('username') + ' has entered the room.'}, room=room)

    emit('message2', {'msg': 'There are currently ' + str(numClients[room]) + ' users in this room.'}, room=room)


####        VARIABLES FOR PVP       ####
player_timer_restart = False
player_game_started = False
player_game_ended = False
player_game_pause = False
player1_votes = dict()
player2_votes = dict()
player_game_users = dict() #this is the data structure to show who has voted corresponding with data structure above
player1_scores = dict()
player2_scores = dict()
player_games_per_round = 3
player_rounds = 3
player_game_nums = dict()
player_game_rounds = dict()
pvp_round_starts = dict()
player1_moves = dict()
player2_moves = dict()
first = True

####        VARIABLES FOR PVP       ####

def player_score(p1, p2):
    if p1 == 1:
        if p2 == 1:
            return(3, 3)
        else:
            return (0, 5)
    else:
        if p2 == 1:
            return (5, 0)
        else:
            return (1, 1)

@socketio.on('test_timer2', namespace='/pvp')
def player_timer(time):
    global first
    global player_game_started
    global player_game_ended
    global player_timer_restart
    global player_game_pause
    restarted = False

    room = session.get('room')
    user = session.get('username')
    if (first and user == player1[room]) or not first:

        emit('message2', {'msg': 'timer connected'}, room=room)
        emit('message2', {'msg': "timer connected with " + str(time['seconds'])}, room=room)

        t = time['seconds']
        if player_game_pause:
            player_game_pause = False
        while t > -1:
            emit('message2', {'msg': 't: ' + str(t)}, room=room)
            if player_timer_restart:
                #emit('message2', {'msg': 'player_timer_restart in if loop'}, room=room)
                t = -2
                #player_timer_restart = False
                restarted = True
            else:
                #emit('message2', {'msg': 'player_timer_restart is false'}, room=room)
                emit('test_timer_reply2', {'msg': t}, room=room)
                #emit('message1', {'msg': "time finished"}, room=room)
                socketio.sleep(1)
                t -= 1
            #player_timer_restart = False
        if t == -1 or t == 0 or t == -2:
            player_game_ended = True
            if not restarted:
                emit('player_timer_over',{},room=room)
            if t == -2:
                emit('message2', {'msg': "restarted: " + str(restarted)}, room=room)
            if restarted and not player_game_pause:
                emit('message2', {'msg': "timer is over with t = " + str(t)}, room=room)
                player_timer_restart = False
                player_timer({'seconds': 11})

    first = False

    if player_game_pause:
        emit('message2', {'msg': "we are in the middle of a round of games"}, room=room)





@socketio.on('start2', namespace='/pvp')
def start2(data):
    global player_game_pause
    if not player_game_pause:
        global first
        user = session.get('username')
        room = session.get('room')
        emit('message2', {'msg': 'start received with no pause'}, room=room)

        if room not in pvpStarts:
            pvpStarts[room] = [user]
        else:
            if user not in pvpStarts[room]:
                pvpStarts[room].append(user)

        if len(pvpStarts[room]) == 2:
            emit('message2', {'msg': "gameo starto"}, room=room)
            player1[room] = pvpStarts[room][0]
            player2[room] = pvpStarts[room][1]
            emit('message2', {'msg': "player1 is: " + player1[room]}, room=room)
            emit('message2', {'msg': "player2 is: " + player2[room]}, room=room)
            if first:
                emit('first_timer', {}, room=room)
            else:
                player_timer({'seconds': 7})
    else:
        user = session.get('username')
        room = session.get('room')
        emit('message2', {'msg': 'start received with pause'}, room=room)
        round_num = player_game_rounds[room]

        tempTup = (room, round_num)
        if tempTup not in pvp_round_starts:
            pvp_round_starts[tempTup] = [user]
        else:
            if user not in pvp_round_starts[tempTup]:
                pvp_round_starts[tempTup].append(user)
        if len(pvp_round_starts[tempTup]) > 1:
            player_game_rounds[room] += 1
            player_game_pause = False
            player_timer({'seconds': 13})

@socketio.on('handleVote2', namespace='/pvp')
def handleVote2(ballot):
    global player_timer_restart
    global player_game_nums
    global player_round_nums
    global player_game_pause

    room = session.get('room')
    vote = ballot['vote']
    user = session.get('username')

    if room not in player_game_rounds:
        player_game_rounds[room] = 1
    round_num = player_game_rounds[room]
    if room not in player_game_nums:
        player_game_nums[room] = 1
    game_num = player_game_nums[room]
    tempTup = (room, round_num, game_num)
    tempTup2 = (room, round_num)

    p1 = player1[room]
    p2 = player2[room]

    if tempTup not in player_game_users:
        player_game_users[tempTup] = []
    if game_num > round_num * player_games_per_round:
        player_game_pause = True
        player_timer_restart = True
    if vote != -1:
        if tempTup2 not in player1_moves:
            player1_moves[tempTup2] = []
        if tempTup2 not in player2_moves:
            player2_moves[tempTup2] = []

        if user not in player_game_users[tempTup]:
            player_game_users[tempTup].append(user)
            if user == p1:
                player1_votes[tempTup] = vote
                player1_moves[tempTup2].append(vote)
            else:
                player2_votes[tempTup] = vote
                player2_moves[tempTup2].append(vote)

        if len(player_game_users[tempTup]) > 1:
            temp_p1_vote = player1_votes[tempTup]
            temp_p2_vote = player2_votes[tempTup]
            s = player_score(temp_p1_vote, temp_p2_vote)

            player1_score = s[0]
            player2_score = s[1]

            if tempTup2 not in player1_scores:
                player1_scores[tempTup2] = 0
            if tempTup2 not in player2_scores:
                player2_scores[tempTup2] = 0

            player1_scores[tempTup2] += player1_score
            player2_scores[tempTup2] += player2_score

            emit('vote_results2', {'player1': player1_scores[tempTup2], 'player2': player2_scores[tempTup2]}, room=room)
            emit('message2', {'msg': "Player1: " + toString(player1_moves[tempTup2])}, room=room)
            emit('message2', {'msg': "Player2: " + toString(player2_moves[tempTup2])}, room=room)
            player_timer_restart = True
            emit('message2', {'msg': "Restart has been set to true"}, room=room)
            player_game_nums[room] += 1

            #first move tally
            if len(player1_moves[tempTup2]) == 1:
                vote = Votes(user=user, room=room,game_num=1000, vote=player1_moves[tempTup2][0])
                db.session.add(vote)
                db.session.commit()
            if len(player2_moves[tempTup2]) == 1:
                vote = Votes(user=user, room=room,game_num=1000, vote=player1_moves[tempTup2][0])
                db.session.add(vote)
                db.session.commit()

            if len(player1_moves[tempTup2]) > 1:
                length = len(player1_moves[tempTup2])
                player1_recent_move = player1_moves[tempTup2][length-1]
                player2_second_recent_move = player2_moves[tempTup2][length-2]
                if player1_recent_move == player2_second_recent_move:
                    vote = Votes(user=user, room=room, game_num=2000, vote=1)
                    db.session.add(vote)
                    db.session.commit()
                else:
                    vote = Votes(user=user, room=room, game_num=2000, vote=2)
                    db.session.add(vote)
                    db.session.commit()

            if len(player2_moves[tempTup2]) > 1:
                length = len(player2_moves[tempTup2])
                player2_recent_move = player2_moves[tempTup2][length-1]
                player1_second_recent_move = player1_moves[tempTup2][length-2]
                if player2_recent_move == player1_second_recent_move:
                    vote = Votes(user=user, room=room, game_num=2000, vote=1)
                    db.session.add(vote)
                    db.session.commit()
                else:
                    vote = Votes(user=user, room=room, game_num=2000, vote=2)
                    db.session.add(vote)
                    db.session.commit()

            cooperate_first = Votes.query.filter_by(game_num=1000, vote=1).count()
            cheat_first = Votes.query.filter_by(game_num=1000, vote=2).count()
            emit('message2', {'msg': "Cooperate has been played first " + str(cooperate_first) + " times"}, room=room)
            emit('message2', {'msg': "Cheat has been played first " + str(cheat_first) + " times"}, room=room)

            copy = Votes.query.filter_by(game_num=2000, vote=1).count()
            non_copy = Votes.query.filter_by(game_num=2000, vote=2).count()
            emit('message2', {'msg': "Players have copied  " + str(copy) + " times"}, room=room)
            emit('message2', {'msg': "Players have not copied" + str(non_copy) + " times"}, room=room)
    else:
        if tempTup2 not in player1_moves:
            player1_moves[tempTup2] = []
        if tempTup2 not in player2_moves:
            player2_moves[tempTup2] = []

        if tempTup2 not in player1_scores:
            player1_scores[tempTup2] = 0
        if tempTup2 not in player2_scores:
            player2_scores[tempTup2] = 0

        if user == player1[room]:
            if len(player_game_users[tempTup]) == 0:
                temp_p1_vote = random.choice([1,2])
                temp_p2_vote = random.choice([1,2])
                player1_moves[tempTup2].append(temp_p1_vote)
                player2_moves[tempTup2].append(temp_p2_vote)
                s = player_score(temp_p1_vote, temp_p2_vote)
                player1_scores[tempTup2] += s[0]
                player2_scores[tempTup2] += s[1]

                #give random votes to both and score
            else:
                if player_game_users[tempTup][0] == p1:
                    temp_p1_vote = player1_votes[tempTup]
                    temp_p2_vote = random.choice([1,2])
                    player1_moves[tempTup2].append(temp_p1_vote)
                    player2_moves[tempTup2].append(temp_p2_vote)
                    s = player_score(temp_p1_vote, temp_p2_vote)
                    player1_scores[tempTup2] += s[0]
                    player2_scores[tempTup2] += s[1]
                else:
                    temp_p2_vote = player2_votes[tempTup]
                    temp_p1_vote = random.choice([1,2])
                    player1_moves[tempTup2].append(temp_p1_vote)
                    player2_moves[tempTup2].append(temp_p2_vote)
                    s = player_score(temp_p1_vote, temp_p2_vote)
                    player1_scores[tempTup2] += s[0]
                    player2_scores[tempTup2] += s[1]
            player_game_nums[room] += 1

            if len(player1_moves[tempTup2]) == 1:
                vote = Votes(user=user, room=room,game_num=1000, vote=player1_moves[tempTup2][0])
                db.session.add(vote)
                db.session.commit()
            if len(player2_moves[tempTup2]) == 1:
                vote = Votes(user=user, room=room,game_num=1000, vote=player1_moves[tempTup2][0])
                db.session.add(vote)
                db.session.commit()

            if len(player1_moves[tempTup2]) > 1:
                length = len(player1_moves[tempTup2])
                player1_recent_move = player1_moves[tempTup2][length-1]
                player2_second_recent_move = player2_moves[tempTup2][length-2]
                if player1_recent_move == player2_second_recent_move:
                    vote = Votes(user=user, room=room, game_num=2000, vote=1)
                    db.session.add(vote)
                    db.session.commit()
                else:
                    vote = Votes(user=user, room=room, game_num=2000, vote=2)
                    db.session.add(vote)
                    db.session.commit()

            if len(player2_moves[tempTup2]) > 1:
                length = len(player2_moves[tempTup2])
                player2_recent_move = player2_moves[tempTup2][length-1]
                player1_second_recent_move = player1_moves[tempTup2][length-2]
                if player2_recent_move == player1_second_recent_move:
                    vote = Votes(user=user, room=room, game_num=2000, vote=1)
                    db.session.add(vote)
                    db.session.commit()
                else:
                    vote = Votes(user=user, room=room, game_num=2000, vote=2)
                    db.session.add(vote)
                    db.session.commit()

            emit('vote_results2', {'player1': player1_scores[tempTup2], 'player2': player2_scores[tempTup2]}, room=room)
            emit('message2', {'msg': "Player1: " + toString(player1_moves[tempTup2])}, room=room)
            emit('message2', {'msg': "Player2: " + toString(player2_moves[tempTup2])}, room=room)

            cooperate_first = Votes.query.filter_by(game_num=1000, vote=1).count()
            cheat_first = Votes.query.filter_by(game_num=1000, vote=2).count()
            emit('message2', {'msg': "Cooperate has been played first " + str(cooperate_first) + " times"}, room=room)
            emit('message2', {'msg': "Cheat has been played first " + str(cheat_first) + " times"}, room=room)

            copy = Votes.query.filter_by(game_num=2000, vote=1).count()
            non_copy = Votes.query.filter_by(game_num=2000, vote=2).count()
            emit('message2', {'msg': "Players have copied  " + str(copy) + " times"}, room=room)
            emit('message2', {'msg': "Players have not copied " + str(non_copy) + " times"}, room=room)

            player_timer({'seconds': 12})



@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('javascript_files', path)

if __name__ == '__main__':
    socketio.run(app, debug=True)