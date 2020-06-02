import { announcePlayerJoin } from "./join.js";
import { announcePlayerLeave, clearSessionData } from "./leave.js";
import { deal } from "./deal.js"

$(document).ready(function() {
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
    return false;
  });
  socket.on('new_chat_message', function(msg, cb) {
    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ': ' + msg.data).html());
  });


  // deal card
  socket.on('deal_hands', function (msg, cb) {
    deal();
    $('#action-button').html('Discard');
    $('#action-button').prop('disabled', true);
  });

  socket.on('receive_cut_card', function (msg, cb) {
    sessionStorage.setItem('cut', msg.cut_card);
    let cutCardImage = $('<img/>', {
      id: 'facedownCutCard',
      class: 'playerCard',
      src: '/static/img/cards/facedown.png'
    });
    $('#deck').append(cutCardImage);
  });

  socket.on('show_cut_card', function (msg, cb) {
    let cutCardImage = $('<img/>', {
      id: 'cutCard',
      class: 'playerCard',
      src: '/static/img' + msg.cut_card
    });
    $('#deck').append(cutCardImage);
    $('#facedownCutCard').remove();
  });


  // handle discard from sever
  socket.on('post_discard', function (msg, cb) {
    console.log(msg.nickname + ' just discarded');
    if (sessionStorage.getItem('nickname') === msg.nickname) {
      // remove card image
      $('#' + msg.discarded).parent().remove();

      // update session
      let card_ids = JSON.parse(sessionStorage.getItem('card_ids'));
      card_ids.splice( $.inArray(msg.discarded, card_ids), 1 );
      sessionStorage.setItem('card_ids', JSON.stringify(card_ids));
        // check if ready to play
        if (card_ids.length === 4) {
          socket.emit('ready_to_peg', {game: gameName, nickname: nickname})
        }
    } else {
      $("#" + msg.nickname).find('img').first().remove();
    }
  });

  // display cut deck action
  socket.on('show_cut_deck_action', function (msg, cb) {
      $('#action-button').html('Cut deck');
  });

  socket.on('announce_cut_deck_action', function (msg, cb) {
    socket.emit('send_message', {
      game: gameName,
      nickname: 'cribbot',
      data: 'Time to cut the deck!'
    });
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

