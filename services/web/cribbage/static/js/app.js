$(document).ready(function() {
  // Use a "/test" namespace.
  // An application can open a connection on multiple namespaces, and
  // Socket.IO will multiplex all those connections on a single
  // physical channel. If you don't care about multiple channels, you
  // can set the namespace to an empty string.
  namespace = '/game';

  // Connect to the Socket.IO server.
  // The connection URL has the following format, relative to the current page:
  //     http[s]://<domain>:<port>[/<namespace>]
  var socket = io(namespace);

  if (sessionStorage.getItem("gameName") !== null && sessionStorage.getItem("nickname") !== null) {
    $('.game').show();
    $('.lobby').hide();
    socket.emit('join', {game: sessionStorage.getItem('gameName'), nickname: sessionStorage.getItem('nickname')});
    $('#player-name').text(sessionStorage.getItem('nickname'));
    $('#game-name').text('Game: ' + sessionStorage.getItem('gameName'));
  }


  // join game
  $('form#join').submit(function (event) {
    let nickname = $('#join_nickname').val();
    let gameName = $('#join_game_name').val();
    sessionStorage.setItem('nickname', nickname);
    sessionStorage.setItem('gameName', gameName);
    socket.emit('join', {game: gameName, nickname: nickname});
    return false;
  });

  socket.on('player_join', function (msg, cb) {
    $('.game').show();
    $('.lobby').hide();

    if ($("#player-" + msg.nickname).length == 0) {
      let playerDiv = $('<div/>', {
        id: 'player-' + msg.nickname,
        class: 'scoreboard-player-area',
        html: '<h5 class="player-name">' + msg.nickname + '</h5><h6>class="player-score">' + 0 + '</h6>'
      });
      $('.scoreboard').append(playerDiv);
    }

    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  });


  // leave game
  $('form#leave').submit(function(event) {
      let nickname = sessionStorage.getItem("nickname");
      let gameName = sessionStorage.getItem("gameName");
      socket.emit('leave', {game: gameName, nickname: nickname});
      sessionStorage.removeItem('nickname');
      sessionStorage.removeItem('gameName');
      return false;
  });

  socket.on('player_leave', function (msg, cb) {
    $('.game').hide();
    $('.lobby').show();
    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' left.').html());
  });


  // send message
  $('form#send_message').submit(function(event) {
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
    socket.on('deal_card', function (msg, cb) {
      console.log('here');
      $('#playerCards').append(msg.data);
      if (cb)
        cb();
    });
    $('#action-button').click(function (event) {
      socket.emit('deal_card');
      return false;
    });

});