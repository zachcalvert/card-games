export function announcePlayerJoin(msg) {
  if ($("#" + msg.nickname).length == 0) {
    let playerDiv = $('<div/>', {
      id: msg.nickname,
      class: 'scoreboard-player-area',
      html: '<h5><span class="player-name">' + msg.nickname + '</h5span><span class="player-score">' + 0 + '</span></h5>'
    });
    $('.scoreboard').append(playerDiv);
    $('#game-log').append('<br>' + $('<div/>').text(msg.nickname + ' joined.').html());
  }
}