import { announcePlayerJoin } from "./join.js";
import { announcePlayerLeave, clearSessionData } from "./leave.js";
import { deal } from "./deal.js";
import { discard } from "./discard.js";
import { revealCutCard, showCutDeckAction} from "./cut.js";
import { scorePlay, removeCurrentTurnDisplay, renderCurrentTurnDisplay } from "./peg.js";
import { start } from "./start.js";

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

// DEAL
socket.on('deal_hands', function (msg, cb) {
  deal(msg);
});

// DISCARD
socket.on('post_discard', function (msg, cb) {
  discard(msg);
});

// CUT
socket.on('show_cut_deck_action', function (msg, cb) {
  socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: msg.cutter + ', time to cut the deck!'});
  showCutDeckAction(msg.cutter);
});

socket.on('show_cut_card', function (msg, cb) {
  revealCutCard(msg.cut_card, msg.turn);
  renderCurrentTurnDisplay(msg.turn, 'Play');
});


// PEG
socket.on('show_card_played', function (msg, cb) {
  scorePlay(msg);
});


// SCORE
socket.on('show_score_hands_action', function (msg, cb) {
  $('#action-button').text('Score Hands');
});


$('#action-button').click(function (event) {
  let action = $(this).text();

  if (action === 'Start Game') {
    socket.emit('start_game', {game: gameName});
    socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Start your engines!'});
    return;
  }

  if (action === 'Deal') {
    socket.emit('deal_hands', {game: gameName});
    socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Time to discard!'});
    return;
  }

  if (action === 'Discard') {
    let discarded = $('li.list-group-item.selected').children()[0].id;
    socket.emit('discard', {game: gameName, nickname: nickname, discarded: discarded});
    return;
  }

  if (action === 'Cut deck') {
    socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
  }

  if (action === 'Play') {
    console.log('played card!')
    let card_played = $('li.list-group-item.selected').children()[0].id;
    socket.emit('play_card', {game: gameName, nickname: nickname, card_played: card_played});
    return;
  }

  if (action === 'Pass') {
    return;
  }
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
