import { addMessage } from "./actions/chat.js";
import { deal } from "./actions/deal.js";
import { discard } from "./actions/discard.js";
import { announcePlayerJoin } from "./actions/join.js";
import { announcePlayerLeave, clearSessionData } from "./actions/leave.js";
import { renderCurrentTurnDisplay, invalidCard } from "./actions/peg.js";
import { awardPoints, clearTable, displayScoredHand } from "./actions/score.js";
import { start, resetTable } from "./actions/start.js";
import { decorateWinner, drawGameSummary } from "./actions/win.js";

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
  sessionStorage.setItem('ws', msg.winningScore);
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
$('#send_message').submit(function(event) {
  socket.emit('send_message', {game: gameName, nickname: nickname, data: $('#message-content').val()});
  $("#message-content").val("");
  return false;
});

socket.on('new_message', function(msg, cb) {
  addMessage(msg.type, msg.nickname, msg.data);
});

socket.on('gif', function(msg, cb) {
  let embeddedGif = $('<iframe/>', {
    class: 'embedded-gif',
    src: msg.gif
  });
  addMessage('gif', msg.nickname, embeddedGif);
});

socket.on('animation', function(msg, cb) {
  let animation = $('<div/>', {
    class: msg.type,
    html: ''
  });
  $(animation).css('background-image', 'url(/static/img/' + msg.type + '/' + msg.instance + '.gif)');
  addMessage('animation', msg.nickname, animation);
});


// DEAL
socket.on('deal_hands', function (msg, cb) {
  deal(msg);
});

// PEG
socket.on('show_card_played', function (msg, cb) {
  peg(msg);
});

socket.on('invalid_card', function (msg, cb) {
  invalidCard(msg.card);
});

socket.on('send_turn', function(msg, cb) {
  renderCurrentTurnDisplay(msg.player, msg.action);
});

socket.on('display_scored_hand', function(msg, cb) {
  displayScoredHand(msg.player);
});

socket.on('clear_table', function (msg, cb) {
  clearTable(msg.next_dealer);
});

socket.on('reset_table', function (msg, cb) {
  resetTable();
});

socket.on('award_points', function (msg, cb) {
  awardPoints(msg.player, msg.amount, msg.reason);
});

socket.on('decorate_winner', function (msg, cb) {
  decorateWinner(msg.player);
  drawGameSummary(gameName);
});

$('#action-button').click(function (event) {
  let action = $(this).text();

  if (action === 'START') {
    let message = nickname + ' is setting up the game..';
    socket.emit('send_message', {game: gameName, nickname: 'cribby', data: message});
    $('#start-menu').modal();
  }

  if (action === 'DEAL') {
    socket.emit('deal_hands', {game: gameName});
  }

  if (action === 'DISCARD') {
    let card = $('img.card.selected').prop('id');
    if (card) {
      socket.emit('discard', {game: gameName, player: nickname, card: card});
    } else {
      let message = 'Psst! Click on a card to discard it ;)';
      socket.emit('send_message', {
        game: gameName, nickname: 'cribby', private: 'true', data: message});
    }
  }

  if (action === 'PLAY') {
    let card_played = $('img.card.selected').prop('id');
    if (card_played) {
      socket.emit('peg_round_action', {game: gameName, player: nickname, card_played: card_played});
    } else {
      let message = 'Psst! Click on a card to play it ;)';
      socket.emit('send_message', {
        game: gameName, nickname: 'cribby', private: 'true', data: message});
    }
  }

  if (action === 'PASS') {
    socket.emit('peg_round_action', {game: gameName, player: nickname});
  }

  if (action === 'SCORE') {
    socket.emit('score_hand', {game: gameName, nickname: nickname});
  }

  if (action === 'NEXT') {
    socket.emit('end_round', {game: gameName, nickname: nickname});
  }

  if (action === 'REMATCH') {
    socket.emit('play_again', {game: gameName, nickname: nickname});
  }

  $('#action-button').prop('disabled', true);
  return false;
});


$('#start-game').click(function (event) {
  let team_one = $('#team_one').val();
  let team_two = $('#team_two').val();
  socket.emit('start_game', {game: gameName, team_one: team_one, team_two: team_two});
  $('#start-menu').modal('hide');
});


$(document).ready(function() {
  let welcomeMessage = "Welcome, " + nickname + '!';
  socket.emit('send_message', {game: gameName, nickname: 'cribby', data: welcomeMessage, private: 'true'});
});

$(document).on('click', '.player-card', function(e) {
  $(this).siblings().each(function(index, card) {
    if ($(card).hasClass('selected')) {
      $(this).animate({'margin-top': '0px'}, 200);
    }
    $(card).removeClass('selected');
  });

  $(this).toggleClass('selected');
  if ($(this).hasClass('selected')) {
    $(this).animate({'margin-top': '-20px'}, 200);
    $('#action-button').prop('disabled', false);
  } else {
    $(this).animate({'margin-top': '0px'}, 200);
    $('#action-button').prop('disabled', true);
  }
});