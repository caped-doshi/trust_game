var countdownEl;
var player1_scoreEl;
var player2_scoreEl;
window.onload = function() {
    countdownEl = document.getElementById("timer");
    player1_scoreEl = document.getElementById("player1");
    player2_scoreEl = document.getElementById("player2")
};
var socket;
$(document).ready(function() {

    socket = io.connect('http://' + document.domain + ':' + location.port + '/pvp');
    socket.on('connect', function() {
        socket.emit('join2', {});
    });

    socket.on('message2', function(data) {
        console.log(data.msg); //for now it will be to the console
    });

    socket.on('test_timer_reply2', function(data){
        console.log(data.msg);
        countdownEl.innerText = data.msg;
    });

    socket.on('vote_results2', function(data){
        player1_scoreEl.innerText = "Player1: " + data.player1;
        player2_scoreEl.innerText = "Player2: " + data.player2;
    });

    socket.on('first_timer', function(data){
        socket.emit('test_timer2', {'seconds': 14});
    });

    socket.on('player_timer_over', function(data){
        socket.emit('handleVote2', {'vote': -1});
        console.log('player timer over');
    });

    $('#cheat').click(function(e){
        socket.emit('handleVote2', {'vote': 2});
    });

    $('#cooperate').click(function(e){
        socket.emit('handleVote2', {'vote': 1});
    });

    $('#start').click(function(e){
        console.log('start pressed');
        socket.emit('start2',{});
    });
});