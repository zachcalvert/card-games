import { announcePlayerJoin } from "./actions/join.js";
import { announcePlayerLeave, clearSessionData } from "./actions/leave.js";
import { deal } from "./actions/deal.js";
import { discard, animateDiscard } from "./actions/discard.js";
import { revealCutCard } from "./actions/cut.js";
import { peg, renderCurrentTurnDisplay, clearPeggingArea, invalidCard } from "./actions/peg.js";
import { start, resetTable } from "./actions/start.js";
import { awardPoints, clearTable, displayScoredHand, revealCrib, decorateWinner } from "./actions/score.js";

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
  start(msg.dealer, msg.players);
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
  socket.emit('send_message', {game: gameName, nickname: nickname, data: $('#message-content').val()});
  $("#message-content").val("");
  return false;
});
socket.on('new_chat_message', function(msg, cb) {
  let chatMessage = $('<div/>', {
    class: 'chat-message',
    html: '<b>' + msg.nickname + '</b>' + ': ' + msg.data
  });
  $('.game-log').append(chatMessage).html();
  updateScroll();
});

socket.on('new_points_message', function(msg, cb) {
  let pointsMessage = $('<div/>', {
    class: 'points-message',
    html: msg.data
  });
  $('.game-log').append(pointsMessage).html();
  updateScroll();
});


socket.on('gif', function(msg, cb) {
  let embeddedGif = $('<iframe/>', {
    class: 'embedded-gif',
    src: msg.gif
  });
  let gifMessage = $('<div/>', {
    class: 'gif-message',
    html: '<b>' + msg.nickname + ': </b>'
  });
  gifMessage.append(embeddedGif);
  $('.game-log').append(gifMessage).html();
  updateScroll();
});

socket.on('blob', function(msg, cb) {
  let chatMessage = $('<div/>', {
    class: 'chat-message',
    html: '<b>' + msg.nickname + '</b>' + ':'
  });
  let blob = $('<div/>', {
    class: msg.blob,
    html: ''
  });
  $('.game-log').append(chatMessage).html();
  $('.game-log').append(blob).html();
  updateScroll();
});


// DEAL
socket.on('deal_hands', function (msg, cb) {
  deal(msg);
});

socket.on('discard', function (msg, cb) {
  discard(msg);
});

socket.on('deal_extra_crib_card', function (msg, cb) {
  animateDiscard(msg.card);
});

// CUT
socket.on('show_cut_card', function (msg, cb) {
  revealCutCard(msg.cut_card, msg.turn);
  renderCurrentTurnDisplay(msg.turn, 'PLAY');
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

socket.on('clear_pegging_area', function (msg, cb) {
  clearPeggingArea();
});

socket.on('reveal_crib', function (msg, cb) {
  revealCrib(msg.crib, msg.dealer);
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
});

$('#action-button').click(function (event) {
  let action = $(this).text();

  if (action === 'START') {
    socket.emit('start_game', {game: gameName});
  }

  if (action === 'DEAL') {
    socket.emit('deal_hands', {game: gameName});
  }

  if (action === 'DISCARD') {
    let card = $('img.player-card.selected').prop('id');
    socket.emit('discard', {game: gameName, player: nickname, card: card});
  }

  if (action === 'CUT') {
    socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
  }

  if (action === 'PLAY') {
    let card_played = $('img.player-card.selected').prop('id');
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

  if (action === 'CRIB') {
    socket.emit('score_crib', {game: gameName, nickname: nickname});
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

function updateScroll() {
  $(".game-log").scrollTop($(".game-log")[0].scrollHeight);
}


$(document).ready(function() {
  let welcomeMessage = "Welcome!";
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
