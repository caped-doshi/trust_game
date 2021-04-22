var gameNum = 1;
var countdownEl;
var player_scoreEl;
var machine_scoreEl;
window.onload = function() {
    countdownEl = document.getElementById("countdown");
    player_scoreEl = document.getElementById("player");
    machine_scoreEl = document.getElementById("machine")
};
var socket;
$(document).ready(function(){

    //socketio functions
    socket = io.connect('http://' + document.domain + ':' + location.port + '/vs_machine');
    socket.on('connect', function() {
        socket.emit('join1', {});
    });

    socket.on('status1', function(data) {
        $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    socket.on('message1', function(data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    socket.on('vote_results1', function(data){
        $('#chat').val($('#chat').val() + "cooperate: " + data.results1 + ' votes' + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
        $('#chat').val($('#chat').val() + "cheat: " + data.results2 + ' votes' + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
        console.log('vote results through');

        var total_votes = data.results1 + data.results2;
        var votes1 = Math.round(data.results1 / total_votes * 100);
        var votes2 = 100 - votes1;
        console.log(votes1);
        console.log(votes2);
        $('#results1').css('width', votes1 + '%');
        $('#results2').css('width', votes2 + '%');

    });

    socket.on('vote_finished1', function(data){
        $('#chat').val($('#chat').val() + "player: " + data.player_score + ' points' + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
        $('#chat').val($('#chat').val() + "machine: " + data.m_score + ' points' + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
        player_scoreEl.innerText = "player: " + data.player_score + ' points';
        machine_scoreEl.innerText = "machine: " + data.m_score + ' points';
        gameNum += 1;
        console.log('client game num');
        console.log(gameNum);
    });

    socket.on('timer_over', function(data){
        socket.emit('vote1', {});
        console.log('handle empty vote');
        socket.emit('')
    });

    socket.on('next_room1', function(data){
        socket.emit('left', {}, function() {
            socket.disconnect();
            // go back to the login page
            //window.location.href = "{{ url_for('pvp') }}";
            window.location.href = 'http://' + document.domain + ':' + location.port + '/pvp';
        });
    });

    socket.on('test_timer_reply', function(data){
        // $('#chat').val($('#chat').val() + data.msg + '\n');
        // $('#chat').scrollTop($('#chat')[0].scrollHeight);
        countdownEl.innerText = data.msg;
        console.log(data.msg);
    });

    socket.on('game_paused', function(data){
        console.log(data.msg);
    });


    //button on-click
    $('#send').click(function(e) {
        text = $('#text').val();
        $('#text').val('');
        socket.emit('text1', {msg: text});
    });
    $('#cooperate').click(function(e){
        //socket.emit('test_timer_stop', {});
        text = 'voted for cooperate.';
        socket.emit('text1', {msg: text});
        socket.emit('vote1', {gn: gameNum, vote: 1});
        console.log('hey1');
    });
    $('#cheat').click(function(e){
        //socket.emit('test_timer_start', {});
        text = 'voted for cheat';
        socket.emit('text1', {msg: text});
        socket.emit('vote1', {gn: gameNum, vote: 2});
        console.log('hey2');
    });

    $('#start').click(function(e){
        socket.emit('test_timer', {seconds: 8});
    });
    $('#next_room').click(function(e){
        window.location.href = 'http://' + document.domain + ':' + location.port + '/pvp';
    });

    function leave_room() {
        socket.emit('left1', {}, function() {
            socket.disconnect();
            // go back to the login page
            window.location.href = "{{ url_for('index') }}";
        });
    }


});
// const startingMinutes = 0.1;
// let time = startingMinutes * 60;
//
// function updateTimer() {
//     const minutes = Math.floor(time / 60);
//     let seconds = time % 60;
//
//     console.log(minutes);
//     console.log(seconds);
//
//     seconds = seconds < 10 ? '0' + seconds: seconds;
//
//     countdownEl.innerText = minutes + ":" + seconds;
//     time = time - 1;
//
//     if (time === -1){
//         stopTimer();
//     }
//
//     console.log(time);
// }
// tempTimer = setInterval(updateTimer, 1000);
//
// function stopTimer(){
//     clearInterval(tempTimer);
//     console.log("timer has been stopped");
//     resetTimer(30);
// }
//
// function resetTimer(t){
//     time = t;
//     tempTimer = setInterval(updateTimer, 1000);
// }
