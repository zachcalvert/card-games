export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length == 0) {
    let playerName = $('<h5/>', {
      class: 'player-name',
      html: msg.nickname
    });
    let playerPoints = $('<h6/>', {
      class: 'player-points',
      html: msg.points
    });
    let playerDiv = $('<div/>', {
      id: msg.nickname,
      class: 'opponent rounded panel',
      html: '<h5><span class="player-name">' + msg.nickname + '</h5><span class="player-score">' + 0 + '</span>'
    });
    $('.opponents').append(playerDiv);
    $('.playerDiv').append(playerName);
    $('.playerDiv').append(playerPoints);
    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}