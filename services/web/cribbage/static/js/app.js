import { announcePlayerJoin } from "./join.js";
import { announcePlayerLeave, clearSessionData } from "./leave.js";
import { deal } from "./deal.js";
import { discard } from "./discard.js";
import { displayFacedownCutCard, displayCutCard, showCutDeckAction} from "./cut.js";
import { moveCardFromHandToTable, removeCurrentTurnDisplay, renderCurrentTurnDisplay } from "./peg.js";
import { start } from "./start.js";


const namespace = '/game';
const socket = io(namespace);

const gameName = sessionStorage.getItem('gameName');
const nickname = sessionStorage.getItem('nickname');

let DEALER = 0;
let TURN = 0;

if (gameName !== null && nickname !== null) {
  socket.emit('join', {game: gameName, nickname: nickname});
}

socket.on('player_join', function (msg, cb) {
  announcePlayerJoin(msg);
});

// START GAME
socket.on('start_game', function (msg, cb) {
  start(msg);
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
  socket.emit('send_message', {
    game: gameName, nickname: nickname, data: $('#message_content').val()});
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
  const readyToPeg = discard(msg);
  if (readyToPeg) {
    socket.emit('ready_to_peg', {game: gameName, nickname: nickname})
  }
});


// CUT
socket.on('receive_cut_card', function (msg, cb) {
  displayFacedownCutCard(msg);
});

socket.on('show_cut_deck_action', function (msg, cb) {
  showCutDeckAction();
});

socket.on('announce_cut_deck_action', function (msg, cb) {
  socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Time to cut the deck!'});
});

socket.on('show_cut_card', function (msg, cb) {
  displayCutCard(msg);
  rotateTurn();
});



function rotateTurn() {
  console.log('rotating turn...')
  let players = JSON.parse(sessionStorage.getItem('players'));
  let current_turn = players[TURN];
  console.log('TURN is ' + TURN + ', player is ' + current_turn);
  removeCurrentTurnDisplay(current_turn);

  TURN += 1;
  let next_turn = players[TURN];
    if (!next_turn) {
      TURN = 0;
      next_turn = players[TURN];
    }
  console.log('TURN is now ' + TURN + ', player is now ' + next_turn);
  renderCurrentTurnDisplay(next_turn);
}

socket.on('show_card_played', function (msg, cb) {
  moveCardFromHandToTable(msg);
  showCardPlayScore(msg);
  rotateTurn();
});



$('#action-button').click(function (event) {
  if ($(this).text() === 'Start Game') {
    socket.emit('start_game', {game: gameName});
    socket.emit('send_message', {game: sessionStorage.getItem('gameName'), nickname: 'cribbot', data: 'Start your engines!'});
  } else if ($(this).text() === 'Deal') {
    socket.emit('deal_hands', {game: gameName});
    socket.emit('send_message', {game: sessionStorage.getItem('gameName'), nickname: 'cribbot', data: 'Time to discard!'});
  } else if ($(this).text() === 'Discard') {
    let cardId = $('li.list-group-item.selected').children()[0].id;
    socket.emit('discard', {game: gameName, nickname: nickname, cardId: cardId});
  } else if ($(this).text() === 'Cut deck') {
    socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
  } else {
    let cardId = $('li.list-group-item.selected').children()[0].id;
    console.log('cardId is ' + cardId);
    socket.emit('play_card', {game: gameName, nickname: nickname, cardId: cardId});
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
