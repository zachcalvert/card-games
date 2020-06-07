import { announcePlayerJoin } from "./join.js";
import { announcePlayerLeave, clearSessionData } from "./leave.js";
import { deal } from "./deal.js";
import { discard } from "./discard.js";
import { displayFacedownCutCard, displayCutCard, showCutDeckAction} from "./cut.js";
import { scorePlay, removeCurrentTurnDisplay, renderCurrentTurnDisplay } from "./peg.js";
import { start } from "./start.js";

const namespace = '/game';
const socket = io(namespace);
const gameName = sessionStorage.getItem('gameName');
const nickname = sessionStorage.getItem('nickname');

let PLAYERS = [];
let DEALER = 0;
let TURN = 0;


if (gameName !== null && nickname !== null) {
  socket.emit('join', {game: gameName, nickname: nickname});
}

socket.on('player_join', function (msg, cb) {
  announcePlayerJoin(msg);
  console.log(msg.nickname + ' just joined.');
});

socket.on('start_game', function (msg, cb) {
  console.log('starting game!')
  sessionStorage.setItem('players', JSON.stringify(msg.players));
  PLAYERS = JSON.parse(sessionStorage.getItem('players'));
  console.log('started with players: ' + PLAYERS);
  DEALER = PLAYERS[0];
  console.log('crib belongs to ' + DEALER);
  start(DEALER);
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
  const readyToPeg = discard(msg, DEALER);
  if (readyToPeg) {
    socket.emit('ready_to_peg', {game: gameName, nickname: nickname});
  }
});

// CUT
socket.on('receive_cut_card', function (msg, cb) {
  console.log('cut card is ' + msg.cut_card);
  displayFacedownCutCard(msg.cut_card);
});

socket.on('show_cut_deck_action', function (msg, cb) {
  socket.emit('send_message', {game: gameName, nickname: 'cribbot', data: 'Time to cut the deck!'});
  TURN += 1;
  let cutting_player = PLAYERS[TURN];
  if (!cutting_player) {
    TURN = 0;
    cutting_player = PLAYERS[TURN];
  }
  console.log('cutting_player ' + cutting_player);
  showCutDeckAction(cutting_player);
});

socket.on('show_cut_card', function (msg, cb) {
  displayCutCard(msg.cut_card);
  renderCurrentTurnDisplay(PLAYERS[TURN]);
});


// PEG
socket.on('show_card_played', function (msg, cb) {
  scorePlay(msg);
  rotateTurn();
});


// SCORE
socket.on('show_score_hands_action', function (msg, cb) {
  $('#action-button').text('Score Hands');
});


function rotateTurn() {
  let current_turn = PLAYERS[TURN];
  console.log('TURN is ' + TURN + ', player is ' + current_turn);
  removeCurrentTurnDisplay(current_turn);

  TURN += 1;
  let next_turn = PLAYERS[TURN];
    if (!next_turn) {
      TURN = 0;
      next_turn = PLAYERS[TURN];
    }
  console.log('TURN is now ' + TURN + ', player is now ' + next_turn);
  renderCurrentTurnDisplay(next_turn);
}


$('#action-button').click(function (event) {
  let action = $(this).text();

  if (action === 'Start Game') {
    console.log('started game')
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
    let cardId = $('li.list-group-item.selected').children()[0].id;
    socket.emit('discard', {game: gameName, nickname: nickname, dealer: DEALER, discarded: cardId});
    return;

  }

  if (action === 'Cut deck') {
    socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
  }

  if (action === 'Play') {
      let card_played = $('li.list-group-item.selected').children()[0].id;
      console.log('card is ' + card_played);

      let previously_played_cards = [];
      $("#play-pile > img").each((index, elem) => {
        previously_played_cards.unshift(elem.id);
      });
      console.log('previously_played_cards ' + previously_played_cards);
      socket.emit('play_card', {
        game: gameName,
        nickname: nickname,
        card_played: card_played,
        previously_played_cards: previously_played_cards,
        running_total: $("#play-total").html()
      });
      return
  }

  if (action === 'Pass') {
    rotateTurn();
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
