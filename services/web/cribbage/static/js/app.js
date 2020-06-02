import { showCutDeckAction, showFacedownCutCard } from './cut.js';
import { discard } from "./discard.js";
import { deal } from "./deal.js";


$(document).ready(function() {

  const namespace = '/game';
  const gameName = sessionStorage.getItem('gameName');
  const nickname = sessionStorage.getItem('nickname');

  // Connect to the Socket.IO server.
  // The connection URL has the following format, relative to the current page:
  //     http[s]://<domain>:<port>[/<namespace>]
  var socket = io(namespace);

  if (gameName !== null && nickname !== null) {
    socket.emit('join', {game: gameName, nickname: nickname});
  }

  // join game
  socket.on('player_join', function (msg, cb) {
    if ($("#" + msg.nickname).length == 0) {
      let playerDiv = $('<div/>', {
        id: msg.nickname,
        class: 'scoreboard-player-area',
        html: '<h5><span class="player-name">' + msg.nickname + '</h5span><span class="player-score">' + 0 + '</span></h5>'
      });
      $('.scoreboard').append(playerDiv);
      $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
    }
  });


  // send message
  $('form#send_message').submit(function(event) {
    console.log('here!');
    let nickname = sessionStorage.getItem("nickname");
    let gameName = sessionStorage.getItem("gameName");
    socket.emit('send_message', {
      game: gameName, nickname: nickname, data: $('#message_content').val()});
    return false;
  });
  socket.on('new_chat_message', function(msg, cb) {
    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ': ' + msg.data).html());
    if (cb)
      cb();
  });


  // deal card
  socket.on('deal_hands', function (msg, cb) {
    deal(msg);
    $('#action-button').html('Discard');
    $('#action-button').prop('disabled', true);
  });


  // handle discard from sever
  socket.on('post_discard', function (msg, cb) {
    discard(msg);
  });


  // CUT
  socket.on('announce_cut_deck_action', function (msg, cb) {
    socket.emit('send_message', {
      game: gameName,
      nickname: 'cribbot',
      data: 'Time to cut the deck!'
    });
  });

  socket.on('show_cut_deck_action', function (msg, cb) {
    showCutDeckAction();
  });

  socket.on('receive_cut_card', function (msg, cb) {
    showFacedownCutCard(msg);
  });

  socket.on('show_cut_card', function (msg, cb) {
    showCutCard(msg);
  });



  $('#action-button').click(function (event) {
    if ($(this).text() === 'Deal Hands') {
      socket.emit('deal_hands', {game: gameName});
      socket.emit('send_message', {game: sessionStorage.getItem('gameName'), nickname: 'cribbot', data: 'Time to discard!'});
    } else if ($(this).text() === 'Discard') {
      let cardId = $('li.list-group-item.active').children()[0].id;
      socket.emit('discard', {game: gameName, nickname: nickname, cardId: cardId});
    } else if ($(this).text() === 'Cut deck') {
      socket.emit('cut_deck', {game: gameName, cut_card: sessionStorage.getItem('cut')});
    }
    return false;
  });

  $('#activate-dark-mode').click(function (event) {
      $('body').attr('style', 'background-color: #000000 !important');
      $('.game').css({"background-color":"#000000", "color": "#F5F5F5"});
      $('.panel').css({"background-color": "#343a40", "border": "1px solid #8B7B8B"});
  });
  $('#activate-light-mode').click(function (event) {
      $("body").css({"background-color":"#344152"});
      $('.game').css({"background-color":"#344152", "color": "#F5F5F5"});
      $('.panel').css({"background-color": "#343a40", "border": "1px solid #404040"});
  });
});

$(document).on('click', 'li.list-group-item', function(e) {
  $(this).toggleClass('active');
  if ($(this).hasClass('active')) {
    $('#action-button').prop('disabled', false);
  } else if($(this).siblings(".active").length == 0) {
    $('#action-button').prop('disabled', true);
  }
});