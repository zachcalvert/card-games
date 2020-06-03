import { announcePlayerJoin } from "./join.js";
import { announcePlayerLeave, clearSessionData } from "./leave.js";
import { deal } from "./deal.js";
import { discard } from "./discard.js";
import { displayFacedownCutCard, displayCutCard, showCutDeckAction} from "./cut.js";
import { start } from "./start.js";


$(document).ready(function() {
  const namespace = '/game';
  const socket = io(namespace);

  const gameName = sessionStorage.getItem('gameName');
  const nickname = sessionStorage.getItem('nickname');

  let PLAYER_ORDER = [];

  if (gameName !== null && nickname !== null) {
    socket.emit('join', {game: gameName, nickname: nickname});
  }

  socket.on('player_join', function (msg, cb) {
    announcePlayerJoin(msg);
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


  // START GAME
  socket.on('start_game', function (msg, cb) {
    start(msg);
  });


  // DEAL
  socket.on('deal_hands', function (msg, cb) {
    deal(msg);
    $('#action-button').html('Discard').prop('disabled', true);
  });

  // CUT
  socket.on('receive_cut_card', function (msg, cb) {
    displayFacedownCutCard(msg);
  });

  socket.on('show_cut_card', function (msg, cb) {
    displayCutCard(msg);
  });

  socket.on('show_cut_deck_action', function (msg, cb) {
    showCutDeckAction();
  });

  socket.on('announce_cut_deck_action', function (msg, cb) {
    socket.emit('send_message', {
      game: gameName,
      nickname: 'cribbot',
      data: 'Time to cut the deck!'
    });
  });


  // DISCARD
  socket.on('post_discard', function (msg, cb) {
    const readyToPeg = discard(msg);
    if (readyToPeg) {
      socket.emit('ready_to_peg', {game: gameName, nickname: nickname})
    }
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
    }
    return false;
  });
});

$(document).on('click', 'li.list-group-item', function(e) {
  $(this).toggleClass('selected');
  if ($(this).hasClass('selected')) {
    $('#action-button').prop('disabled', false);
  } else if($(this).siblings(".selected").length == 0) {
    $('#action-button').prop('disabled', true);
  }
});