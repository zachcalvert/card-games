import { announcePlayerJoin } from "./actions/join.js";
import { announcePlayerLeave, clearSessionData } from "./actions/leave.js";
import { deal } from "./actions/deal.js";
import { discard } from "./actions/discard.js";
import { revealCutCard } from "./actions/cut.js";
import { peg, renderCurrentTurnDisplay, clearPeggingArea } from "./actions/peg.js";
import { start } from "./actions/start.js";
import { awardPoints } from "./actions/score.js";

const namespace = '/game';
const socket = io(namespace);
const gameName = sessionStorage.getItem('gameName');
const nickname = sessionStorage.getItem('nickname');


if (gameName !== null && nickname !== null) {
  socket.emit('join', {game: gameName, nickname: nickname});
}

socket.on('player_join', function (msg, cb) {
  announcePlayerJoin(msg);
});

socket.on('start_game', function (msg, cb) {
  start(msg.dealer);
});


$('#leave-game').click(function (event) {
  socket.emit('leave', {game: gameName, nickname: nickname});
  clearSessionData();
});
socket.on('player_leave', function (msg, cb) {
  announcePlayerLeave(msg);
});


// send message
$('form#send_message').submit(function(event) {
  socket.emit('send_message', {game: gameName, nickname: nickname, data: $('#message_content').val()});
  $("#message_content").val("");
  return false;
});
socket.on('new_chat_message', function(msg, cb) {
  $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ': ' + msg.data).html());
});


socket.on('update_action_button', function(msg, cb) {
  $('#action-button').text(msg.action);
});

socket.on('enable_action_button', function(msg, cb) {
  renderCurrentTurnDisplay(msg.nickname, msg.action);
});


// DEAL
socket.on('deal_hands', function (msg, cb) {
  deal(msg);
});

socket.on('post_discard', function (msg, cb) {
  discard(msg);
});

// CUT
socket.on('show_cut_card', function (msg, cb) {
  revealCutCard(msg.cut_card, msg.turn);
  renderCurrentTurnDisplay(msg.turn, 'PLAY');
});

// PEG
socket.on('show_card_played', function (msg, cb) {
  peg(msg);
  renderCurrentTurnDisplay(msg.next_player, msg.next_player_action);
});

socket.on('player_passed', function (msg, cb) {
  renderCurrentTurnDisplay(msg.next_player, msg.next_player_action);
});

socket.on('clear_pegging_area', function (msg, cb) {
  clearPeggingArea();
});



socket.on('award_points', function (msg, cb) {
  awardPoints(msg.player, msg.amount, msg.reason);
});


$('#action-button').click(function (event) {
  let action = $(this).text();

  if (action === 'START') {
    socket.emit('start_game', {game: gameName});
    socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Start your engines!'});
    return;
  }

  if (action === 'DEAL') {
    socket.emit('deal_hands', {game: gameName});
    socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Time to discard!'});
    return;
  }

  if (action === 'DISCARD') {
    let discarded = $('li.list-group-item.selected').children()[0].id;
    socket.emit('discard', {game: gameName, nickname: nickname, discarded: discarded});
    return;
  }

  if (action === 'CUT') {
    socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
  }

  if (action === 'PLAY') {
    console.log('played card!')
    let card_played = $('li.list-group-item.selected').children()[0].id;
    socket.emit('play_card', {game: gameName, nickname: nickname, card_played: card_played});
    return;
  }

  if (action === 'PASS') {
    socket.emit('pass', {game: gameName, nickname: nickname});
  }
  $('#action-button').prop('disabled', true);
  return false;
});

$(document).on('click', 'li.list-group-item', function(e) {
  $(this).toggleClass('selected');
  if ($(this).hasClass('selected')) {
    $('#action-button').prop('disabled', false);
  } else if($(this).siblings(".selected").length == 0) {
    $('#action-button').prop('disabled', true);
  }
});
